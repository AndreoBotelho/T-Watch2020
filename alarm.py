##### startup script #####

#!/opt/bin/lv_micropython -i

import lvgl as lv
import mClock
import re

##### main script #####

class ALARM_APP(object):
    
    
    def __init__(self, screen):

        self.minutes = "\n".join([
            "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
            "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
            "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
            "41", "42", "43", "44", "45", "46", "47", "48", "49", "50",
            "51", "52", "53", "54", "55", "56", "57", "58", "59"
            ])

        self.hours = "\n".join([
            "00", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10",
            "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
            "21", "22", "23", "24"])
        
            
  
        self.dd = lv.roller(screen)
        self.dd.set_options(self.hours,lv.roller.MODE.NORMAL)
        self.dd.set_size(70,100)
        self.dd.align(lv.ALIGN.CENTER, -50, 0)

        self.dd1 = lv.roller(screen)
        self.dd1.set_options(self.minutes,lv.roller.MODE.NORMAL)
        self.dd1.set_size(70,100)
        self.dd1.align_to(self.dd,lv.ALIGN.OUT_RIGHT_MID, 30, 0)

        self.cb = lv.checkbox(screen)
        self.cb.set_text("ON")
        self.cb.align_to(self.dd1,lv.ALIGN.OUT_BOTTOM_MID, -50, 15)
        self.cb.add_event(self.event_handler, lv.EVENT.ALL, None)
        

        self.la = lv.label(screen)
        self.la.set_text("Alarm")
        self.la.align(lv.ALIGN.TOP_MID, 0, 10)

        self.la = lv.label(screen)
        self.la.set_text("Hour")
        self.la.align_to(self.dd, lv.ALIGN.OUT_TOP_MID, 0, -5)

        self.la = lv.label(screen)
        self.la.set_text("Minutes")
        self.la.align_to(self.dd1, lv.ALIGN.OUT_TOP_MID, 0, -5)
        
#         alarm = mClock.clockref.rtc.get_alarm()
#         print(alarm)
#         if alarm is not None:
#             self.cb.add_state(lv.STATE.CHECKED)
#             self.dd.set_selected(alarm[1],lv.ANIM.OFF)
#             self.dd1.set_selected(alarm[0],lv.ANIM.OFF)
#             mClock.clockref.rtc.enable_alarm_interrupt()
            

    def event_handler(self, e):
        code = e.get_code()
        obj = e.get_target_obj()
        if code == lv.EVENT.VALUE_CHANGED:
            txt = obj.get_text()
            if obj.get_state() & lv.STATE.CHECKED:
                if(mClock.clockref != None):
                    hour = self.dd.get_selected()
                    minute =  self.dd1.get_selected()   
                    mClock.clockref.rtc.set_daily_alarm(hours=hour, minutes=minute)
                    mClock.clockref.rtc.enable_alarm_interrupt()
            else:
                if(mClock.clockref != None):
                    mClock.clockref.rtc.turn_alarm_off()
                    mClock.clockref.rtc.disable_alarm_interrupt()


