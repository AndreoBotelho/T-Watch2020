import lvgl as lv
import machine
from machine import Pin,I2C,PWM
from ili9XXX import st7789
from ft6x36 import ft6x36
import axp202c_new as axp202
import pcf8563
import bma423_new as bma423
import time
import esp32
import fs_driver



class DateTime():
    hour = None
    minute = None
    second = None
    date = None

g_data = DateTime()
bl_power = 100

offcounter = 15
screenOff = True
bl = None
bg_img = None

axp=axp202.PMU()
axp.enablePower(axp202.AXP202_LDO2)
axp.enablePower(axp202.AXP202_DCDC3)
axp.clearIRQ()

i2c0 = axp.bus  # I2C(0,scl.Pin(22), sda=Pin(21))
rtc=pcf8563.PCF8563(i2c0)
rtc.enable_alarm_interrupt()
sensor = bma423.BMA423(i2c0)


issleep = 0  #// 0 = wake, 1 = sleep, 2 = sleep and disable peripherals

stpcounter = 0
targetTime = time.ticks_add(time.ticks_ms(), 1000)  #// for next 1 second timeout
oldsecond = 0
upTimer = None
sleepTimer = None
clickP = None
battery = None
        
def updateClock_timer(e):
    global g_data, rtc, oldsecond, axp, battery
    if oldsecond != rtc.seconds():
        oldsecond = rtc.seconds()
        g_data.second.set_text('{:0>2}'.format(rtc.seconds()))
        g_data.minute.set_text('{:0>2}'.format(rtc.minutes()))
        g_data.hour.set_text('{:0>2}'.format(rtc.hours()))
        bat = axp.getBattPercentage()
        if bat > 80:
             battery.set_text(lv.SYMBOL.BATTERY_FULL);
        elif bat > 50:
            battery.set_text(lv.SYMBOL.BATTERY_3)
        elif bat > 35:
            battery.set_text(lv.SYMBOL.BATTERY_2);
        elif bat > 10:
            battery.set_text(lv.SYMBOL.BATTERY_1);
        else:
            battery.set_text(lv.SYMBOL.BATTERY_EMPTY);


def backlightAdj( state = True, power = 100):
        global  bl_power, bl
        if state:
            if bl:
                bl.deinit()
            backLight = Pin(15, Pin.OUT);
            bl = PWM(backLight)
            bl.freq(500)
            bl_power = power
            bl.duty(bl_power*10) # 0 - 1023 = 0% - 100%
        else:
            bl.deinit()
    
def displayOnTimer():
    result = False
    global targetTime,offcounter
    # run clock routine each second
    if time.ticks_diff(targetTime, time.ticks_ms()) < 0:
        targetTime = time.ticks_add(time.ticks_ms(), 1000) 
        if offcounter > 0:
            offcounter = offcounter - 1

        if offcounter < 13:  #// set low power active mode
            machine.freq(80000000)
        else:  #// set mid power active mode
            machine.freq(240000000) 

        #updateClock()
        if offcounter < 5:  #// set low power active mode
           backlightAdj(True,20)
        result = True
    else:
        result = False
    
    #print(sensor.read_accel())

    
    return result

def click_Cb(pin = None):
    global offcounter
    offcounter = 15
    backlightAdj(True,80)

def setup():
    global bl, bl_power, bg_img, i2c0, sensor, battery
    # init display, set backlight
    disp = st7789(
        mosi=19, clk=18, cs=5, dc=27, rst=-1, backlight=-1, power=-1,
        width=240, height=240, rot=1, factor=4)

    #init touch        
    touch=ft6x36(0, 23, 32, 10000,width=240, height=240,inv_x=True, inv_y=True)

    #config backlight dimming
    backlightAdj(True,80)
    # BMA423 Configuration
    sensor.map_int(0,bma423.BMA423_TILT_INT | bma423.BMA423_WAKEUP_INT  )
    sensor.accel_range=2 #2G
    sensor.accel_odf = 9 #200Hz
    sensor.accel_perf = 1 #perf mode
    sensor.feature_enable('step_cntr')
    sensor.feature_enable('tilt')
    sensor.feature_enable('wakeup')
    sensor.feature_enable('any_motion',0)
    sensor.feature_enable('no_motion',0)
    sensor.accel_enable=1
    sensor.step_dedect_enabled=1

    fs_drv = lv.fs_drv_t()
    fs_driver.fs_register(fs_drv, 'S')

    bg_img = lv.img(lv.scr_act())
    try:
        bg_img.set_src('S:bg.png')
        bg_img.align(lv.ALIGN.TOP_MID, 0, 0)
    except Exception as e:
        print("BG image not found" + str(e))

    style = lv.style_t()
    style_s = lv.style_t()
    style2 = lv.style_t()
    style3 = lv.style_t()

    style.init()
    style.set_text_color(lv.color_white())
    try:
        style.set_text_font(lv.font_montserrat_34)
    except:
        font_mexellent_3d_34 = lv.font_load("S:mexcellent.3d-34.fnt")
        style.set_text_font(font_mexellent_3d_34)
    
    style_s.init()
    style_s.set_text_color(lv.color_white())
    try:
        style_s.set_text_font(lv.font_montserrat_48)
    except:
        font_mexellent_3d_72 = lv.font_load("S:mexcellent.3d.fnt")
        style_s.set_text_font(font_mexellent_3d_72)

    g_data.hour = lv.label(bg_img)
    g_data.hour.add_style(style_s,0)
    g_data.hour.set_text("00:")
    g_data.hour.align(lv.ALIGN.BOTTOM_LEFT, 10, 0)

    g_data.minute = lv.label(bg_img)
    g_data.minute.add_style(style_s,0)
    g_data.minute.set_text("00:")
    g_data.minute.align_to(g_data.hour, lv.ALIGN.OUT_RIGHT_MID,  -10, 0)
    
    g_data.second = lv.label(bg_img)
    g_data.second.add_style(style,0)
    g_data.second.set_text("00")
    g_data.second.align_to(g_data.minute, lv.ALIGN.OUT_RIGHT_TOP,  0, 5)


    style2.init()
    style2.set_text_color(lv.palette_main(lv.PALETTE.LIGHT_GREEN))
    style2.set_text_font(lv.font_montserrat_16);
    style2.set_bg_color(lv.color_black())
    style2.set_bg_opa(lv.OPA.COVER)

    g_data.date = lv.label(bg_img);
    g_data.date.add_style(style2, 0);
    g_data.date.set_text("01/01/2001");
    g_data.date.align(lv.ALIGN.TOP_RIGHT, -5, 5);

    style3.init()
    style3.set_text_color(lv.color_white())
    style3.set_text_font(lv.font_montserrat_16)

    battery = lv.label(bg_img);
    battery.add_style(style3, 0);
    battery.align(lv.ALIGN.TOP_LEFT, 5, 5);
    battery.set_text("100");
    

    g_data.hour.set_text(str(rtc.hours()));
    g_data.minute.set_text(str(rtc.minutes()));
    g_data.second.set_text(str(rtc.seconds()));
    g_data.date.set_text( str(rtc.day()) + "/" + str(rtc.month()) +"/20"+ str(rtc.year()));

    upTimer = lv.timer_create(updateClock_timer, 500, None)
    sleepTimer = lv.timer_create(sleepTimer_cb, 100, None)

    #setupBLE();
    
    installirqhandler()

def installirqhandler():
    # define the irq handlers within this method so we have
    # access to self (closure) without global variable
    global axp
    
    axp.enableIRQ(axp202.AXP202_PEK_SHORTPRESS_IRQ)
    axp.enableIRQ(axp202.AXP202_CHARGING_IRQ)
    axp.enableIRQ(axp202.AXP202_CHIP_TEMP_HIGH_IRQ )
    axp.enableIRQ(axp202.AXP202_BATT_OVER_TEMP_IRQ )
    axp.enableIRQ(axp202.AXP202_CHARGING_FINISHED_IRQ)
    axp.enableIRQ(axp202.AXP202_CHARGING_IRQ)
    axp.enableIRQ(axp202.AXP202_BATT_EXIT_ACTIVATE_IRQ )
    axp.enableIRQ(axp202.AXP202_BATT_ACTIVATE_IRQ )
    
    def tp_interrupt(pin):
        print("Got Touch Pad Interrupt on pin:",pin)

    def axp_interrupt(pin):
        irq=axp.readIRQ()
        print("Got AXP Power Mangment Interrupt on pin:",pin," irq=",irq)
        axp.clearIRQ()

    def rtc_interrupt(pin):
        print("Got RTC Interrupt on pin:",pin)

    def bma_interrupt(pin):
        print("Got BMA Accellorator Interrupt on pin:",pin)

    tpint=Pin(38,Pin.IN)
    tpint.irq(trigger=Pin.IRQ_RISING, handler=click_Cb)
    rtcint=Pin(37,Pin.IN)
    rtcint.irq(trigger=Pin.IRQ_FALLING, handler=rtc_interrupt)
    axpint=Pin(35,Pin.IN)
    axpint.irq(trigger=Pin.IRQ_FALLING, handler=axp_interrupt)
    #bmaint=Pin(39,Pin.IN)
    #bmaint.irq(trigger=Pin.IRQ_RISING, handler=bma_interrupt)


def sleepTimer_cb(e):
    
    global axp, sensor, ssleep, offcounter
        
    
    if machine.wake_reason() == machine.TIMER_WAKE: # // deep sleep after 45s idle to save power
        #axp.disablePower(axp202.AXP202_LDO2)
        #axp.disablePower(axp202.AXP202_LDO3)
        #axp.disablePower(axp202.AXP202_LDO4)
        #esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_TIMER);
        #ssleep = 2;
        #//esp_deep_sleep_start();machine.deepsleep()
        machine.lightsleep() # sleep
        
    elif machine.wake_reason() ==  machine.EXT1_WAKE:
        #esp32.wake_on_ext1((None,None), esp32.WAKEUP_ANY_HIGH)
        if ssleep > 0:
            int_status = sensor.int_status()
            print("status = "+ str(int_status[0]))
            print("sensor wake")
            if ssleep == 2:
                axp.enablePower(axp202.AXP202_LDO2)
                axp.enablePower(axp202.AXP202_LDO3)
                axp.enablePower(axp202.AXP202_LDO4)
            ssleep = 0;
            #watch->displayWakeup();
            #lv.task_handler()
            backlightAdj(True,80)
            offcounter = 15
            
    elif machine.wake_reason() == machine.EXT0_WAKE:
        esp32.wake_on_ext0(None, None)
        if ssleep > 0:
            if ssleep == 2:
                axp.enablePower(axp202.AXP202_LDO2)
                axp.enablePower(axp202.AXP202_LDO3)
                axp.enablePower(axp202.AXP202_LDO4)
            ssleep = 0
            #esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_EXT0);
            #watch->displayWakeup();
            #lv.task_handler();
            backlightAdj(True,80)
            offcounter = 15;

    displayOnTimer()
        #debugUI();

    if offcounter == 0:  #// Display shutdown counter
        #watch->displaySleep();
        backlightAdj(False,80)
        offcounter = 1
        #esp_sleep_enable_ext0_wakeup(TOUCH_INT, LOW);
        esp32.wake_on_ext0(Pin(38,Pin.IN), esp32.WAKEUP_ALL_LOW)
        esp32.wake_on_ext1(pins = (Pin(39,Pin.IN),Pin(39,Pin.IN)), level = esp32.WAKEUP_ANY_HIGH)
        ssleep = 1;
        machine.lightsleep(30000) #sleep 30s

setup()

    


