
import lvgl as lv
##### main script #####


class SETTINGS_APP:
    
    
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


        self.bg = lv.obj(screen)
        self.bg.set_size(240,240)
        self.bg.center()
        

        self.title = lv.label(self.bg)
        self.title.set_text("Settings")
        self.title.align(lv.ALIGN.TOP_MID, -10, 5)
        
        self.clock_la = lv.label(self.bg)
        self.clock_la.set_text("Adjust Time")
        self.clock_la.align(lv.ALIGN.TOP_MID, 0, 30)
    
        self.dd = lv.roller(self.bg)
        self.dd.set_options(self.hours,lv.roller.MODE.NORMAL)
        self.dd.set_size(50,60)
        self.dd.align_to(self.clock_la, lv.ALIGN.OUT_BOTTOM_LEFT, -50, 25)

        self.dd1 = lv.roller(self.bg)
        self.dd1.set_options(self.minutes,lv.roller.MODE.NORMAL)
        self.dd1.set_size(50,60)
        self.dd1.align_to(self.dd,lv.ALIGN.OUT_RIGHT_MID, 10, 0)

        self.la = lv.label(self.bg)
        self.la.set_text("Hour")
        self.la.align_to(self.dd, lv.ALIGN.OUT_TOP_MID, 0, -5)

        self.la = lv.label(self.bg)
        self.la.set_text("Minutes")
        self.la.align_to(self.dd1, lv.ALIGN.OUT_TOP_MID, 0, -5)

        self.ok_btn = lv.btn(self.bg)
        self.la = lv.label(self.ok_btn)
        self.la.set_text("OK")
        self.la.center()
        self.ok_btn.set_size(50,50)
        self.ok_btn.align_to(self.dd1,lv.ALIGN.OUT_RIGHT_MID, 10, 0)
        self.ok_btn.add_event(self.btn_event_handler, lv.EVENT.ALL, None)
        

        self.bri_la = lv.label(self.bg)
        self.bri_la.set_text("Screen Brigthness")
        self.bri_la.align(lv.ALIGN.TOP_RIGHT, -50, 140)

        self.slider = lv.slider(self.bg)
        self.slider.set_width(100)        
        self.slider.align_to(self.bri_la,lv.ALIGN.OUT_BOTTOM_LEFT, 5, 15)
        self.slider.add_event(self.slider_event_cb, lv.EVENT.VALUE_CHANGED, None)
       
        self.curr_bri_la = lv.label(self.bg)
        self.curr_bri_la.set_text("100")
        self.curr_bri_la.align_to(self.slider, lv.ALIGN.OUT_RIGHT_MID, 15, 0)

        self.out_la = lv.label(self.bg)
        self.out_la.set_text("Screen TimeOut")
        self.out_la.align_to(self.bri_la, lv.ALIGN.OUT_BOTTOM_LEFT, 0, 50)

        self.cb5 = lv.checkbox(self.bg)
        self.cb5.set_text("5")
        self.cb5.align_to(self.out_la,lv.ALIGN.OUT_BOTTOM_LEFT, 0, 15)
        self.cb5.add_event(self.chk_event_handler, lv.EVENT.VALUE_CHANGED, None)
        
        self.cb10 = lv.checkbox(self.bg)
        self.cb10.set_text("10")
        self.cb10.align_to(self.cb5, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
        self.cb10.add_event(self.chk_event_handler, lv.EVENT.VALUE_CHANGED, None)

        self.cb15 = lv.checkbox(self.bg)
        self.cb15.set_text("15")
        self.cb15.align_to(self.cb10, lv.ALIGN.OUT_RIGHT_MID, 10, 0)
        self.cb15.add_event(self.chk_event_handler, lv.EVENT.VALUE_CHANGED, None)

        self.clock = lv.label(self.bg)
        self.clock.set_text("00:00")
        self.clock.align(lv.ALIGN.TOP_RIGHT, 0, 0)

    
    def btn_event_handler(self, e):
        code = e.get_code()
        #obj = e.get_target_obj()    
        
    def chk_event_handler(self, e):
        obj = e.get_target_obj()
        time = int(obj.get_text())
        if obj.get_state() & lv.STATE.CHECKED:
            if time == 5: 
                self.cb10.clear_state(lv.STATE.CHECKED)
                self.cb15.clear_state(lv.STATE.CHECKED)
            elif time == 10:
                self.cb5.clear_state(lv.STATE.CHECKED)
                self.cb15.clear_state(lv.STATE.CHECKED)
            elif time == 15:
                self.cb10.clear_state(lv.STATE.CHECKED)
                self.cb5.clear_state(lv.STATE.CHECKED)
            print(str(time))

    def slider_event_cb(self, evt):
        self.curr_bri_la.set_text(str(self.slider.get_value()))