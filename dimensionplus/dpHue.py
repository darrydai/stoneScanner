#!/usr/bin/python3

# dpHue.py

# This is a A Philips Hue function
#
# auther: Lanli Chen
# created: 2017/01/09
# updated: 2017/01/09
#
# https://github.com/studioimaginaire/phue
#
# © 2017 Dimension+ All Rights Reserved.
#

# -----------------------------------------------------------------------------
# import the libraries
#
import asyncio
#from time import sleep
from lib.phue import Bridge
#import random


# -----------------------------------------------------------------------------
# define Hue class
#
# Find My Bridge IP Address:
# https://www.meethue.com/api/nupnp
# => [{"id":"001788fffe49ef2a","internalipaddress":"192.168.1.36"}]
#
class Hue:

    bridge = None
    bridge_ip = "192.168.1.36"
    group_name = ""
    scene_name = ""
    scene_start_at = 0.0 # second

    def __init__(self, bridge_ip = "192.168.1.36"):

        self.__bridge_ip = bridge_ip
        self.__bridge = Bridge(self.__bridge_ip)

        # If the app is not registered and the button is not pressed,
        # press the button and call connect() (this only needs to be run a single time)
        self.__bridge.connect()


    # scene_transformation
    def scene_transformation(self, scene_start_at=0, group_name="", scene_name=""):
        self.__scene_start_at = scene_start_at
        self.__group_name = group_name
        self.__scene_name = scene_name


    # do_transform
    @asyncio.coroutine
    def do_transform(self):
        yield from self.scene_start_at()
        yield from self.run_scene()


    # scene_start_at
    @asyncio.coroutine
    def scene_start_at(self):
        yield from asyncio.sleep(self.__scene_start_at)
        print('bridge_ip:', self.__bridge_ip, ' -> scene_start_at:', self.__scene_start_at)


    # run_scene
    @asyncio.coroutine
    def run_scene(self):
        self.__bridge.run_scene(group_name=self.__group_name, scene_name=self.__scene_name)
        print('bridge_ip:', self.__bridge_ip, ' -> run_scene complete')


############################################################
# local test
'''
myHue = Hue()
myHue.scene_transformation(scene_start_at=1, group_name="All", scene_name="北極極光")
#myHue.do_transform()

myHue2 = Hue()
myHue2.scene_transformation(scene_start_at=3, group_name="All", scene_name="專注精神")
#myHue2.do_transform()
'''


# -----------------------------------------------------------------------------
# define concurret_task function
#
'''
@asyncio.coroutine
def concurret_task():

    tasks = list()
    tasks += [myHue.do_transform()]
    tasks += [myHue2.do_transform()]

    print('total tasks = ', tasks.__len__())
    yield from asyncio.wait(tasks)

    return True
'''

# -----------------------------------------------------------------------------
# define test function
#
'''
def main():

    print('start Hue')
    print()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(concurret_task())
    loop.close()

    print()
    print('end Hue')
'''

# -----------------------------------------------------------------------------
# test
#
'''
if __name__ == '__main__':

    # while True:
    main()
'''