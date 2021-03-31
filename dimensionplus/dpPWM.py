#!/usr/bin/python3

# dpPWM.py

# This is a PWM function
#
# auther: Lanli Chen
# created: 2016/03/04
# updated: 2016/03/30
#
# © 2016 Dimension+ All Rights Reserved.
#

# -----------------------------------------------------------------------------
# import the libraries
#
import asyncio
from time import sleep
from gpiozero import PWMLED
# import itertools
# import sys
from dimensionplus import dpUtility


# -----------------------------------------------------------------------------
# define LEDFade class
#
# PWMLED(pin, active_high=True, initial_value=0, frequency=100)
#
# This library uses Broadcom (BCM) pin numbering for the GPIO pins, as opposed to physical (BOARD) numbering.
#
class LEDFade:

    pwmLed = None
    pin = 0
    frequency = 60
    start_at = 0.0
    keep_on = 0.0

    in_interval = 0.2
    out_interval = 0.1

    range_start = 0.0
    range_stop = 1.0
    range_step = 0.1

    round_decimal = 1 # round(x[, n]): x 代表最接近的整數， n 代表小數點位數即是 round_decimal
    calibration = True # 是否要做 keep_on 的時間校準


    def __init__(self, pin, frequency=60, start_at=0, keep_on=0, in_interval=0.2, out_interval=0.1, range_start=0.0, range_stop=1.0, range_step=0.1, round_decimal=1, calibration=True):

        self.__pin = pin
        self.__frequency = frequency
        self.__start_at = start_at
        self.__keep_on = keep_on

        self.__in_interval = in_interval
        self.__out_interval = out_interval

        self.__range_start = range_start
        self.__range_stop = range_stop
        self.__range_step = range_step
        self.__round_decimal = round_decimal
        self.__calibration = calibration

        if self.__calibration:
            fadeTime = self.get_fade_time()
            print('>>>>>>>>>>>> fadeTime = ',fadeTime)
            self.__keep_on -= fadeTime

        if self.__keep_on < 0:
            self.__keep_on = 0

        self.__pwmLed = PWMLED(pin=self.__pin, frequency=self.__frequency)


    @asyncio.coroutine
    def do(self):

        yield from self.start_at()
        yield from self.fade_in()
        yield from self.keep_on()
        yield from self.fade_out()


    # @asyncio.coroutine
    def get_fade_time(self):

        fadeCount=0
        for i in dpUtility.floate_range(start=self.__range_start, stop=self.__range_stop, step=self.__range_step, decimal=self.__round_decimal):
            fadeCount += 1

        fadeTime = fadeCount * (self.__in_interval + self.__out_interval)
        # yield from asyncio.sleep(0.0)

        return round(fadeTime, self.__round_decimal)


    @asyncio.coroutine
    def start_at(self):

        yield from asyncio.sleep(self.__start_at)
        print('pwmLed pin:', self.__pwmLed._pin, ' -> start_at:', self.__start_at)


    @asyncio.coroutine
    def keep_on(self):

        yield from asyncio.sleep(self.__keep_on)
        print('pwmLed pin:', self.__pwmLed._pin, ' -> keep_on:', self.__keep_on)


    # PWM the LED value from 0 to 1 (or from 1 to 0) with a 0.1(or 0.01) step
    @asyncio.coroutine
    def fade_in(self):

        print('pwmLed pin:', self.__pwmLed._pin, ' -> fade_in')
        print()

        # for i in dpUtility.floate_range_2(start=0.0, stop=1.0, step=0.01):
        # for i in dpUtility.floate_range_1(start=0.0, stop=1.0, step=0.1):
        for i in dpUtility.floate_range(start=self.__range_start, stop=self.__range_stop, step=self.__range_step, decimal=self.__round_decimal):
            # print(i)
            self.__pwmLed.value = i
            yield from asyncio.sleep(self.__in_interval)


    # PWM the LED value from 0 to 1 (or from 1 to 0) with a 0.1(or 0.01) step
    @asyncio.coroutine
    def fade_out(self):

        print('pwmLed pin:', self.__pwmLed._pin, ' -> fade_out')
        print()

        # for i in dpUtility.floate_range_2(start=1.0, stop=0.0, step=-0.01):
        # for i in dpUtility.floate_range_1(start=1.0, stop=0.0, step=-0.1):
        for i in dpUtility.floate_range(start=self.__range_stop, stop=self.__range_start, step=-self.__range_step, decimal=self.__round_decimal):
            # print(i)
            self.__pwmLed.value = i
            yield from asyncio.sleep(self.__out_interval)


# global obj for testing: create obj in loop function, may cause Segmentation fault
# led_13_Fade = LEDFade(pin=27, start_at=1.0, keep_on=4.0)
# led_16_Fade = LEDFade(pin=23, start_at=2.0, keep_on=5.0)


# -----------------------------------------------------------------------------
# define concurret_task function
#
'''
@asyncio.coroutine
def concurret_task():

    # tasks = list()
    # tasks += [led_13_Fade.do()]
    # tasks += [led_16_Fade.do()]
    # #print('total tasks = ', tasks.__len__())
    # yield from asyncio.wait(tasks)

    return True
'''

# -----------------------------------------------------------------------------
# define test function
#
'''
def main():

    print('start LEDFadeInOut_main')
    print()

    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(concurret_task())
    # loop.close()

    print()
    print('end LEDFadeInOut_main')
'''

# -----------------------------------------------------------------------------
# test
#
'''
if __name__ == '__main__':

    # while True:
    main()
'''