##############################################################################
#           Calendar APP
##############################################################################

import lvgl as lv
import machine_clock

##### main script #####

class CALENDAR_APP:
    
    
    def __init__(self, screen):

        self.screen = screen
        self.calendar = lv.calendar(self.screen)
        self.calendar.set_size(240, 225)
        self.calendar.align(lv.ALIGN.CENTER, 0, 15)
        #calendar.add_event(event_handler, lv.EVENT.ALL, None)

        self.calendar.set_today_date(2000+machine_clock.clockref.rtc.year(), machine_clock.clockref.rtc.month(), machine_clock.clockref.rtc.day())
        self.calendar.set_showed_date(2000+machine_clock.clockref.rtc.year(), machine_clock.clockref.rtc.month())

        lv.calendar_header_arrow(self.calendar)
         
        self.calendar.add_event(self.event_handler, lv.EVENT.LONG_PRESSED, None)
        
        la = lv.label(self.screen)
        la.set_text("Calendar")
        la.align(lv.ALIGN.TOP_LEFT, 0, -10)
        self.clock = lv.label(self.screen)
        self.clock.set_text("00:00")
        self.clock.align(lv.ALIGN.TOP_RIGHT, 0, -10)

    def update_clock(self, hour, minute, second):
        self.clock.set_text("{}:{}".format(hour,minute))
            
    def event_handler(self, e):
        buttons = ["Add Event", "Close", ""]
        date = lv.calendar_date_t()
        self.calendar.get_pressed_date(date)
        self.mbox = lv.msgbox(self.screen, "Events {}/{}".format(date.day,date.month), "There's no saved event this date.", buttons, False)
        self.mbox.add_event(self.event_cb, lv.EVENT.VALUE_CHANGED, None)
        self.mbox.center()
        
    def event_cb(self, e):
        #btn = self.mbox.get_selected_btn()
        selected = self.mbox.get_active_btn_text()
        if selected == "Close":
            self.mbox.close()




