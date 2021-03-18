import cv2
import numpy as np
import skimage.exposure
from dimensionplus import dpSubprocess
from time import sleep

dpSubprocess.load_background_image(image='background.jpg')

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

x=284	
y=23

w=1322
h=839

# def otsu_canny(image, lowrate=0.5):
#     if len(image.shape) > 2:
#         image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#     # Otsu's thresholding
#     ret, _ = cv2.threshold(image, thresh=0, maxval=255, type=(cv2.THRESH_BINARY + cv2.THRESH_OTSU))
#     edged = cv2.Canny(image, threshold1=(ret * lowrate), threshold2=ret)

#     # return the edged image
#     return edged

crop_img = img[y:y+h,x:x+w]
#hh, ww = crop_img.shape[:2]
cv2.imwrite('/home/pi/stoneScanner/data/pic/crop_img.png',crop_img)

gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)
edged = cv2.Canny(blurred, 20, 60)
# edged = otsu_canny(crop_img)

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
    mask = thresh[y:y + h, x:x + w]
    cv2.imwrite('/home/pi/stoneScanner/data/pic/mask2.png',mask)
    stone = cv2.bitwise_and(stone, stone, mask = mask)
    image = image_resize(stone, height = 1024)
    tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(image)
    rgba = [b,g,r, alpha]
    result = cv2.merge(rgba,4)
    cv2.imwrite('/home/pi/stoneScanner/data/pic/stone.png',result)

cv2.waitKey(0)
cv2.destroyAllWindows()