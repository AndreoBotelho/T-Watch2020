##############################################################################
#           Alarm APP
##############################################################################

import lvgl as lv
import machine_clock
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
        
        self.clock = lv.label(screen)
        self.clock.set_text("00:00")
        self.clock.align(lv.ALIGN.TOP_RIGHT, 0, 0)

        self.la = lv.label(screen)
        self.la.set_text("Hour")
        self.la.align_to(self.dd, lv.ALIGN.OUT_TOP_MID, 0, -5)

        self.la = lv.label(screen)
        self.la.set_text("Minutes")
        self.la.align_to(self.dd1, lv.ALIGN.OUT_TOP_MID, 0, -5)

    def update_clock(self, hour, minute, second):
        self.clock.set_text("{}:{}".format(hour,minute))
        
        
    def event_handler(self, e):
        code = e.get_code()
        obj = e.get_target_obj()
        if code == lv.EVENT.VALUE_CHANGED:
            txt = obj.get_text()
            if obj.get_state() & lv.STATE.CHECKED:
                if(machine_clock.clockref != None):
                    hour = self.dd.get_selected()
                    minute =  self.dd1.get_selected()   
                    machine_clock.clockref.rtc.set_daily_alarm(hours=hour, minutes=minute)
                    machine_clock.clockref.rtc.enable_alarm_interrupt()
            else:
                if(machine_clock.clockref != None):
                    machine_clock.clockref.rtc.turn_alarm_off()
                    machine_clock.clockref.rtc.disable_alarm_interrupt()


