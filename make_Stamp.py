from PIL import Image,ImageOps,ImageEnhance
import configparser
import numpy 
import numpy as np
import random
import subprocess
# import ql800_Print
import qltest
import logging

config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

def make_Stamp(stoneNum,stampNum,stone_id,stampBgNum):

    if stone_id == 1:
        bg_Path=config['stamp']['stamp_BG']+'Text_01_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 2:
        bg_Path=config['stamp']['stamp_BG']+'Text_02_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 3:
        bg_Path=config['stamp']['stamp_BG']+'Text_03_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 4:
        bg_Path=config['stamp']['stamp_BG']+'Text_04_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 6:
        bg_Path=config['stamp']['stamp_BG']+'Text_06_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 7:
        bg_Path=config['stamp']['stamp_BG']+'Text_07_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 8:
        bg_Path=config['stamp']['stamp_BG']+'Text_08_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 9:
        bg_Path=config['stamp']['stamp_BG']+'Text_09_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 10:
        bg_Path=config['stamp']['stamp_BG']+'Text_10_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 11:
        bg_Path=config['stamp']['stamp_BG']+'Text_11_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 12:
        bg_Path=config['stamp']['stamp_BG']+'Text_12_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 13:
        bg_Path=config['stamp']['stamp_BG']+'Text_13_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 14:
        bg_Path=config['stamp']['stamp_BG']+'Text_14_'+str(stampBgNum).zfill(2)+'.png'
    if stone_id == 15:
        bg_Path=config['stamp']['stamp_BG']+'Text_Easter_'+str(stampBgNum).zfill(2)+'.png'
        qltest.sendToPrinter(bg_Path)
        return
    # if stone_id == 'mountain':
    #     bg_Path=config['stamp']['stamp_BG']+'/Text_13_01.png'

    #path
    #bg_Path=config['stamp']['stamp_BG']+'/Text_'+str(random.randint(1,14))+'_01.png'
    stoneImg_path=config['stamp']['stone_BG_removed']
    save_path=config['stamp']['stamp_save']+'stamp_'+str(stampNum)+'.png'

    #Image processing parameter
    sharpness = float(config['stamp']['sharpness'])
    contrast = float(config['stamp']['contrast'])
    color = float(config['stamp']['color'])

    #stamp background black area
    blackArea = [498,450]

    #load background
    bg_Img=Image.open(bg_Path)
    bg_Img=bg_Img.convert('RGBA')
    bg_Img.thumbnail((696,696),Image.ANTIALIAS)

    #load stone image
    stoneImg=Image.open(stoneImg_path+'stone_'+str(stoneNum).zfill(4)+'.png')
    stoneImg=stoneImg.convert('RGBA')
    #stoneImg=stoneImg.rotate(90)
    stoneImg.thumbnail((295,295),Image.ANTIALIAS)

    # stoneImg=stoneImg.convert('L')
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
    #stoneImg.thumbnail((295,295),Image.ANTIALIAS)
    stoneW,stoneH=stoneImg.size

    stoneCopy=stoneImg

    #convert image to gary then to binary
    # stoneCopy=stoneCopy.convert('L')
    stoneCopy=stoneCopy.convert('1')

    #shift the stone image position
    bg_Img.paste(stoneCopy,(int((blackArea[1]-stoneW)/2),int((blackArea[0]-stoneH)/2)),stoneImg)
    #bg_Img.thumbnail((696,696),Image.ANTIALIAS)
    # new = bg_Img.rotate(90)
    bg_Img.save(save_path,dpi=(300,300))
    # new.save(save_path,dpi=(300,300))
    # ql800_Print.sendToPrinter(save_path)
    qltest.sendToPrinter(save_path)
    # subprocess.run(["sudo","brother_ql","-b","linux_kernel","-p","/dev/usb/lp0","-m","QL-800","print","-l","62","-d","--red",save_path],stdout=subprocess.PIPE)


def main():
    try:
        make_Stamp(227,0,1)
    except Exception as e:
        print("發生錯誤：",e)

if __name__ == '__main__':
    main()