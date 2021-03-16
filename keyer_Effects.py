import cv2
import numpy as np
from dimensionplus import dpSubprocess

dpSubprocess.load_background_image(image='background.jpg')

webcam = cv2.VideoCapture(0)
# 讀取影像
return_value, image = webcam.read()
# 儲存名為Picture.png的照片
cv2.imwrite("/home/pi/stoneScanner/data/pic/picture.png", image)
# 刪除webcam，避免影像佔用資源
del(webcam)

img=cv2.imread('/home/pi/stoneScanner/data/pic/picture.png')
## (1) Convert to gray, and threshold
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(gray)

#二值化，将背景150到255的像素值改为255
th, threshed = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
## (2) Morph-op to remove noise
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11,11))
morphed = cv2.morphologyEx(threshed, cv2.MORPH_CLOSE, kernel)
## (3) Find the max-area contour
cnts = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
cnt = sorted(cnts, key=cv2.contourArea)[-1]
## (4) Crop and save it
x,y,w,h = cv2.boundingRect(cnt)

#取反色，删除背景的影响。
dst = 255-img[y:y+h, x:x+w]
cv2.imwrite("/home/pi/stoneScanner/data/pic/001.png", dst)