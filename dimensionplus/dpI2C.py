#!/usr/bin/python3

# dpI2C.py

# This is a I2C function
#
# Using the I2C Interface
# http://www.raspberry-projects.com/pi/programming-in-python/i2c-programming-in-python/using-the-i2c-interface-2
#
# auther: Lanli Chen
# created: 2016/03/21
# updated: 2016/03/30
#
# © 2016 Dimension+ All Rights Reserved.
#

# -----------------------------------------------------------------------------
# import the libraries
#
import smbus
import asyncio
# from time import sleep


# -----------------------------------------------------------------------------
# define I2C class
#
class I2C:

    bus = None           # SMBus
    deviceI2C = 1        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
    deviceAddress = 0x04 # 7 bit address (will be left shifted to add the read write bit)
    reg = 0x00           # 打算要存取的暫存器位置
    writeValue = 1       # 送出給 arduino 的值
    byteRead = 4         # 讀取的位元數
    wait = 0.1           # 送出值給 arduino 後, 讀取回傳值前的等待秒數


    def __init__(self, deviceI2C=1, deviceAddress=0x04, reg=0x00, writeValue=1, byteRead=4, wait=0.1):

        self.__deviceI2C = deviceI2C
        self.__deviceAddress = deviceAddress
        self.__reg = reg
        self.__writeValue = writeValue
        self.__byteRead = byteRead
        self.__wait = wait
        self.__bus = smbus.SMBus(self.__deviceI2C)


    # task to write and received single data
    @asyncio.coroutine
    def single_task(self):

        yield from self.write_number()
        data = yield from self.read_number()
        print ("Arduino: Hey RPI, I received single data: ", data, "\n")


    # task to write and received multi data
    @asyncio.coroutine
    def multi_task(self):

        yield from self.write_number()
        data = yield from self.read_block_data()
        print ("Arduino: Hey RPI, I received multi data: ", data, "\n")


    # 送出值給 arduino
    @asyncio.coroutine
    def write_number(self):

        self.__bus.write_byte_data(self.__deviceAddress, self.__reg, self.__writeValue)
        print("RPI: Hi Arduino, I sent you: %d." %(self.__writeValue))
        yield from asyncio.sleep(self.__wait)


    # 從 arduino 讀取單一值
    @asyncio.coroutine
    def read_number(self):

        data = self.__bus.read_byte(self.__deviceAddress)
        # return data
        yield from data

    # 從 arduino 讀取區塊值(陣列)
    @asyncio.coroutine
    def read_block_data(self):

        data = self.__bus.read_i2c_block_data(self.__deviceAddress, self.__reg, self.__byteRead)
        # return data
        yield from data


# -----------------------------------------------------------------------------
# main
#
'''
def main():

    print('-------- start main -------- ')

    # myI2C = I2C(writeValue=1, byteRead=4)
    # tasks = [myI2C.single_task()]
    # #tasks = [myI2C.multi_task()]
    #
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.wait(tasks))
    loop.close()

    print('-------- end main --------')
'''

# -----------------------------------------------------------------------------
# test
#
'''
if __name__ == '__main__':

    main()
'''