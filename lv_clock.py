import lvgl as lv
import machine
import fs_driver
from machine_clock import M_CLOCK
import machine
import calc
import calendar
import alarm
import digi_clock
import bw_clock
import round_clock
import settings
from utime import ticks_us, ticks_diff

i_clock = M_CLOCK()
tab_calendar = None
digi_c = None
upTimer = None
sleepTimer = None
calendar_app = None
clock_main = None
debug =None
mbox1 = None
oldminute = 0
tablist = []
        
def updateClock_UI(e): 
    global g_data, i_clock, calendar_app, debug, digi_c, oldminute, clock_main
    if i_clock.updateClock_timer():
            calendar_app.calendar.set_today_date(2000+i_clock.rtc.year(), i_clock.rtc.month(), i_clock.rtc.day())
    if i_clock.axp.isVBUSPlug() is not 0:
        current = i_clock.axp.getVbusCurrent()
    else:
        current = i_clock.axp.getBattDischargeCurrent()
    digi_c.update_UI(i_clock.clock_data.hour, i_clock.clock_data.minute, i_clock.clock_data.second,
                     i_clock.clock_data.battery, i_clock.clock_data.date, current)
    
    act = clock_main.get_tab_act()
    tab = tablist[act]
    if tab != None:
        tab.update_clock(i_clock.clock_data.hour, i_clock.clock_data.minute, i_clock.clock_data.second)
    
    freq = machine.freq() / 1000000
    bat = i_clock.axp.getBattPercentage()
    debug.set_text("CPU Clock: {} Mhz \n Battery Charge: {} \n Battery Current: {}".format( freq, bat, current))


def begin():
    
    global digi_c, upTimer, sleepTimer, i_clock, calendar_app, debug, mbox1, tab_calendar, clock_main
    i_clock.setup()

    # Create TABVIEW Main Screen
    clock_main = lv.tabview(lv.scr_act(), lv.DIR.LEFT, 0)
    clock_main.set_size(240, 240)
    clock_main.align(lv.ALIGN.CENTER, 0, 0)
    
    # Create Tabs
    tab_alarm = clock_main.add_tab("Alarm")
    tab_adj = clock_main.add_tab("Settings")
    tab_clock = clock_main.add_tab("Clock")
    tab_calendar = clock_main.add_tab("Calendar")
    tab_calc = clock_main.add_tab("Calculator")
    tab_status = clock_main.add_tab("Status")

    tab_alarm.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_clock.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_calendar.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_calc.clear_flag(lv.obj.FLAG.SCROLLABLE)
    tab_status.clear_flag(lv.obj.FLAG.SCROLLABLE)

    clock_main.set_act(2,lv.ANIM.OFF) 
        
    digi_c = digi_clock.CLOCK(tab_clock)

    digi_c.begin()
    
    i_clock.updateClock_timer()

    
    # init alarm tab
    alarm_app = alarm.ALARM_APP(tab_alarm)
    
    #init settings tab
    
    settings_app = settings.SETTINGS_APP(tab_adj)
    
    #init calc tab
    calc_app = calc.CALC_APP()
    calc_app.setup(tab_calc)
    
    calendar_app = calendar.CALENDAR_APP(tab_calendar)

    #Configure debug UI
    debug = lv.label(tab_status)
    debug.align(lv.ALIGN.TOP_MID, 0, 0)
    reset = lv.btn(tab_status)
    reset.add_event(reset_cb, lv.EVENT.CLICKED, None)
    reset.set_size(100,50)
    reset.align(lv.ALIGN.BOTTOM_MID, 0, 0)
    lbl =  lv.label(reset)
    lbl.set_text("Reset")
    
    tablist.extend([alarm_app, None,digi_c,calendar_app,calc_app,None])

    updateClock_UI(None)
    
    upTimer = lv.timer_create(updateClock_UI, 1000, None)
    sleepTimer = lv.timer_create(i_clock.sleepTimer_cb, 100, None)
    
    i_clock.display.backlightAdj(True,i_clock.op.bl_power)
    
    
   
def reset_cb(e):
    machine.reset()
     

begin()



