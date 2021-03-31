from PIL import Image,ImageOps,ImageEnhance
import configparser
import numpy 
import numpy as np
import random
import subprocess

config = configparser.ConfigParser()
config.read('/home/pi/stoneScanner/stone_scanner.ini')

def make_Stamp():
    #path
    bg_Path=config['stamp']['stamp_BG']+'/Text_'+str(random.randint(1,14))+'_01.png'
    stoneImg_path=config['stamp']['stone_BG_removed']
    save_path=config['stamp']['stamp_save']+'/stamp_1.png'

    #Image processing parameter
    sharpness = float(config['stamp']['sharpness'])
    contrast = float(config['stamp']['contrast'])
    color = float(config['stamp']['color'])

    #stamp background black area
    blackArea = [498,450]

    #load background
    bg_Img=Image.open(bg_Path)
    bg_Img=bg_Img.convert('RGBA')

    #load stone image
    stoneImg=Image.open(stoneImg_path)
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
    bg_Img.save(save_path,dpi=(600,300))

    subprocess.run(["sudo","brother_ql","-b","linux_kernel","-p","/dev/usb/lp0","-m","QL-800","print","-l","62","--red","/home/pi/stoneScanner/data/pic/stamp/stamp_result/stamp_1.png"],stdout=subprocess.PIPE)

def main():
    make_Stamp()

if __name__ == '__main__':
    main()