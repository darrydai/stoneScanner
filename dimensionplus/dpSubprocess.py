#!/usr/bin/python3

# dpSubprocess.py

# This is a Subprocess function
#
# auther: Lanli Chen
# created: 2016/03/04
# updated: 2016/03/30
#
# © 2017 Dimension+ All Rights Reserved.
#
# memo:
# it need sudo to run
#

# -----------------------------------------------------------------------------
# import the libraries
#
# import os
import glob
import random
import subprocess
import asyncio
from asyncio.subprocess import PIPE
from time import sleep


# -----------------------------------------------------------------------------
# define load_background_image function
#
# - image (str)
# - pre_path (str)
#
def load_background_image(image, pre_path='/home/pi/stoneScanner/data/pic/'):
    image_path = pre_path + image
    #cmd = 'sudo fbi -noverbose -d /dev/fb0 -T 2 -a ' + image_path
    cmd = 'sudo fbi -noverbose -d /dev/fb0 -T 1 ' + image_path
    subprocess.check_call(cmd, shell=True)
    #print(cmd)


# -----------------------------------------------------------------------------
# define load_background function
#
# - image_path (str)
#
# @asyncio.coroutine
# def load_background(image_path):
#     cmd = 'fbi -noverbose -d /dev/fb0 -T 1 -a ' + image_path
#     yield from asyncio.create_subprocess_shell(cmd)
#     #print(cmd)


# -----------------------------------------------------------------------------
# define LoadBackground class
#
class LoadBackground:

    # pre_path = '../data/images/' # you can use this for test in __main__
    pre_path = 'data/pic/'
    image = None
    image_path = None


    def __init__(self, image, pre_path='data/pic/'):
        self.__pre_path = pre_path
        self.__image = image
        self.__image_path = self.__pre_path + self.__image


    @asyncio.coroutine
    def do(self):
        yield from self.load_background()


    @asyncio.coroutine
    def load_background(self):
        #
        # fbi
        #
        # This program displays images using the Linux framebuffer device.
        # Supported formats: PhotoCD, jpeg, ppm, gif, tiff, xwd, bmp, png,
        # webp. It tries to use ImageMagick's convert for unknown file formats.
        #cmd = 'fbi -noverbose -d /dev/fb0 -T 2 -a ' + self.__image_path
        cmd = 'sudo fbi -noverbose -d /dev/fb0 -T 1 ' + self.__image_path
        print(cmd)
        yield from asyncio.create_subprocess_shell(cmd)


# -----------------------------------------------------------------------------
# define MediaPlay class
#
class MediaPlay:

    # pre_path = '../data/videos/' # you can use this for test in __main__
    pre_path = 'data/videos/'
    media = None
    media_path = None
    start_at = 0.0
    random = False
    filter = True


    def __init__(self, media='', start_at=0.0, random=False, filter=True, pre_path='data/videos/'):
        self.__pre_path = pre_path
        self.__media = media
        self.__media_path = self.__pre_path + self.__media
        self.__start_at = start_at
        self.__random = random
        self.__filter = filter


    @asyncio.coroutine
    def do(self):

        if self.__random:
            self.__media_path = self.get_random_media()
            print('>>>>>> random_media = ', self.__media_path)

        yield from self.play_media()


    @asyncio.coroutine
    def play_media(self):

        playSecond = yield from self.get_media_duration()
        # print('playSecond='+ str(playSecond))
        yield from asyncio.sleep(self.__start_at)

        cmd = 'omxplayer ' + self.__media_path

        #print(cmd)
        yield from asyncio.create_subprocess_shell(cmd)
        yield from asyncio.sleep(playSecond) # keep enough time for play movie


    @asyncio.coroutine
    def get_media_duration(self):

        proc = yield from asyncio.create_subprocess_shell('mediainfo --Full '+ self.__media_path +' |grep Duration', stdin=PIPE, stdout=PIPE)

        while True:
            line = yield from proc.stdout.readline()
            # print(line.decode('ascii').rstrip())
            # Duration                                 : 6131

            list = (line.decode('ascii').rstrip()).split()
            return int(int(list[2])/1000)+1


    # @asyncio.coroutine
    def get_random_media(self):

        if self.__filter:
            # media_list = glob.glob('data/videos/*.mp4') + glob.glob('data/videos/*.mov')
            media_list = glob.glob(self.__pre_path + '*.mp4') + glob.glob(self.__pre_path + '*.mov')
        else:
            # media_list = glob.glob('data/videos/*.*')
            media_list = glob.glob(self.__pre_path + '*.*')

        return random.choice(media_list)


# -----------------------------------------------------------------------------
# define playMovie function
#
# @asyncio.coroutine
# def playMovie(moviePath):
#     cmd = 'omxplayer ' + moviePath
#     yield from asyncio.create_subprocess_shell(cmd)
#     #print(cmd)


# -----------------------------------------------------------------------------
# define play_movie function
#
# - movie_name (str)
# - start (second: int, float)
#
# @asyncio.coroutine
# def play_movie(movie_name, start_at):
#
#     playSecond = yield from get_media_duration(movie_name)
#     # print('play_second='+ str(playSecond))
#     yield from asyncio.sleep(start_at)
#
#     cmd = 'omxplayer ' + movie_name
#     #print(cmd)
#     yield from asyncio.create_subprocess_shell(cmd)
#     yield from asyncio.sleep(playSecond) # keep enough time for play movie


# -----------------------------------------------------------------------------
# define get_media_duration function
#
# - media_name (str)
#
# $ mediainfo --Full ../../system/data/test.mp4 |grep Duration
#
# @asyncio.coroutine
# def get_media_duration(media_name):
#     proc = yield from asyncio.create_subprocess_shell('mediainfo --Full '+ media_name +' |grep Duration', stdin=PIPE, stdout=PIPE)
#
#     while True:
#         line = yield from proc.stdout.readline()
#         # print(line.decode('ascii').rstrip())
#         # Duration                                 : 6131
#
#         list = (line.decode('ascii').rstrip()).split()
#         return int(int(list[2])/1000)+1


# global obj for testing: create obj in loop function, may cause Segmentation fault
# loadBackground = LoadBackground(image='black.jpg', pre_path='../data/images/') # can load in loop
# mediaPlay1 = MediaPlay(media='Alice_1.mov', start_at=0, pre_path='../data/videos/')


# -----------------------------------------------------------------------------
# define concurret_task function
#
'''
@asyncio.coroutine
def concurret_task():

    tasks = list()
    # tasks += [loadBackground.do()]
    # tasks += [mediaPlay1.do()]

    #print('total tasks = ', tasks.__len__())
    yield from asyncio.wait(tasks)

    return True
'''


# -----------------------------------------------------------------------------
# define main function
#
'''
def main():

    print('hello main()')
    # loop = asyncio.get_event_loop()
    # result = loop.run_until_complete(concurret_task())
    # loop.close()
'''


# -----------------------------------------------------------------------------
# test
#
'''
if __name__  == "__main__":

    # while True:
    main()
'''