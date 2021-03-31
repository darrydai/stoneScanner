#!/usr/bin/python3

# dpOpenData.py

# This is a OpenData function
#
# auther: Lanli Chen
# created: 2016/09/21
# updated: 2016/09/21
#
# © 2016 Dimension+ All Rights Reserved.
#

# -----------------------------------------------------------------------------
# import the libraries
#
import smbus
import asyncio
from time import sleep
from urllib import request
try: import xml.etree.cElementTree as ET
except ImportError: import xml.etree.ElementTree as ET

from dimensionplus import dpSubprocess
import subprocess

# -----------------------------------------------------------------------------
# define CWB class (中央氣象局 Central Weather Bureau)
#
# http://opendata.cwb.gov.tw/
# http://opendata.cwb.gov.tw/opendatadoc/DIV2/A0003-001.pdf
#
class CWB:

    # data pre_defined
    opendata_cwb_url = 'http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0003-001&authorizationkey=CWB-D21AF32C-09B6-4E31-9EED-5FBDFA71B926'
    xml_file = 'opendata_cwb.xml'
    # ignore first level's child 8 tags: identifier, sender, sent, status, msgType, dataid, scope, dataset
    ignore_tag_nums = 8 # numbers for ignore tags
    normal_sleep = 0.5 # take a normal sleep
    query_interval = 10.0 # interval(second) for query next data

    # location data
    #locationLat = '' # 緯度 (座標系統採TW D67)
    #locationLon = '' # 經度 (座標系統採TW D67)

    # 臺東-> 臺東縣:臺東市, 成功-> 臺東縣:成功鎮, 大武-> 臺東縣:大武鄉, 蘭嶼-> 臺東縣:蘭嶼鄉
    locationName = '臺東'
    #locationName = '成功'
    #locationName = '大武'
    #locationName = '蘭嶼'

    #stationId = '' # 測站 ID
    obsTime = '' # 觀測時間

    # weatherElement
    #TIME = '' # 未使用
    #ELEV = '' # 高度，單位公尺
    WDIR = '' # 風向，單位度，一般風向, 0 表示無風
    WDSD = '' # 風速，單位公尺/秒
    #TEMP = '' # 溫度，單位攝氏
    #HUMD = '' # 相對濕度，單位百分比率，此處以實數0-1.0 記錄
    #PRES = '' # 測站氣壓，單位百帕
    #_24R = '' # 日累積雨量，單位毫米
    #H_FX = '' # 小時瞬間最大陣風風速，單位公尺/秒
    #H_XD = '' # 小時瞬間最大陣風風向，單位度
    #H_FXT = '' # 小時瞬間最大陣風時間，hhmm (小時分鐘)
    #H_F10 = '' # 本時最大10分鐘平均風速，單位公尺/秒
    #H_10D = '' # 本時最大10分鐘平均風向，單位度
    #H_F10T = '' # 本時最大10分鐘平均風速發生時間，hhmm (小時分鐘)

    #CITY = '' # 縣市
    #CITY_SN = '' # 縣市編號
    #TOWN = '' # 鄉鎮
    #TOWN_SN = '' # 鄉鎮編號

    # I2C
    bus = None           # SMBus
    deviceI2C = 1        # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)
    deviceAddress = 0x08 # 7 bit address (will be left shifted to add the read write bit)
    #reg = 0x00           # 打算要存取的暫存器位置
    writeValue = 225    # 送出給 arduino 的值, 0 ~ 255
    #byteRead = 4         # 讀取的位元數
    #wait = 0.1           # 送出值給 arduino 後, 讀取回傳值前的等待秒數


    # init function
    def __init__(self, locationName='臺東', xml_file='opendata_cwb.xml', query_interval=10.0):

        self.__locationName = locationName
        self.__xml_file = xml_file
        self.__query_interval = query_interval
        print('locationName = ',self.__locationName)
        print('xml_file = ',self.__xml_file)
        print('query_interval = ',self.__query_interval)


    @asyncio.coroutine
    def do(self):

        yield from self.url_retrieve()
        yield from self.parse_location()
        yield from self.i2c_write()


    # url_retrieve: get recent data & save to xml file
    @asyncio.coroutine
    def url_retrieve(self):

        request.urlretrieve(self.opendata_cwb_url, self.__xml_file)
        #yield from asyncio.sleep(self.__query_interval)
        yield from asyncio.sleep(self.normal_sleep)
        print('>>>>>>>>>>>> url_retrieve ok: ', self.__xml_file)


    # parse location value
    @asyncio.coroutine
    def parse_location(self):

        tree = ET.ElementTree(file=self.__xml_file)
        root = tree.getroot() #print(root.tag)

        # counter for record first level's child tags
        counter = 0

        for child in root:

            counter += 1

            # ignore 8 tags: identifier, sender, sent, status, msgType, dataid, scope, dataset
            # => we just need 'location' tags
            if counter > self.ignore_tag_nums: # 8
                #print('tag:', child.tag) # tag: {urn:cwb:gov:tw:cwbcommon:0.1}location
                location_node_child = child.getchildren()[2]

                # find locationName
                if location_node_child.text == self.__locationName:
                    #print('location:', location_node_child.text)

                    #self.locationLat = child.getchildren()[0].text
                    #self.locationLon = child.getchildren()[1].text
                    #self.__locationName = child.getchildren()[2].text
                    #self.stationId = child.getchildren()[3].text
                    self.obsTime = child.getchildren()[4].getchildren()[0].text
                    #self.TIME = child.getchildren()[5].getchildren()[1].getchildren()[0].text
                    #self.ELEV = child.getchildren()[6].getchildren()[1].getchildren()[0].text
                    self.WDIR = child.getchildren()[7].getchildren()[1].getchildren()[0].text
                    self.WDSD = child.getchildren()[8].getchildren()[1].getchildren()[0].text
                    #self.TEMP = child.getchildren()[9].getchildren()[1].getchildren()[0].text
                    #self.HUMD = child.getchildren()[10].getchildren()[1].getchildren()[0].text
                    #self.PRES = child.getchildren()[11].getchildren()[1].getchildren()[0].text
                    #self._24R = child.getchildren()[12].getchildren()[1].getchildren()[0].text
                    #self.H_FX = child.getchildren()[13].getchildren()[1].getchildren()[0].text
                    #self.H_XD = child.getchildren()[14].getchildren()[1].getchildren()[0].text
                    #self.H_FXT = child.getchildren()[15].getchildren()[1].getchildren()[0].text
                    #self.H_F10 = child.getchildren()[16].getchildren()[1].getchildren()[0].text
                    #self.H_10D = child.getchildren()[17].getchildren()[1].getchildren()[0].text
                    #self.H_F10T = child.getchildren()[18].getchildren()[1].getchildren()[0].text
                    #self.CITY = child.getchildren()[19].getchildren()[1].text
                    #self.CITY_SN = child.getchildren()[20].getchildren()[1].text
                    #self.TOWN = child.getchildren()[21].getchildren()[1].text
                    #self.TOWN_SN = child.getchildren()[22].getchildren()[1].text

                    #print('緯度:(TW D67)', self.locationLat)
                    #print('經度(TW D67):', self.locationLon)
                    print('位置名稱:', self.__locationName)
                    #print('測站 ID:', self.stationId)
                    print('觀測時間:', self.obsTime)
                    #print('TIME(未使用):', self.TIME)
                    #print('高度(公尺):', self.ELEV)
                    print('風向(度):', self.WDIR)
                    print('風速(單位公尺/秒):', self.WDSD)
                    # print('溫度(攝氏):', self.TEMP)
                    # print('相對濕度(百分比率):', self.HUMD)
                    # print('測站氣壓(百帕):', self.PRES)
                    # print('日累積雨量(毫米):', self._24R)

                    # print('小時瞬間最大陣風風速(公尺/秒):', self.H_FX) # maybe: -
                    # print('小時瞬間最大陣風風向(度):', self.H_XD) # maybe: -
                    # print('小時瞬間最大陣風時間(hhmm 小時分鐘):', self.H_FXT) # maybe: /
                    # print('本時最大10分鐘平均風速(公尺/秒):', self.H_F10) # maybe: -
                    # print('本時最大10分鐘平均風向(度):', self.H_10D) # maybe: -
                    # print('本時最大10分鐘平均風速發生時間(hhmm 小時分鐘):', self.H_F10T)

                    # print('縣市:', self.CITY)
                    # print('縣市編號:', self.CITY_SN)
                    # print('鄉鎮:', self.TOWN)
                    # print('鄉鎮編號:', self.TOWN_SN)

        yield from asyncio.sleep(self.normal_sleep)


    # I2C
    @asyncio.coroutine
    def i2c_write(self):

        self.bus = smbus.SMBus(self.deviceI2C)
        # #write_value = int(float(self.WDIR) * 10)
        write_value = int(float(self.WDIR))
        #
        self.bus.write_byte(self.deviceAddress, write_value)
        # #self.bus.write_byte_data(self.deviceAddress, self.reg, write_value)
        print("RPI: Hi Arduino, I sent you: %d." %(write_value))

        # load_background_image
        dpSubprocess.load_background_image(image='blue.jpg')


        yield from asyncio.sleep(self.__query_interval)
