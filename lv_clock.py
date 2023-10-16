import lvgl as lv
import machine
import fs_driver
from mClock import M_CLOCK
import machine
import calc
import alarm
import digi_clock
import bw_clock
import round_clock
import gc
from utime import ticks_us
from utime import ticks_diff

gc.collect()
init_mem  = gc.mem_free()
now = ticks_us()

print(gc.mem_free())
i_clock = M_CLOCK()
tab_calendar = None
digi_c = None
upTimer = None
sleepTimer = None
calendar = None
debug =None
mbox1 = None
oldminute = 0
        
def updateClock_UI(e): 
    global g_data, i_clock, calendar, debug, digi_c, oldminute
    if(i_clock.updateClock_timer()):
            calendar.set_today_date(2000+i_clock.rtc.year(), i_clock.rtc.month(), i_clock.rtc.day())
    if i_clock.axp.isVBUSPlug() is not 0:
        current = i_clock.axp.getVbusCurrent()
    else:
        current = i_clock.axp.getBattDischargeCurrent()
    digi_c.update_UI(i_clock.clock_data.hour, i_clock.clock_data.minute, i_clock.clock_data.second,
                     i_clock.clock_data.battery, i_clock.clock_data.date, current)
    freq = machine.freq() / 1000000
    bat = i_clock.axp.getBattPercentage()
    debug.set_text("CPU Clock: {} Mhz \n Battery Charge: {} \n Battery Current: {}".format( freq, bat, current))


def begin():
    
    global digi_c, upTimer, sleepTimer, i_clock, calendar, debug, mbox1, tab_calendar
    then = ticks_diff(ticks_us(), now)
    print("init machine clock {}".format(then))
    i_clock.setup()
    then = ticks_diff(ticks_us(), now)
    # Create TABVIEW Main Screen
    print("init tabview {}".format(then))

    clock_main = lv.tabview(lv.scr_act(), lv.DIR.LEFT, 0)
    clock_main.set_size(240, 240)
    clock_main.align(lv.ALIGN.CENTER, 0, 0)
    clock_tab = clock_main.add_tab("Clock Main")
    clock_settings = lv.tabview(clock_tab, lv.DIR.TOP, 0)
    clock_settings.set_size(240, 240)
    clock_settings.align(lv.ALIGN.CENTER, 0, 0)
    clock_tab.clear_flag(lv.obj.FLAG.SCROLLABLE)

    tab_alarm = clock_settings.add_tab("Alarm")
    tab_clock = clock_settings.add_tab("Clock")
    tab_adj = clock_settings.add_tab("Settings")
    tab_calendar = clock_main.add_tab("Calendar")
    tab_calc = clock_main.add_tab("Calculator")
    
    tab_clock.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_calendar.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_calc.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_adj.clear_flag(lv.obj.FLAG.SCROLLABLE)

    clock_settings.set_act(1,lv.ANIM.OFF) 
    
    then = ticks_diff(ticks_us(), now)
    print("init clock face {}".format(then))
    
    digi_c = digi_clock.CLOCK(tab_clock)

    digi_c.begin()
    
    i_clock.updateClock_timer()

    # Init Calendar Tab
    then = ticks_diff(ticks_us(), now)
    print("init calendar {}".format(then))

    calendar = lv.calendar(tab_calendar)
    calendar.set_size(240, 240)
    calendar.align(lv.ALIGN.CENTER, 0, 0)
    #calendar.add_event(event_handler, lv.EVENT.ALL, None)

    calendar.set_today_date(2000+i_clock.rtc.year(), i_clock.rtc.month(), i_clock.rtc.day())
    calendar.set_showed_date(2000+i_clock.rtc.year(), i_clock.rtc.month())

    lv.calendar_header_dropdown(calendar)
     
    calendar.add_event(event_handler, lv.EVENT.LONG_PRESSED, None)

    # init alarm tab
    then = ticks_diff(ticks_us(), now)
    print("init alarm {}".format(then))
    alarm_app = alarm.ALARM_APP(tab_alarm)
    #init calc tab
    then = ticks_diff(ticks_us(), now)
    print("init calc {}".format(then))
    calc_app = calc.CALC_APP()

    calc_app.setup(tab_calc)


    #Configure debug UI
    debug = lv.label(tab_adj)
    debug.align(lv.ALIGN.TOP_MID, 0, 0)
    reset = lv.btn(tab_adj)
    reset.add_event(reset_cb, lv.EVENT.CLICKED, None)
    reset.set_size(100,50)
    reset.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    lbl =  lv.label(reset)
    lbl.set_text("Reset")


    updateClock_UI(None)
    
    upTimer = lv.timer_create(updateClock_UI, 1000, None)
    sleepTimer = lv.timer_create(i_clock.sleepTimer_cb, 100, None)
    
    i_clock.display.backlightAdj(True,i_clock.op.bl_power)
    
    gc.collect()
    print(gc.mem_free())
    print(str(init_mem - gc.mem_free()))

    
    
   
def reset_cb(e):
    machine.reset()
     
def event_cb(e):
    mbox = e.get_target_obj()
    btn = mbox.get_selected_btn()
    print("Button %s clicked" % mbox.get_btn_text(btn))

def event_handler(e):
    global mbox1, tab_calendar
    buttons = ["Apply", "Close", ""]
    mbox1 = lv.msgbox(tab_calendar, "Hello", "This is a message box with two buttons.", buttons, True)
    mbox1.add_event(event_cb, lv.EVENT.VALUE_CHANGED, None)
    mbox1.center()


begin()



