from PIL import Image,ImageOps,ImageEnhance
import numpy 
import numpy as np
import random

sharpness = 3
contrast = 2.5
color = 15

blackArea = [498,450]

file_Num = random.randint(1,14)

#load background
bg_Path='/Users/Darry/Desktop/Darrys_project/2021/04_文博花蓮館/code/stoneScanner/data/pic/stamp/stampBG/Text_'+str(file_Num)+'_01.png'
bg_Img=Image.open(bg_Path)
bg_Img=bg_Img.convert('RGBA')

#load stone image
stoneImg=Image.open("/Users/Darry/Desktop/Darrys_project/2021/04_文博花蓮館/code/stoneScanner/data/pic/stone_morph.png")
stoneImg=stoneImg.convert('RGBA')

#Enhance stone image sharpness
enh_sha = ImageEnhance.Sharpness(stoneImg)
stoneImg = enh_sha.enhance(sharpness)

#Enhance stone image contrast
enh_con = ImageEnhance.Contrast(stoneImg)
stoneImg = enh_con.enhance(contrast)

#Enhance stone image color
enh_col = ImageEnhance.Color(stoneImg)
stoneImg = enh_col.enhance(color)

#resize stone image
stoneImg.thumbnail((295,295),Image.BILINEAR)
stoneW,stoneH=stoneImg.size

stoneCopy=stoneImg

#convert image to gary then to binary
stoneCopy=stoneCopy.convert('L')
stoneCopy=stoneCopy.convert('1')

#shift the stone image position
bg_Img.paste(stoneCopy,(int((blackArea[0]-stoneW)/2),int((blackArea[1]-stoneH)/2)),stoneImg)
bg_Img.save("/Users/Darry/Desktop/Darrys_project/2021/04_文博花蓮館/code/stoneScanner/data/pic/stamp/01.png",dpi=(600,300))
