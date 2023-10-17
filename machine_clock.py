import lvgl as lv
import machine
from machine import Pin,SoftI2C,PWM,I2S
from ili9XXX import st7789
import ft6x36_2 as ft6x36
import axp202c_2 as axp202
import pcf8563
import bma423_2 as bma423
import time
import esp32
import fs_driver
import uasyncio


# ======= I2S CONFIGURATION =======
I2S_SCK_PIN = 26
I2S_WS_PIN = 25
I2S_SD_PIN = 33
I2S_ID = 0
I2S_BUFFER_LENGTH_IN_BYTES = 8000
# ======= I2S CONFIGURATION =======


# ======= ALARM FILE CONFIGURATION =======
ALARM_WAV_FILE = "/snd/short-alarm.wav"
ALARM_WAV_SAMPLE_SIZE_IN_BITS = 16
ALARM_FORMAT = I2S.STEREO
ALARM_SAMPLE_RATE_IN_HZ = 44100
# ======= AUDIO CONFIGURATION =======


class Settings():
    bl_power = 100
    screen_timer = 15
    sleep = True
    alarm_hour = 0
    alarm_minute = 0
    alarm_enable = False
    
    
class DateTime():
    hour = "00"
    minute = "00"
    second = "00"
    date = "00"
    clock = None
    battery = ""

class st7789_bl(st7789):        

    def init_pwm(self, power = 100):
        self.bl_power = power
        self.backLight = Pin(15, Pin.OUT)
        self.bl = PWM(self.backLight)
        self.bl.freq(500)

    def backlightAdj(self, state = True, power = 100):
        if state:
            try:
                getattr(self, "bl")
            except AttributeError:
                self.init_pwm(power)
            if  self.bl != None:
                self.bl_power = power
                self.bl.duty(self.bl_power*10) # 0 - 1023 = 0% - 100%
            else:
                self.init_pwm(power)
        else:
            self.bl.deinit()
            self.bl = None

clockref = None

class M_CLOCK:
    """Base Clock Object"""


    def __init__(self):
        global clockref
        clockref = self
        self.op = Settings()
        self.clock_data = DateTime()
        self.bl_power = 100
        self.offcounter = self.op.screen_timer
        self.axp=axp202.PMU()
        self.issleep = 0  #// 0 = wake, 1 = sleep, 2 = sleep and disable peripherals
        self.stpcounter = 0
        self.targetTime = time.ticks_add(time.ticks_ms(), 1000)  #// for next 1 second timeout
        self.oldsecond = 0
        self.ssleep = 0
        self.sensor = None

    def updateClock_timer(self):
        if self.oldsecond != self.rtc.seconds():
            self.oldsecond = self.rtc.seconds()
            self.clock_data.second ='{:0>2}'.format(self.rtc.seconds())
            self.clock_data.minute='{:0>2}'.format(self.rtc.minutes())
            self.clock_data.hour='{:0>2}'.format(self.rtc.hours())
            if self.rtc.hours() == 0:
                self.clock_data.date = str(self.rtc.day()) + "/" + str(self.rtc.month()) +"/20"+ str(self.rtc.year())
                return True
            bat = self.axp.getBattPercentage()
            if bat > 100:
                bat = 100
            if bat > 80:
                self.clock_data.battery=lv.SYMBOL.BATTERY_FULL
            elif bat > 50:
                self.clock_data.battery=lv.SYMBOL.BATTERY_3
            elif bat > 35:
                self.clock_data.battery=lv.SYMBOL.BATTERY_2
            elif bat > 10:
                self.clock_data.battery=lv.SYMBOL.BATTERY_1
            else:
                self.clock_data.battery=lv.SYMBOL.BATTERY_EMPTY
            
            
    def displayOnTimer(self):
        # run clock routine each second
        if time.ticks_diff(self.targetTime, time.ticks_ms()) < 0:
            self.targetTime = time.ticks_add(time.ticks_ms(), 1000) 

            if self.axp.isVBUSPlug(): 
                machine.freq(160000000)     
            else:
                if self.offcounter > 0:
                    self.offcounter = self.offcounter - 1

                if self.offcounter > self.op.screen_timer * 4 / 5 :  #// set low power active mode
                    machine.freq(240000000) 
                elif self.offcounter > self.op.screen_timer * 3 / 5 :  #// set low power active mode
                    machine.freq(160000000)
                else:#// set mid power active mode
                    machine.freq(80000000) 
            if self.offcounter < 5:  #// set low power active mode
                 self.display.backlightAdj(True,10)
            return  True
        else:
            return False
        
    def installirqhandler(self):
        # define the irq handlers within this method so we have
        # access to self (closure) without global variable
        
        self.axp.enableIRQ(axp202.AXP202_PEK_SHORTPRESS_IRQ)
        self.axp.enableIRQ(axp202.AXP202_CHARGING_IRQ)
        self.axp.enableIRQ(axp202.AXP202_CHIP_TEMP_HIGH_IRQ )
        self.axp.enableIRQ(axp202.AXP202_BATT_OVER_TEMP_IRQ )
        self.axp.enableIRQ(axp202.AXP202_CHARGING_FINISHED_IRQ)
        self.axp.enableIRQ(axp202.AXP202_CHARGING_IRQ)
        self.axp.enableIRQ(axp202.AXP202_BATT_EXIT_ACTIVATE_IRQ )
        self.axp.enableIRQ(axp202.AXP202_BATT_ACTIVATE_IRQ )
        self.axp.enableIRQ(axp202.AXP202_VBUS_REMOVED_IRQ)
        self.axp.enableIRQ(axp202.AXP202_VBUS_CONNECT_IRQ)
        
        def tp_interrupt(pin):
            self.offcounter = self.op.screen_timer
            self.touch.t_irq = pin.value() is 0
            self.display.backlightAdj(True,self.op.bl_power)

        def axp_interrupt(pin):
            irq=self.axp.readIRQ() 
            #print("Got AXP Power Mangment Interrupt on pin:",pin," irq=",irq)
            self.axp.clearIRQ()

        def rtc_interrupt(pin):
            if self.rtc.check_for_alarm_interrupt():
                self.axp.disablePower(axp202.AXP202_LDO4)
                self.axp.setLDO4Voltage(axp202.AXP202_LDO4_3300MV)
                self.axp.enablePower(axp202.AXP202_LDO4)

                self.audio_out = I2S( I2S_ID, sck=Pin(I2S_SCK_PIN), ws=Pin(I2S_WS_PIN), sd=Pin(I2S_SD_PIN),
                    mode=I2S.TX, bits=ALARM_WAV_SAMPLE_SIZE_IN_BITS, format=ALARM_FORMAT, rate=ALARM_SAMPLE_RATE_IN_HZ,
                    ibuf=I2S_BUFFER_LENGTH_IN_BYTES,
                )
                
                try:
                    self.wav = open(ALARM_WAV_FILE, "rb")
                    self.pos = self.wav.seek(44)                # advance to first byte of Data section in WAV file
                except:
                    print("alarm audio file read error")
                self.count = 3                                  #repeat counter for alarm sound
                self.audio_out.irq(self.play_alarm_wav)         # i2s_callback is called when buf is emptied
                self.audio_out.write(b'\x00' * 1024)


        def bma_interrupt(pin):
            print("Got BMA Accellorator Interrupt on pin:",pin)


        tpint=Pin(38,Pin.IN)
        tpint.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=tp_interrupt)
        rtcint=Pin(37,Pin.IN)
        rtcint.irq(trigger=Pin.IRQ_FALLING, handler=rtc_interrupt)
        axpint=Pin(35,Pin.IN)
        axpint.irq(trigger=Pin.IRQ_FALLING, handler=axp_interrupt)
        bmaint=Pin(39,Pin.IN)
        bmaint.irq(trigger=Pin.IRQ_RISING, handler=bma_interrupt)
                
    def play_alarm_wav(self, e):
            # allocate sample array
            wav_samples = bytearray(230000) #allocate 200k buffer
            wav_samples_mv = memoryview(wav_samples)
            num_read = self.wav.readinto(wav_samples_mv)
            # continuously read audio samples from the WAV file
            # and write them to an I2S DAC
            try:
                # end of WAV file?
                if num_read == 0:
                    if self.count > 0:
                        # end-of-file, advance to first byte of Data section
                        _ = self.wav.seek(44)
                        num_read = self.wav.readinto(wav_samples_mv)
                        self.count = self.count - 1
                    else:
                        # cleanup
                        self.wav.close()
                        self.audio_out.deinit()
                        self.axp.disablePower(axp202.AXP202_LDO4)
                _ = self.audio_out.write(wav_samples_mv[:num_read])
            except (KeyboardInterrupt, Exception) as e:
                print("caught exception {} {}".format(type(e).__name__, e))


    def setup(self, init_sensor = False):
        
        self.axp.setLDO2Voltage(3100)
        self.axp.enablePower(axp202.AXP202_LDO2)
        self.axp.disablePower(axp202.AXP202_LDO4)
        self.axp.clearIRQ()
        self.axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_BATT_CUR_ADC1)
        self.axp.enableADC(axp202.AXP202_ADC1, axp202.AXP202_VBUS_CUR_ADC1)
 
        self.i2c0 = self.axp.bus 
        self.rtc=pcf8563.PCF8563(self.i2c0)
        #self.rtc.enable_alarm_interrupt()
        if init_sensor:
            self.sensor = bma423.BMA423(self.i2c0)
        
        # init display, set backlight
        self.display = st7789_bl(
            mosi=19, clk=18, cs=5, dc=27, rst=-1, backlight=-1, power=-1,
            width=240, height=240, start_y= 80, rot=-3, factor=3, mhz=60)
        
        #self.display.send_cmd(0x38)
        
        #self.display.init_pwm(80)

        #init touch        
        self.touch=ft6x36.ft6x36(0, 23, 32, 10000,width=240, height=240,inv_x=False, inv_y=False)

        #config backlight dimming
        self.display.backlightAdj(True,self.op.bl_power)
        if self.sensor != None :
            # BMA423 Configuration
            remap_data = ([1,1,0,1,2,1])
            self.sensor.set_remap_axes(remap_data)
            self.sensor.accel_range=2 #2G
            self.sensor.accel_odf = 8 #100Hz
            self.sensor.accel_perf = 1 #perf mode
            self.sensor.accel_enable= 1
            self.sensor.feature_enable('any_motion',0)
            self.sensor.feature_enable('no_motion',0)
            self.sensor.feature_enable('step_cntr')
            self.sensor.feature_enable('tilt')
            self.sensor.feature_enable('wakeup')
            self.sensor.map_int(0, bma423.BMA423_TILT_INT | bma423.BMA423_WAKEUP_INT )
            self.sensor.map_int(1, bma423.BMA423_TILT_INT | bma423.BMA423_WAKEUP_INT )
            self.sensor.step_dedect_enabled=1
            
        self.clock_data.date = str(self.rtc.day()) + "/" + str(self.rtc.month()) +"/20"+ str(self.rtc.year())

        #setupBLE();
        
        self.installirqhandler()


    def sleepTimer_cb(self, e):
        
        #print("wake reason {}".format(machine.wake_reason()))
        if machine.wake_reason() == machine.TIMER_WAKE: # // deep sleep after 45s idle to save power
            self.ssleep = 2
            self.display.send_cmd(0x10) #display sleep
            self.touch.setPowerMode(ft6x36.FT_PMODE_MONITOR) #touch low power
            self.axp.disablePower(axp202.AXP202_LDO2) #disable backlight
            self.axp.disablePower(axp202.AXP202_LDO4)
            if self.sensor != None :
                self.sensor.advance_power_save=1
                self.sensor.accel_enable=0
            print("deep sleep")
            time.sleep_ms(50)
            machine.lightsleep() # sleep
            
        elif machine.wake_reason() ==  machine.EXT1_WAKE:
            #esp32.wake_on_ext1(None, None)
            if self.ssleep > 0:
                if self.ssleep > 1:
                    self.touch.setPowerMode(ft6x36.FT_PMODE_ACTIVE)
                    self.display.send_cmd(0x11)
                    self.axp.setLDO2Voltage(3100)
                    self.axp.enablePower(axp202.AXP202_LDO2)
                    if self.sensor != None :
                        self.sensor.advance_power_save=0
                        self.sensor.accel_enable=1
                self.ssleep = 0 
                #watch->displayWakeup();
                self.display.backlightAdj(True,self.op.bl_power)
                self.offcounter = self.op.screen_timer
                
        elif machine.wake_reason() == machine.EXT0_WAKE:
            if self.ssleep > 0:
                if self.ssleep > 1:
                    self.touch.setPowerMode(ft6x36.FT_PMODE_ACTIVE)
                    self.display.send_cmd(0x11)
                    self.axp.setLDO2Voltage(3100)
                    self.axp.enablePower(axp202.AXP202_LDO2)
                    if self.sensor != None :
                        self.sensor.advance_power_save=0
                        self.sensor.accel_enable=1
                self.ssleep = 0
                self.display.backlightAdj(True,self.op.bl_power)
                self.offcounter = self.op.screen_timer
                print("wake 0")

        self.displayOnTimer()

        if self.offcounter == 0 and self.op.sleep:  #// Display shutdown counter
            if self.ssleep == 0:
                #watch->displaySleep();
                self.display.backlightAdj(False,100)
                esp32.wake_on_ext0(Pin(38,Pin.IN), esp32.WAKEUP_ALL_LOW)
                esp32.wake_on_ext1(pins = (Pin(39,Pin.IN),Pin(39,Pin.IN)), level = esp32.WAKEUP_ANY_HIGH)
                self.ssleep = 1  
                machine.lightsleep(30000) #sleep 30s




