# Pure Python LVGL indev driver for the FocalTech FT6X36 capacitive touch IC
#
#       from ft6x36 import ft6x36 
# 
#       touch = ft6x36(sda=<pin>, scl=<pin>)
#
# If you set the size of the touchpad, you have the option to invert each 
# axis, and you'll get some extra robustness against occasional read errors
# as values outside the touchpad are quietly rejected. If you select to swap
# the axes, width and height as well as the inversions refer to the situation
# before the swap.
#
# The nice thing about this driver is that it allows access to the second
# finger, as the FT6X36 is multi-touch. (Two fingers max, with caveats on
# some boards.)
#
# The number of presses is in touch.presses, touch.points[0] and points[1]
# hold the positions. LVGL is not (yet) multi-touch, so all it sees is the
# position in points[0].
import lvgl as lv
from machine import I2C, Pin

try:
    import struct
except ImportError:
    import ustruct as struct


FT_NO_GESTRUE = const(0x00)
FT_MOVE_UP = const(0x01)
FT_MOVE_LEFT = const(0x02)
FT_MOVE_DOWN = const(0x03)
FT_MOVE_RIGHT = const(0x04)
FT_ZOOM_IN = const(0x05)
FT_ZOOM_OUT = const(0x06)


FT_EVENT_PUT_DOWN = const(0x00)
FT_EVENT_PUT_UP = const(0x00)
FT_EVENT_CONTACT = const(0x00)
FT_EVENT_NONE = const(0x00)

FT_PMODE_ACTIVE  = const(0x00)         # ~4mA
FT_PMODE_MONITOR = const(0x01)        # ~1.5mA
FT_PMODE_DEEPSLEEP =const(0x03)      # ~100uA  The reset pin must be pulled down to wake up

FT6206_DEFAULT_I2C_ADDR = 0x38

FT6XXX_REG_DATA = const(0x00)
FT6XXX_REG_NUMTOUCHES = const(0x02)
FT6XXX_REG_THRESHHOLD = const(0x80)
FT6XXX_REG_POINTRATE = const(0x88)
FT6XXX_REG_LIBH = const(0xA1)
FT6XXX_REG_LIBL = const(0xA2)
FT6XXX_REG_CHIPID = const(0xA3)
FT6XXX_REG_FIRMVERS = const(0xA6)
FT6XXX_REG_VENDID = const(0xA8)
FT6XXX_REG_RELEASE = const(0xAF)


FT5206_VENDID                    = const(0x11)
FT6206_CHIPID                    = const(0x06)
FT6236_CHIPID                    = const(0x36)
FT6236U_CHIPID                   = const(0x64)
FT5206U_CHIPID                   = const(0x64)

FT_REGISTER_MODE          = const(0x00)
FT_REGISTER_GEST          = const(0x01)
FT_REGISTER_STATUS        = const(0x02)
FT_REGISTER_TOUCH1_XH     = const(0x03)
FT_REGISTER_TOUCH1_XL     = const(0x04)
FT_REGISTER_TOUCH1_YH     = const(0x05)
FT_REGISTER_TOUCH1_YL     = const(0x06)
FT_REGISTER_THRESHHOLD    = const(0x80)
FT_REGISTER_CONTROL       = const(0x86)
FT_REGISTER_MONITORTIME   = const(0x87)
FT_REGISTER_ACTIVEPERIOD   = const(0x88)
FT_REGISTER_MONITORPERIOD   = const(0x89)

FT_REGISTER_LIB_VERSIONH  = const(0xA1)
FT_REGISTER_LIB_VERSIONL  = const(0xA2)
FT_REGISTER_INT_STATUS    = const(0xA4)
FT_REGISTER_POWER_MODE    = const(0xA5)
FT_REGISTER_VENDOR_ID     = const(0xA3)
FT_REGISTER_VENDOR1_ID    = const(0xA8)
FT_REGISTER_ERROR_STATUS  = const(0xA9)


class ft6x36:

    def __init__(self, i2c_dev=0, sda=21, scl=22, freq=400000, addr=0x38, width=-1, height=-1, 
                 inv_x=False, inv_y=False, swap_xy=False, irq= True):

        if not lv.is_initialized():
            lv.init()

        self.width, self.height = width, height
        self.inv_x, self.inv_y, self.swap_xy = inv_x, inv_y, swap_xy
        self.i2c = I2C(i2c_dev, sda=Pin(sda), scl=Pin(scl), freq=freq)
        self.addr = addr
        self.t_irq = irq #irq touch flag
        try:
            print("FT6X36 touch IC ready (fw id 0x{0:X} rel {1:d}, lib {2:X})".format( \
                int.from_bytes(self.i2c.readfrom_mem(self.addr, 0xA6, 1), "big"), \
                int.from_bytes(self.i2c.readfrom_mem(self.addr, 0xAF, 1), "big"), \
                int.from_bytes(self.i2c.readfrom_mem(self.addr, 0xA1, 2), "big") \
            ))
        except:
            print("FT6X36 touch IC not responding")
            return
        self.point = lv.point_t( {'x': 0, 'y': 0} )
        self.points = [lv.point_t( {'x': 0, 'y': 0} ), lv.point_t( {'x': 0, 'y': 0} )]
        self.state = lv.INDEV_STATE.RELEASED
                
        self.indev_drv = lv.indev_create()
        self.indev_drv.set_type(lv.INDEV_TYPE.POINTER)
        self.indev_drv.set_read_cb(self.callback)
        
                    
        self._write(FT_REGISTER_INT_STATUS, 0x01, True) #set interrupt mode
        self._write(FT_REGISTER_CONTROL, 0x01, True) #auto monitor mode

    #@micropython.native
    def callback(self, driver, data):

        def get_point(offset):
            x = (sensorbytes[offset    ] << 8 | sensorbytes[offset + 1]) & 0x0fff
            y = (sensorbytes[offset + 2] << 8 | sensorbytes[offset + 3]) & 0x0fff
            if (self.width != -1 and x >= self.width) or (self.height != -1 and y >= self.height):
                raise ValueError
            x = self.width - x - 1 if self.inv_x else x
            y = self.height - y - 1 if self.inv_y else y
            (x, y) = (y, x) if self.swap_xy else (x, y)
            return { 'x': x, 'y': y }
        
        if self.t_irq is True:
            data.point = self.points[0]
            data.state = self.state
            sensorbytes = self.i2c.readfrom_mem(self.addr, 2, 11)
            self.presses = sensorbytes[0]
            if self.presses > 2:
                return
            try:
                if self.presses:
                    self.points[0] = get_point(1)
                if self.presses == 2:
                    self.points[1] = get_point(7)
            except ValueError:
                return
            if sensorbytes[3] >> 4:
                self.points[0], self.points[1] = self.points[1], self.points[0]
            data.point = self.points[0]
            data.state = self.state = lv.INDEV_STATE.PRESSED if self.presses else lv.INDEV_STATE.RELEASED
        else:
            data.state = self.state
            self.presses = 0
            data.point = self.points[0]
            data.state = self.state = lv.INDEV_STATE.RELEASED
            
          
    @property
    def touched(self):
        """ Returns the number of touches currently detected """
        return self._read(FT6XXX_REG_NUMTOUCHES, 1)[0]

    # pylint: disable=unused-variable
    @property
    def touches(self):
        """
        Returns a list of touchpoint dicts, with 'x' and 'y' containing the
        touch coordinates, and 'id' as the touch # for multitouch tracking
        """
        touchpoints = []
        data = self._read(FT6XXX_REG_DATA, 32)

        for i in range(2):
            point_data = data[i * 6 + 3 : i * 6 + 9]
            if all([i == 0xFF for i in point_data]):
                continue
            # print([hex(i) for i in point_data])
            x, y, weight, misc = struct.unpack(">HHBB", point_data)
            # print(x, y, weight, misc)
            touch_id = y >> 12
            x &= 0xFFF
            y &= 0xFFF
            point = {"x": x, "y": y, "id": touch_id}
            touchpoints.append(point)
        return touchpoints

    def _read(self, reg, length):
        """Returns an array of 'length' bytes from the 'register'"""
        result = bytearray(length)
        self.i2c.readfrom_mem_into(self.addr, reg, result)
        return result

    def _write(self, reg, values, single = False):
        """Writes an array of 'length' bytes to the 'register'"""
        if single is False:
            values = [(v & 0xFF) for v in values]
        self.i2c.writeto_mem(self.addr,reg,bytes(values))
            
            
    def setPowerMode(self, mode):
        self._write(FT_REGISTER_POWER_MODE, mode, True)
            
            
    def getControl(self): # get control register value 0 - active, 1  - auto monitor mode(default)
        return self._read(FT_REGISTER_CONTROL, 1)

    def getGesture(self):
        val = self._read(FT_REGISTER_GEST, 1)
        if val == 0x10:
            return FT_MOVE_UP
        elif val == 0x14:
            return FT_MOVE_RIGHT
        elif val == 0x18:
            return FT_MOVE_DOWN
        elif val == 0x1C:
            return FT_MOVE_LEFT
        elif val == 0x48:
            return FT_ZOOM_IN
        elif val == 0x49:
            return FT_ZOOM_OUT
        else:
            return FT_NO_GESTRUE