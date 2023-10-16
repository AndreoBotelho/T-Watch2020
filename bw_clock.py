import lvgl as lv
import fs_driver


class DateTimeUi():
    hour = None
    minute = None
    second = None
    date = None
    battery = None

class CLOCK:
    
    def __init__(self, screen):
        
        self.screen = screen
        self.style_bg = lv.style_t()
        self.style_clock = lv.style_t()
        self.style_date = lv.style_t()
        self.style_batt = lv.style_t()
        self.bg  = lv.obj(screen)
        self.g_data = DateTimeUi()
        
        
    def begin(self):
        
                
        fs_drv = lv.fs_drv_t()
        fs_driver.fs_register(fs_drv, 'S')
        
        self.style_bg.init()
        self.style_bg.set_bg_opa(lv.OPA.COVER)
        self.style_bg.set_bg_color(lv.color_white())
        
        self.bg.add_style(self.style_bg,0)
        self.bg.set_size(240,240)
        self.bg.align(lv.ALIGN.CENTER,  0, 0)
        self.bg.clear_flag(lv.obj.FLAG.SCROLLABLE)


        
        self.style_clock.init()
        self.style_clock.set_text_color(lv.palette_main(lv.PALETTE.LIGHT_BLUE))
        try:
            self.style_clock.set_text_font(lv.font_montserrat_48)
        except:
            font_portsquake_8K1z_120 = lv.font_load("S:Sportsquake-8K1z.fnt")
            self.style_clock.set_text_font(font_portsquake_8K1z_120)

        self.g_data.hour = lv.label(self.bg)
        self.g_data.hour.add_style(self.style_clock,0)
        self.g_data.hour.set_text("00:")
        self.g_data.hour.align(lv.ALIGN.TOP_LEFT, 0, 20)
        
        self.style_clock_m = lv.style_t()
        self.style_clock_m.init()
        self.style_clock_m.set_text_font(font_portsquake_8K1z_120)
        self.style_clock_m.set_text_color(lv.palette_main(lv.PALETTE.ORANGE))

        self.g_data.minute = lv.label(self.bg)
        self.g_data.minute.add_style(self.style_clock_m,0)
        self.g_data.minute.set_text("00:")
        self.g_data.minute.align(lv.ALIGN.BOTTOM_RIGHT, 0, 15)

        self.style_date.init() 
        self.style_date.set_text_font(lv.font_montserrat_16)
        self.style_date.set_radius(5)
        self.style_date.set_bg_opa(lv.OPA.COVER)
        self.style_date.set_bg_color(lv.palette_lighten(lv.PALETTE.GREY, 1))
        self.style_date.set_outline_width(2)
        self.style_date.set_outline_color(lv.color_black())
        self.style_date.set_pad_all(5)
        self.style_date.set_shadow_width(30)
        self.style_date.set_shadow_color(lv.color_black())
        self.style_date.set_text_color(lv.color_black())

        self.g_data.date = lv.label(self.bg);
        self.g_data.date.add_style(self.style_date, 0);
        self.g_data.date.set_text("01/01/2001");
        self.g_data.date.align(lv.ALIGN.TOP_RIGHT, 5, -10);

        self.style_batt.init()
        self.style_batt.set_text_color(lv.color_black())
        self.style_batt.set_text_font(lv.font_montserrat_28)

        self.g_data.battery = lv.label(self.bg)
        self.g_data.battery.add_style(self.style_batt, 0)
        self.g_data.battery.align(lv.ALIGN.TOP_LEFT, -5, -10)
        self.g_data.battery.set_text(lv.SYMBOL.BATTERY_FULL)
        
        #self.debug = lv.label(self.bg)
        #self.debug.align(lv.ALIGN.BOTTOM_LEFT, 5, 0)

        
    def update_UI(self, hour, minute, second, battery, date, current):
        #self.g_data.second.set_text(second)
        self.g_data.minute.set_text(minute)
        self.g_data.hour.set_text(hour)
        self.g_data.battery.set_text(battery)
        self.g_data.date.set_text(date)
        #self.debug.set_text("Batt Curr: \n{}".format(current))


        