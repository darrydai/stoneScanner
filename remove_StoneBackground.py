import configparser
import cv2
import skimage.exposure
import queue
import numpy as np
#import multiprocessing as mp
import threading, queue
from picamera import PiCamera
from fractions import Fraction
from dimensionplus import dpSubprocess
from time import sleep

config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

#File name
original_img = config['captrue']['original_img']
result_img = config['captrue']['captrue_result']

stoneNum = int(config['stone']['stone_Num'])

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
    # dpSubprocess.load_background_image(image='background.jpg')
    #set camera
    camera = PiCamera(resolution=(1920,1080))
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
    cv2.imwrite('/home/pi/stoneScanner/data/pic/captrue/dbug/crop_img.png',crop_img)

    #darkness of image
    a = np.double(crop_img)
    b = a - 60
    dark_img = np.uint8(b)
    cv2.imwrite('/home/pi/stoneScanner/data/pic/captrue/dbug/dark_img.png',dark_img)

    #find the stone contours
    gray = cv2.cvtColor(dark_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edged = cv2.Canny(blurred, 30, 150)
    (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours = contours[0] if len(contours) == 2 else contours[1]
    #big_contour = max(contours, key=cv2.contourArea)
    #big_contour = max(cnts, key=cv2.contourArea)
    stone = crop_img.copy()
    #cv2.drawContours(stone,[big_contour], 0, 255, -1)
    cv2.drawContours(stone, cnts, -1, (0, 255, 0), 2)
    cv2.imwrite('/home/pi/stoneScanner/data/pic/Contours_img.png',stone)


    #Take out the stone
    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        stone = crop_img[y:y + h, x:x + w]
        #cv2.imwrite('/home/pi/stoneScanner/data/pic/stone0.png',stone)
        # mask = thresh[y:y + h, x:x + w]
        mask = np.zeros(gray.shape[:2],dtype="uint8")
        cv2.drawContours(mask, [c], -1, 255, -1)

        #ERODE mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21,21))
        mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)
        cv2.imwrite('/home/pi/stoneScanner/data/pic/captrue/dbug/mask.png',mask)

        mask = mask[y:y + h, x:x + w]
        stone = cv2.bitwise_and(stone, stone, mask = mask)
        image = image_resize(stone, height = 1024)

        #transparent background
        tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
        b, g, r = cv2.split(image)
        rgba = [b,g,r, alpha]
        result = cv2.merge(rgba,4)
        
        #for multi detection 
        #a=str(i)
        #save_location='/home/pi/stoneScanner/data/pic/stone'+a+'.png'
        #cv2.imwrite(save_location,result)

        cv2.imwrite(result_img+str(stoneNum)+'.png',result)
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    workState.put(2)
    workState.task_done()

def main():
    q = queue.Queue()
    capStone = threading.Thread(target=catchStone, args=(q,))
    dpSubprocess.load_background_image(image='background.jpg')
    capStone.start()
    q.join()
    capStone.join()


if __name__ == '__main__':
    main()