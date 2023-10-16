
from ili9XXX import st7789
from ft6x36_new import ft6x36
import axp202c_new as axp202
import bma423_new as bma423
import time

##### main script #####

# init display, set backlight
display = st7789(
    mosi=19,clk=18, cs=5, dc=27, rst=-1, backlight=15, power=-1,
    width=240, height=240, rot=-3, start_y= 80, factor=4, mhz=40)
        
#init touch        
touch=ft6x36(0, 23, 32, 10000,width=240, height=240,inv_x=False, inv_y=False)
touch._write(0xA4, 0x00, True) #set interrupt mode


axp=axp202.PMU()
axp.disablePower(axp202.AXP202_LDO2)
axp.setLDO2Voltage(3000)
axp.enablePower(axp202.AXP202_LDO2)

i2c0 = axp.bus 
sensor = bma423.BMA423(i2c0)
remap_data = ([1,1,0,1,2,1])
sensor.set_remap_axes(remap_data)
sensor.accel_range=2 #2G
sensor.accel_odf = 8 #100Hz
sensor.accel_perf = 1 #perf mode
sensor.accel_enable= 1
