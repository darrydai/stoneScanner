#!/usr/bin/python3

# dpUtility.py

# This is a Utility function
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
# import itertools
# import sys
#import os
import logging
import logging.handlers


# -----------------------------------------------------------------------------
# define floate_range function
#
# Helper function to iterate over a float
# round(x[, n]): 回傳 x 的最接近數字，預設回傳整數， n 代表小數點位數(在此為: decimal)
#
# - start (float)
# - stop (float)
# - step (float)
# - decimal (int)
#
def floate_range(start, stop, step, decimal=1):

    i = start

    if (start < stop):
        while i <= stop:
            yield i
            i += step
            # For some reason, += doesn't always add an exact decimal, so we have to round the value
            i = round(i, decimal)
    else:
        while i >= stop:
            yield i
            i += step
            # For some reason, += doesn't always add an exact decimal, so we have to round the value
            i = round(i, decimal)


# -----------------------------------------------------------------------------
# define floate_range_1 function
#
# Helper function to iterate over a float
# round(x[, n]): 回傳 x 的最接近數字，預設回傳整數， n 代表小數點位數
#
# - start (float)
# - stop (float)
# - step (float)
#
# def floate_range_1(start, stop, step):
#     i = start
#
#     if (start < stop):
#         while i <= stop:
#             yield i
#             i += step
#             # For some reason, += doesn't always add an exact decimal, so we have to round the value
#             i = round(i, 1)
#     else:
#         while i >= stop:
#             yield i
#             i += step
#             # For some reason, += doesn't always add an exact decimal, so we have to round the value
#             i = round(i, 1)


# -----------------------------------------------------------------------------
# define floate_range_2 function
#
# Helper function to iterate over a float
# round(x[, n]): 回傳 x 的最接近數字，預設回傳整數， n 代表小數點位數
#
# - start (float)
# - stop (float)
# - step (float)
#
# def floate_range_2(start, stop, step):
#     i = start
#
#     if (start < stop):
#         while i <= stop:
#             yield i
#             i += step
#             # For some reason, += doesn't always add an exact decimal, so we have to round the value
#             i = round(i, 2)
#     else:
#         while i >= stop:
#             yield i
#             i += step
#             # For some reason, += doesn't always add an exact decimal, so we have to round the value
#             i = round(i, 2)


# -----------------------------------------------------------------------------
# define DPLogger function
#
# log level: debug, info, warn, error, critial
#
# - name (str)
# - pre_path (str):
#                   pre_path='../log/' for normal used;
#                   pre_path='../../log/' for test in __main__
#
# $ cat sample.log | grep ERROR
#
def DPLogger(name, pre_path='../pi/master/log/'):

    log_name = pre_path + name
    log = logging.getLogger(log_name)

    #by setting our logger to the DEBUG level (lowest level) we will include all other levels by default
    log.setLevel(logging.DEBUG)

    # Rotating File Per 0.2MB
    handler = logging.handlers.RotatingFileHandler('%s.log' %log_name, mode='a', maxBytes=(1048576*0.2), backupCount=5)
    handler.setFormatter(logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s"))

    #setup the rotating file handler to automatically increment the log file name when the max size is reached
    log.addHandler(handler)

    return log


# -----------------------------------------------------------------------------
# define test function
#
def frange_main():

    print('start frange_main')
    print()

    # for i in floate_range(start=0.0, stop=1.0, step=0.01, decimal=2):
    #     print(i)
    # for i in floate_range(start=1.0, stop=0.0, step=-0.01, decimal=3):
    #     print(i)

    for i in floate_range(start=0.0, stop=1.0, step=0.1, decimal=1):
        print(i)
    for i in floate_range(start=1.0, stop=0.0, step=-0.1, decimal=1):
        print(i)

    print()
    print('end frange_main')


# -----------------------------------------------------------------------------
# test
#
if __name__ == '__main__':

    frange_main()
    # logger = DPLogger(name='pipi')
    # logger.info('----------- logger begin -----------')
