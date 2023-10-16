##### startup script #####

#!/opt/bin/lv_micropython -i

import lvgl as lv


class DateTimeUi():
    hour = 0
    minute = 0
    second = 0
    date = None
    battery = None

#
# A clock from a meter
#

class CLOCK:
    
    def __init__(self, screen):
        self.g_data = DateTimeUi()
        self.style_date = lv.style_t()
        self.style_batt = lv.style_t()
        self.style_bg = lv.style_t()
        self.screen = screen
        self.bg  = lv.obj(self.screen)

    
    
    def begin(self):
        self.style_bg.init()
        self.style_bg.set_bg_opa(lv.OPA.COVER)
        self.style_bg.set_bg_color(lv.color_white())
        
        self.bg.add_style(self.style_bg,0)
        self.bg.set_size(240,240)
        self.bg.align(lv.ALIGN.CENTER,  0, 0)
        self.bg.clear_flag(lv.obj.FLAG.SCROLLABLE)
        
        
        self.clock_base = lv.meter(self.bg)
        self.clock_base.set_size(240, 240)
        self.clock_base.center()
        self.clock_base.clear_flag(lv.obj.FLAG.SCROLLABLE)


        self.clock_top = lv.meter(self.clock_base)
        self.clock_top.set_size(240, 240)
        self.clock_top.center()
        self.clock_top.clear_flag(lv.obj.FLAG.SCROLLABLE)
        style = lv.style_t()
        style.set_bg_opa(lv.OPA.TRANSP)
        self.clock_top.add_style(style,0)
        self.clock_base.add_style(style,0)
        # Create a scale for the minutes
        # 61 ticks in a 360 degrees range (the last and the first line overlaps)
        self.clock_base.set_scale_ticks(61, 1, 10, lv.palette_main(lv.PALETTE.GREY))
        self.clock_base.set_scale_range(0, 60, 360, 270)

        # Create another scale for the hours. It's only visual and contains only major ticks
        self.clock_top.set_scale_ticks(12, 0, 0, lv.palette_main(lv.PALETTE.GREY))  # 12 ticks
        self.clock_top.set_scale_major_ticks(1, 2, 15, lv.color_black(), 10)         # Every tick is major
        self.clock_top.set_scale_range(1, 12, 330, 300)                             # [1..12] values in an almost full circle

        # Add the hands from images
        self.indic_sec = self.clock_base.add_needle_line(4, lv.palette_main(lv.PALETTE.RED), -10)
        self.indic_min = self.clock_base.add_needle_line(4, lv.color_black(), -20)
        self.indic_hour = self.clock_top.add_needle_line(6, lv.color_black(), -40)

        self.style_date.init()
        self.style_date.set_text_font(lv.font_montserrat_16)
        self.style_date.set_radius(5)
        self.style_date.set_bg_opa(lv.OPA.COVER)
        self.style_date.set_bg_color(lv.palette_lighten(lv.PALETTE.GREY, 1))
        self.style_date.set_outline_width(2)
        self.style_date.set_outline_color(lv.color_white())
        self.style_date.set_outline_pad(3)
        self.style_date.set_shadow_width(30)
        self.style_date.set_shadow_color(lv.color_black())
        self.style_date.set_text_color(lv.color_black())

        self.g_data.date = lv.label(self.bg)
        self.g_data.date.add_style(self.style_date, 0)
        self.g_data.date.set_text("01/01/2001")
        self.g_data.date.align(lv.ALIGN.CENTER,0, 30)
        self.g_data.date.move_background()

        self.style_batt.init()
        self.style_batt.set_text_color(lv.color_black())
        self.style_batt.set_text_font(lv.font_montserrat_28)

        self.g_data.battery = lv.label(self.bg)
        self.g_data.battery.add_style(self.style_batt, 0)
        self.g_data.battery.align(lv.ALIGN.TOP_LEFT, 5, 0)
        self.g_data.battery.set_text(lv.SYMBOL.BATTERY_FULL)
        
    
    def update_UI(self, hour, minute, second, battery, date, current):
        self.g_data.second =int(second)
        self.clock_base.set_indicator_value(self.indic_sec, self.g_data.second)
        self.g_data.minute = int(minute)
        self.clock_base.set_indicator_value(self.indic_min, self.g_data.minute)
        self.g_data.hour = int(hour) % 12
        self.g_data.hour = 12 if self.g_data.hour == 0 else self.g_data.hour
        self.clock_top.set_indicator_value(self.indic_hour, self.g_data.hour)
        self.g_data.battery.set_text(battery)
        self.g_data.date.set_text(date)
        #self.debug.set_text("Batt Curr: \n{}".format(current))


