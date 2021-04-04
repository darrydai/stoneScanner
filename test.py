import numpy as np 
import cv2 

# load image and shrink - it's massive 
img = cv2.imread('/home/pi/stoneScanner/data/pic/captrue/dbug/crop_img.png') 

# get a blank canvas for drawing contour on and convert img to grayscale 
canvas = np.zeros(img.shape,dtype="uint8")
img2gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 

# filter out small lines between counties 
kernel = np.ones((5,5),np.float32)/25 
img2gray = cv2.filter2D(img2gray,-1,kernel) 

# threshold the image and extract contours 
ret,thresh = cv2.threshold(img2gray,245.5,255,cv2.THRESH_BINARY_INV) 
im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

# blurred = cv2.GaussianBlur(img2gray, (11, 11), 0)
# edged = cv2.Canny(blurred, 50, 100)
# (_, contours, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)



cv2.drawContours(canvas, contours, -1,255,-1)
cv2.imwrite("/home/pi/stoneScanner/data/pic/captrue/dbug/canvas.png",canvas) 
# find the main island (biggest area) 
cnt = contours[0]
max_area = cv2.contourArea(cnt) 

for cont in contours: 
    if cv2.contourArea(cont) > max_area: 
     cnt = cont 
     max_area = cv2.contourArea(cont)


# define main island contour approx. and hull 
perimeter = cv2.arcLength(cnt,True) 
epsilon = 0.0001*cv2.arcLength(cnt,True) 
approx = cv2.approxPolyDP(cnt,epsilon,True) 
 
cv2.drawContours(canvas, [approx],-1,(255,255,255),-1) 

cv2.imwrite("/home/pi/stoneScanner/data/pic/captrue/dbug/approx.png",canvas) 

kernel  = np.ones((10,10), np.uint8)
mask = cv2.erode(canvas, kernel, iterations= 1)

(x, y, w, h) = cv2.boundingRect(cnt)
mask = mask[y:y + h, x:x + w]

cv2.imwrite("/home/pi/stoneScanner/data/pic/captrue/dbug/Contour.png",mask) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 