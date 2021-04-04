import sys
import RPi.GPIO as GPIO
import numpy as np
import cv2
import configparser
import skimage.exposure
import queue
import threading,trace,queue
import requests
import keyboard
from picamera import PiCamera
from fractions import Fraction
from pythonosc import udp_client
from omxplayer.player import OMXPlayer
from stoneMl import stoneMl
from make_Stamp import make_Stamp
from time import sleep
from dimensionplus import dpSubprocess

#init config file
config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

# file name
# captrue stone
original_img = config['captrue']['original_img']
result_img = config['captrue']['captrue_result']

# video
VIDEO_PATH = config['video']['VIDEO_PATH']
VIDEO_FILE_IDLE = config['video']['VIDEO_FILE_IDLE']
VIDEO_FILE_SCANNING = config['video']['VIDEO_FILE_SCANNING']
VIDEO_FILE_SCANNING_CMP = config['video']['VIDEO_FILE_SCANNING_CMP']
VIDEO_FILE_SEE_STORY = config['video']['VIDEO_FILE_SEE_STORY']
VIDEO_FILE_SCAN_ERR = config['video']['VIDEO_FILE_SCAN_ERR']
VIDEO_FILE_PRT_CMP = config['video']['VIDEO_FILE_PRT_CMP']
VIDEO_FILE_FULL = config['video']['VIDEO_FILE_FULL']

# init osc
host_ip = config['osc']['host_ip']
host_port = int(config['osc']['host_port'])
osc_sendMsg2Beach = udp_client.SimpleUDPClient(host_ip,host_port)

# define GPIO Pin Number
gpioPin = 5

# Define GPIO Function
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpioPin, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
#GPIO.add_event_detect(gpioPin, GPIO.RISING, bouncetime = 200)

#init video number
video_Num = 1

stoneNum = int(config['captrue']['stone_Num'])
stampNum = int(config['stamp']['stamp_Num'])

class thread_with_trace(threading.Thread):
  def __init__(self, *args, **keywords):
    threading.Thread.__init__(self, *args, **keywords)
    self.killed = False
  
  def start(self):
    self.__run_backup = self.run
    self.run = self.__run      
    threading.Thread.start(self)
  
  def __run(self):
    sys.settrace(self.globaltrace)
    self.__run_backup()
    self.run = self.__run_backup
  
  def globaltrace(self, frame, event, arg):
    if event == 'call':
      return self.localtrace
    else:
      return None
  
  def localtrace(self, frame, event, arg):
    if self.killed:
      if event == 'line':
        raise SystemExit()
    return self.localtrace
  
  def kill(self):
    self.killed = True

def image_resize(image, width = None, height = None, inter = cv2.INTER_AREA):
    # initialize the dimensions of the image to be resized and
    # grab the image size
    dim = None
    (h, w) = image.shape[:2]

    # if both the width and height are None, then return the
    # original image
    if width is None and height is None:
        return image

    # check to see if the width is None
    if width is None:
        # calculate the ratio of the height and construct the
        # dimensions
        r = height / float(h)
        dim = (int(w * r), height)

    # otherwise, the height is None
    else:
        # calculate the ratio of the width and construct the
        # dimensions
        r = width / float(w)
        dim = (width, int(h * r))

    # resize the image
    resized = cv2.resize(image, dim, interpolation = cv2.INTER_CUBIC)

    # return the resized image
    return resized

def catchStone(workState):
    workState.put(0)
    workState.task_done()

    #set camera
    camera = PiCamera(resolution=(1920, 1080))
    camera.shutter_speed = int(config['camera']['shutter_speed'])
    sleep(1)
    camera.capture(original_img)
    workState.put(1)
    workState.task_done()
    camera.close()

    # Read image
    img = cv2.imread(original_img)

    #crop image 
    x=284	
    y=23
    w=1322
    h=839
    crop_img = img[y:y+h,x:x+w]
    crop_img = image_resize(crop_img, height =1440)
    cv2.imwrite('/home/pi/stoneScanner/data/pic/captrue/dbug/crop_img.png',crop_img)

    # img to darknnes
    # a = np.double(crop_img)
    # b = a - 60
    # dark_img = np.uint8(b)

    # get a blank canvas for drawing contour on and convert img to grayscale 
    canvas = np.zeros(crop_img.shape,dtype="uint8") 
    img2gray = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY) 

    # filter out small lines between counties 
    kernel_4_2d = np.ones((5,5),np.float32)/25 
    img2gray = cv2.filter2D(img2gray,-1,kernel_4_2d) 

    # threshold the image and extract contours 
    # can change cv2.threshold function thresh and max value
    ret,thresh = cv2.threshold(img2gray,245.5,255,cv2.THRESH_BINARY_INV) 
    im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

    # another get Contours option
    # blurred = cv2.GaussianBlur(img2gray, (11, 11), 0)
    # edged = cv2.Canny(blurred, 20, 180)
    # (_, contours, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find the stone (biggest area) 
    cnt = contours[0] 
    max_area = cv2.contourArea(cnt) 
    for cont in contours: 
        if cv2.contourArea(cont) > max_area: 
            cnt = cont 
            max_area = cv2.contourArea(cont)

    # define stone contour approx
    perimeter = cv2.arcLength(cnt,True) 
    epsilon = 0.00001*cv2.arcLength(cnt,True) 
    approx = cv2.approxPolyDP(cnt,epsilon,True) 

    cv2.drawContours(canvas, cnt, -1,(255,255,255),-1) 
    cv2.drawContours(canvas, [approx],-1,(255,255,255),-1) 

    # make mask
    mask_Init = np.zeros(img2gray.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask_Init, [approx], -1, (255,255,255), -1)

    # erode mask
    kernel2Erode  = np.ones((10,10), np.uint8)
    mask_Erode = cv2.erode(mask_Init, kernel2Erode, iterations= 5)

    # cut the stone
    (x, y, w, h) = cv2.boundingRect(cnt)
    stone = crop_img[y:y + h, x:x + w]
    mask_Erode = mask_Erode[y:y + h, x:x + w]

    cv2.imwrite('/home/pi/stoneScanner/data/pic/captrue/dbug/mask.png',mask_Erode)

    stone = cv2.bitwise_and(stone, stone, mask = mask_Erode)
    image = image_resize(stone, height = 1024)

    #transparent background
    tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(image)
    rgba = [b,g,r, alpha]
    result = cv2.merge(rgba,4)
    cv2.imwrite(result_img+str(stoneNum)+'.png',result)    

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    workState.put(2)
    workState.task_done()

def writes_StoneNum(stoneNum,stampNum):
  config['captrue']['stone_Num']=str(stoneNum)
  config['stamp']['stamp_Num']=str(stampNum)
  with open('/home/pi/stoneScanner/stone_scanner.ini', 'w') as configfile:
      config.write(configfile)

def playerExit(code,num):
    global video_Num
    video_Num =video_Num + 1
    #print('exit',code)

def upload_Stone(img_Path):
    my_files = {'file': open(img_Path,'rb')}
    values = {'folder':'Photos/incoming/'}
    r = requests.post(config['captrue']['http_Add'],files = my_files,data=values)

#load white background
dpSubprocess.load_background_image(image = 'background.jpg')

player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_IDLE, args='--loop')
player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
sleep(3)
player.play()

while True:
    if GPIO.input(gpioPin):
        player.quit()
        dpSubprocess.load_background_image(image = 'background.jpg')
        stone_CAP_State = queue.Queue()
        stone_CAP = thread_with_trace(target = catchStone,args=(stone_CAP_State,))
        stone_CAP.start()
        while True:
            if stone_CAP_State.get() == 1:
                player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_SCANNING, args='--loop')
                player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                sleep(3)
                player.play()
                while True:
                    if stone_CAP_State.get() == 2:
                        player.quit()
                        stone_CAP_State.join()
                        stone_CAP.kill()
                        stone_CAP.join()
                        
                        #upload stone image to pc
                        upload_Stone(result_img+str(stoneNum)+'.png')
                        
                        #stone ML
                        # stone_id = stoneMl(stoneNum)

                        player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_SCANNING_CMP)
                        player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                        sleep(3)
                        player.play()
                        while video_Num != 4:
                          # print("video3")
                          pass
                        player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_SEE_STORY)
                        player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                        sleep(3)
                        player.play()
                        osc_sendMsg2Beach.send_message("/scanner/left/img/upload",1)
                        while video_Num != 5:
                          # print("video4")
                          pass
                        # make_Stamp(stoneNum,stampNum,stone_id)
                        player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_PRT_CMP)
                        player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                        sleep(3)
                        player.play()
                        while video_Num != 6:
                          # print("video5")
                          pass
                        stone_id = 0
                        video_Num = 1 
                        stoneNum = stoneNum + 1 
                        stampNum = stampNum + 1
                        writes_StoneNum(stoneNum,stampNum,)
                        player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_IDLE, args='--loop')
                        player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                        sleep(3)
                        player.play()
                        break 
                break           
    if keyboard.is_pressed('q'):
      player.quit()
      sys.exit()
      break
    # print("level 1")