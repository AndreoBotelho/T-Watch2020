import lvgl as lv
import fs_driver
import gc


class DateTimeUi():
    hour = None
    minute = None
    second = None
    date = None
    battery = None

class CLOCK:
    
    def __init__(self, screen):
        
        self.screen = screen
        self.style_second = lv.style_t()
        self.style_clock = lv.style_t()
        self.style_date = lv.style_t()
        self.style_batt = lv.style_t()
        self.bg_img = lv.img(screen)
        self.g_data = DateTimeUi()
        
        
    def begin(self):
        
        fs_drv = lv.fs_drv_t()
        fs_driver.fs_register(fs_drv, 'S')

        try:
            self.bg_img.set_src('S:bgxp.png')
            self.bg_img.set_size(240, 240)
            self.bg_img.align(lv.ALIGN.CENTER, 0, 0)
            dsc = lv.snapshot_take(self.bg_img, lv.COLOR_FORMAT.NATIVE)
            self.bg_img.set_src(dsc)
        except Exception as e:
            print("BG image not found" + str(e))

        self.style_second.init()
        self.style_second.set_text_color(lv.color_white())
        try:
            self.style_second.set_text_font(lv.font_montserrat_34)
        except:
            font_mexellent_3d_34 = lv.font_load("S:mexcellent.3d-34.fnt")
            self.style_second.set_text_font(font_mexellent_3d_34)
        
        self.style_clock.init()
        self.style_clock.set_text_color(lv.color_white())
        try:
            self.style_clock.set_text_font(lv.font_montserrat_48)
        except:
            font_mexellent_3d_72 = lv.font_load("S:mexcellent.3d.fnt")
            self.style_clock.set_text_font(font_mexellent_3d_72)

        self.g_data.hour = lv.label(self.bg_img)
        self.g_data.hour.add_style(self.style_clock,0)
        self.g_data.hour.set_text("00:")
        self.g_data.hour.align(lv.ALIGN.BOTTOM_LEFT, 10, 5)

        self.g_data.minute = lv.label(self.bg_img)
        self.g_data.minute.add_style(self.style_clock,0)
        self.g_data.minute.set_text("00:")
        self.g_data.minute.align_to(self.g_data.hour, lv.ALIGN.OUT_RIGHT_MID,  -10, 0)
        
        self.g_data.second = lv.label(self.bg_img)
        self.g_data.second.add_style(self.style_second,0)
        self.g_data.second.set_text("00")
        self.g_data.second.align_to(self.g_data.minute, lv.ALIGN.OUT_RIGHT_BOTTOM,  0, -5)


        self.style_date.init()
        self.style_date.set_text_font(lv.font_montserrat_16)
        self.style_date.set_radius(5)
        self.style_date.set_bg_opa(lv.OPA.COVER)
        self.style_date.set_bg_color(lv.palette_lighten(lv.PALETTE.GREY, 1))
        self.style_date.set_outline_width(2)
        self.style_date.set_outline_color(lv.color_white())
        self.style_date.set_outline_pad(5)
        self.style_date.set_shadow_width(30)
        self.style_date.set_shadow_color(lv.color_black())
        self.style_date.set_text_color(lv.color_black())

        self.g_data.date = lv.label(self.bg_img);
        self.g_data.date.add_style(self.style_date, 0);
        self.g_data.date.set_text("01/01/2001");
        self.g_data.date.align(lv.ALIGN.TOP_RIGHT, -5, 5);

        self.style_batt.init() 
        self.style_batt.set_text_color(lv.color_white())
        self.style_batt.set_text_font(lv.font_montserrat_28)

        self.g_data.battery = lv.label(self.bg_img);
        self.g_data.battery.add_style(self.style_batt, 0);
        self.g_data.battery.align(lv.ALIGN.TOP_LEFT, 5, 5);
        self.g_data.battery.set_text(lv.SYMBOL.BATTERY_FULL);

        
    def update_UI(self, hour, minute, second, battery, date, current):
        self.g_data.second.set_text(second)
        self.g_data.minute.set_text(minute)
        self.g_data.hour.set_text(hour)
        self.g_data.battery.set_text(battery)
        self.g_data.date.set_text(date)

        