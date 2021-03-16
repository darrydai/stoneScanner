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

# Read image
img = cv2.imread('/home/pi/stoneScanner/data/pic/picture.png')
hh, ww = img.shape[:2]

# threshold on white
# Define lower and uppper limits
lower = np.array([200, 200, 200])
upper = np.array([255, 255, 255])

# Create mask to only select black
thresh = cv2.inRange(img, lower, upper)

# apply morphology
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20,20))
morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# get contours
#contours = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]

# draw white contours on black background as mask
mask = np.zeros((hh,ww), dtype=np.uint8)
for cntr in contours:
    cv2.drawContours(mask, [cntr], 0, (255,255,255), -1)

# get convex hull
points = np.column_stack(np.where(thresh.transpose() > 0))
hullpts = cv2.convexHull(points)
((centx,centy), (width,height), angle) = cv2.fitEllipse(hullpts)
print("center x,y:",centx,centy)
print("diameters:",width,height)
print("orientation angle:",angle)

# draw convex hull on image
hull = img.copy()
cv2.polylines(hull, [hullpts], True, (0,0,255), 1)

# create new circle mask from ellipse 
circle = np.zeros((hh,ww), dtype=np.uint8)
cx = int(centx)
cy = int(centy)
radius = (width+height)/8
cv2.circle(circle, (cx,cy), int(radius), 255, -1)

# erode circle a bit to avoid a white ring
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))
circle = cv2.morphologyEx(circle, cv2.MORPH_ERODE, kernel)

# combine inverted morph and circle
mask2 = cv2.bitwise_and(255-thresh, 255-thresh, mask=mask)

# apply mask to image
result = cv2.bitwise_and(img, img, mask=mask2)

result = cv2.blur(result, (5,5))

# save results
cv2.imwrite('/home/pi/stoneScanner/data/pic/thresh2.jpg',thresh)
cv2.imwrite('/home/pi/stoneScanner/data/pic/morph2.jpg',morph)
cv2.imwrite('/home/pi/stoneScanner/data/pic/mask2.jpg',mask)
cv2.imwrite('/home/pi/stoneScanner/data/pic/hull2.jpg',hull)
cv2.imwrite('/home/pi/stoneScanner/data/pic/circle.jpg',circle)
cv2.imwrite('/home/pi/stoneScanner/data/pic/result2.png',result)

cv2.waitKey(0)
cv2.destroyAllWindows()