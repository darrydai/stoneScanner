import cv2
import numpy as np
import skimage.exposure
from dimensionplus import dpSubprocess
from time import sleep

dpSubprocess.load_background_image(image='background.jpg')

sleep(2.0)

webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
# 讀取影像
return_value, image = webcam.read()
# 儲存名為Picture.png的照片
cv2.imwrite("/home/pi/stoneScanner/data/pic/picture.png", image)
# 刪除webcam，避免影像佔用資源
del(webcam)

# Read image
img = cv2.imread('/home/pi/stoneScanner/data/pic/picture.png')

x=302	
y=47

w=1470
h=900

crop_img = img[y:y+h,x:x+w]
hh, ww = crop_img.shape[:2]
cv2.imwrite('/home/pi/stoneScanner/data/pic/crop_img.png',crop_img)

gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
#blurred = cv2.GaussianBlur(gray, (11, 11), 0)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(gray, 30, 150)

#(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]
big_contour = max(contours, key=cv2.contourArea)

#contour = np.zeros_like(gray)
stone = crop_img.copy()
#cv2.drawContours(stone, cnts, -1, (0, 255, 0), 2)
cv2.drawContours(stone, [big_contour], 0, 255, -1)
cv2.imwrite('/home/pi/stoneScanner/data/pic/Contours_img.png',stone)

stone=cv2.cvtColor(stone, cv2.COLOR_BGR2HSV)

lower = np.array([100, 43, 46])
upper = np.array([124, 255, 255])
thresh = cv2.inRange(stone, lower, upper)
cv2.imwrite('/home/pi/stoneScanner/data/pic/thresh.png',thresh)

#blur = cv2.GaussianBlur(contour, (5,5), sigmaX=0, sigmaY=0, borderType = cv2.BORDER_DEFAULT)
#mask0 = skimage.exposure.rescale_intensity(blur, in_range=(127.5,255), out_range=(0,255))
#cv2.imwrite('/home/pi/stoneScanner/data/pic/mask0.png',mask0)

for (i, c) in enumerate(contours):

    (x, y, w, h) = cv2.boundingRect(c)
    stone = crop_img[y:y + h, x:x + w]
    cv2.imwrite('/home/pi/stoneScanner/data/pic/stone0.png',stone)
    #mask = np.zeros(crop_img.shape[:2],dtype="uint8")
    #cv2.imwrite('/home/pi/stoneScanner/data/pic/mask1.png',mask)
    #((centerX, centerY), radius) = cv2.minEnclosingCircle(c)
    #cv2.circle(mask, (int(centerX), int(centerY)), int(radius), 0, -1)
    mask = thresh[y:y + h, x:x + w]
    cv2.imwrite('/home/pi/stoneScanner/data/pic/mask2.png',mask)
    result=cv2.bitwise_and(stone, stone, mask = mask)
    cv2.imwrite('/home/pi/stoneScanner/data/pic/stone.png',result)

cv2.waitKey(0)
cv2.destroyAllWindows()