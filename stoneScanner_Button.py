import sys
import numpy as np
import cv2
import configparser
import skimage.exposure
import queue
import threading,trace,queue
import keyboard
from picamera import PiCamera
from fractions import Fraction
from omxplayer.player import OMXPlayer
from time import sleep
from dimensionplus import dpSubprocess

#init config file
config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

#File name
original_img = config['captrue']['original_img']
result_img = config['captrue']['captrue_result']

background = config['pic']['background']

VIDEO_PATH = config['video']['VIDEO_PATH']
VIDEO_FILE_IDLE = config['video']['VIDEO_FILE_IDLE']
VIDEO_FILE_SCANNING = config['video']['VIDEO_FILE_SCANNING']
VIDEO_FILE_SCANNING_CMP = config['video']['VIDEO_FILE_SCANNING_CMP']
VIDEO_FILE_SEE_STORY = config['video']['VIDEO_FILE_SEE_STORY']
VIDEO_FILE_SCAN_ERR = config['video']['VIDEO_FILE_SCAN_ERR']
VIDEO_FILE_PRT_CMP = config['video']['VIDEO_FILE_PRT_CMP']
VIDEO_FILE_FULL = config['video']['VIDEO_FILE_FULL']

#init video number
video_Num = 1

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
    #hh, ww = crop_img.shape[:2]
    cv2.imwrite('/home/pi/stoneScanner/data/pic/crop_img.png',crop_img)

    # get a blank canvas for drawing contour on and convert img to grayscale 
    canvas = np.zeros(crop_img.shape[:2],dtype="uint8") 
    img2gray = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY) 

    # filter out small lines between counties 
    kernel = np.ones((5,5),np.float32)/25 
    img2gray = cv2.filter2D(img2gray,-1,kernel) 
    cv2.imwrite("img2gray.png",img2gray)

    # threshold the image and extract contours 
    # can change cv2.threshold function thresh and max value
    ret,thresh = cv2.threshold(img2gray,250,255,cv2.THRESH_BINARY_INV) 
    im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

    # another option
    # blurred = cv2.GaussianBlur(img2gray, (11, 11), 0)
    # edged = cv2.Canny(blurred, 50, 100)
    # (_, contours, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find the stone (biggest area) 
    cnt = contours[0] 
    max_area = cv2.contourArea(cnt) 

    for cont in contours: 
        if cv2.contourArea(cont) > max_area: 
            cnt = cont 
            max_area = cv2.contourArea(cont)

    # define stone contour approx. and hull 
    perimeter = cv2.arcLength(cnt,True) 
    epsilon = 0.00001*cv2.arcLength(cnt,True) 
    approx = cv2.approxPolyDP(cnt,epsilon,True) 

    cv2.drawContours(canvas, cnt, -1,(255,255,255),-1) 
    cv2.drawContours(canvas, [approx],-1,(255,255,255),-1) 

    kernel  = np.ones((10,10), np.uint8)
    erode = cv2.erode(canvas, kernel, iterations= 3)

    (x, y, w, h) = cv2.boundingRect(cnt)
    stone = crop_img[y:y + h, x:x + w]
    mask = erode[y:y + h, x:x + w]
    cv2.imwrite('/home/pi/stoneScanner/data/pic/mask.png',mask)
    stone = cv2.bitwise_and(stone, stone, mask = mask)
    image = image_resize(stone, height = 1024)

    #transparent background
    tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(image)
    rgba = [b,g,r, alpha]
    result = cv2.merge(rgba,4)
    cv2.imwrite(result_img,result)    

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    workState.put(2)
    workState.task_done()

def playerExit(code,num):
    global video_Num
    video_Num =video_Num + 1
    print('exit',code)

#load white background
dpSubprocess.load_background_image(image = 'background.jpg')

player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_IDLE, args='--loop')
player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
sleep(3)
player.play()

while True:
    if keyboard.is_pressed('a'):
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
                        while video_Num != 5:
                          # print("video4")
                          pass
                        player = OMXPlayer(VIDEO_PATH+VIDEO_FILE_PRT_CMP)
                        player.exitEvent += lambda _, exit_code: playerExit(exit_code,video_Num)
                        sleep(3)
                        player.play()
                        while video_Num != 6:
                          # print("video5")
                          pass
                        video_Num = 1  
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