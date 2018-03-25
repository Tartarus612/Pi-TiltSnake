#!/usr/bin/python
# This version uses the Complementary Filter output to drive the 2 servos

import smbus
import math
import time

class mpu:


    def read_all(self):
        success = False
        while (success != True):
            try:
                raw_gyro_data = self.bus.read_i2c_block_data(self.address, 0x43, 6)
                raw_accel_data = self.bus.read_i2c_block_data(self.address, 0x3b, 6)
                success = True
            except:
                time.sleep(.002)
                success = False

        gyro_scaled_x = self.twos_compliment((raw_gyro_data[0] << 8) + raw_gyro_data[1]) / self.gyro_scale
        gyro_scaled_y = self.twos_compliment((raw_gyro_data[2] << 8) + raw_gyro_data[3]) / self.gyro_scale
        gyro_scaled_z = self.twos_compliment((raw_gyro_data[4] << 8) + raw_gyro_data[5]) / self.gyro_scale

        accel_scaled_x = self.twos_compliment((raw_accel_data[0] << 8) + raw_accel_data[1]) / self.accel_scale
        accel_scaled_y = self.twos_compliment((raw_accel_data[2] << 8) + raw_accel_data[3]) / self.accel_scale
        accel_scaled_z = self.twos_compliment((raw_accel_data[4] << 8) + raw_accel_data[5]) / self.accel_scale

        return (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z)
        
    def twos_compliment(self, val):
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def get_y_rotation(self, x,z):
        radians = math.atan2(x, z)
        return -math.degrees(radians)

    def get_x_rotation(self, y,z):
        radians = math.atan2(y, z)
        return math.degrees(radians)

    
    
    def __init__(self):
            # Power management registers
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c
         
        # Chip temperature register
        self.temp = 0x41
        self.celsius = (self.temp/340.00) + 36.53
        #print("Temp = ", "%.2f" % celsius, " deg C")  # Just for fun! (Hope it's right!)

        self.gyro_scale = 131.0
        self.accel_scale = 16384.0

        self.address = 0x68  # This is the address value read via the i2cdetect command
        
        self.Tau = 0.5                     # accelerometer noise time constant (seconds)
        self.Delta_t = 0.01                # sampling time (seconds)
        self.Alpha = self.Tau/(self.Tau + self.Delta_t)   # apportionment coefficient
        # Now wake the 6050 up as it starts in sleep mode
        self.bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)
        
        (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = self.read_all()

        self.last_x = self.get_x_rotation(accel_scaled_y, accel_scaled_z)
        self.last_y = self.get_y_rotation(accel_scaled_x, accel_scaled_z)

        self.gyro_offset_x = gyro_scaled_x 
        self.gyro_offset_y = gyro_scaled_y

        self.gyro_total_x = (self.last_x) - self.gyro_offset_x
        self.gyro_total_y = (self.last_y) - self.gyro_offset_y

    #print "{0:.4f} {1:.2f} {2:.2f} {3:.2f} {4:.2f} {5:.2f} {6:.2f}".format( time.time() - now, (last_x), gyro_total_x, (last_x), (last_y), gyro_total_y, (last_y))




    def GetXY(self, secondsSinceLastCall):
        (gyro_scaled_x, gyro_scaled_y, gyro_scaled_z, accel_scaled_x, accel_scaled_y, accel_scaled_z) = self.read_all()
        
        gyro_scaled_x -= self.gyro_offset_x
        gyro_scaled_y -= self.gyro_offset_y
        
        gyro_x_delta = (gyro_scaled_x * secondsSinceLastCall)
        gyro_y_delta = (gyro_scaled_y * secondsSinceLastCall)

        self.gyro_total_x += gyro_x_delta
        self.gyro_total_y += gyro_y_delta

        rotation_x = self.get_x_rotation(accel_scaled_y, accel_scaled_z)
        rotation_y = self.get_y_rotation(accel_scaled_x, accel_scaled_z)

        self.last_x = self.Alpha * (self.last_x + gyro_x_delta) + ((1 - self.Alpha) * rotation_x)
        self.last_y = self.Alpha * (self.last_y + gyro_y_delta) + ((1 - self.Alpha) * rotation_y)

        #roll = middle+int(slope*last_x)
        #pitch = middle+int(slope*last_y)
        return self.last_x, self.last_y
        

