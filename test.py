import numpy as np 
import cv2 

# load image and shrink - it's massive 
img = cv2.imread('/home/pi/stoneScanner/data/pic/crop_img.png') 
# img = cv2.resize(img, None,fx=0.25, fy=0.25, interpolation = cv2.INTER_CUBIC) 

# get a blank canvas for drawing contour on and convert img to grayscale 
canvas = np.zeros(img.shape[:2],dtype="uint8") 
img2gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 

# filter out small lines between counties 
# kernel = np.ones((5,5),np.float32)/25 
# img2gray = cv2.filter2D(img2gray,-1,kernel) 
cv2.imwrite("img2gray.png",img2gray) 
# threshold the image and extract contours 
ret,thresh = cv2.threshold(img2gray,250,255,cv2.THRESH_BINARY_INV) 
im2,contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 

# blurred = cv2.GaussianBlur(img2gray, (11, 11), 0)
# edged = cv2.Canny(blurred, 50, 100)
# (_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(canvas, contours, -1,255,-1)
cv2.imwrite("canvas.png",canvas) 
# find the main island (biggest area) 
cnt = contours[0] 
max_area = cv2.contourArea(cnt) 

for cont in cnts: 
    if cv2.contourArea(cont) > max_area: 
     cnt = cont 
     max_area = cv2.contourArea(cont)



# define main island contour approx. and hull 
#perimeter = cv2.arcLength(cnt,True) 
epsilon = 0.01*cv2.arcLength(cnt,True) 
approx = cv2.approxPolyDP(cnt,epsilon,True) 

#hull = cv2.convexHull(cnt) 

# cv2.isContourConvex(cnt) 

cv2.drawContours(canvas, cnt, -1,(255,255,255),-1) 
cv2.drawContours(canvas, [approx],-1,(255,255,255),-1) 
(x, y, w, h) = cv2.boundingRect(cnt)
mask = canvas[y:y + h, x:x + w]
kernel  = np.ones((10,10), np.uint8)
mask = cv2.erode(mask, kernel, iterations= 10)
## cv2.drawContours(canvas, hull, -1, (0, 0, 255), 3) # only displays a few points as well. 


cv2.imwrite("Contour.png",mask) 
cv2.waitKey(0) 
cv2.destroyAllWindows() 