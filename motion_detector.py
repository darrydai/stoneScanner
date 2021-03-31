import cv2
# import pyttsx3
import threading



baseline_image=None
status_list=[None,None]
video=cv2.VideoCapture(0)

# 設定影像尺寸
width = 320
height = 240

# 設定擷取影像的尺寸大小
video.set(cv2.CAP_PROP_FRAME_WIDTH, width)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

while True:
    check, frame = video.read()
    status=0
    gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray_frame=cv2.GaussianBlur(gray_frame,(25,25),0)

    if baseline_image is None:
        baseline_image=gray_frame
        continue

    delta=cv2.absdiff(baseline_image,gray_frame)
    threshold=cv2.threshold(delta, 90, 255, cv2.THRESH_BINARY)[1]
    cntImg,cnts,_=cv2.findContours(threshold,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        if cv2.contourArea(c) < 10000:
            continue

        status=1
        (x, y, w, h)=cv2.boundingRect(c)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 1)
        
    status_list.append(status)

    if status_list[-1]==1 and status_list[-2]==0:
        print("have something in...")
   
    cv2.imshow("Color Frame",frame)
    key=cv2.waitKey(1)

    if key==ord('q'):
        if status==1:
            times.append(datetime.now())
        break

#Clean up, Free memory
video.release()
cv2.destroyAllWindows
