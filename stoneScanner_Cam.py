import sys
from dimensionplus import dpSubprocess
from time import sleep
import cv2
import numpy as np
import multiprocessing as mp
import subprocess
import psutil
import asyncio
from omxplayer.player import OMXPlayer
import logging

logging.basicConfig(level=logging.INFO)

# Give the preset info
VIDEO_PATH = "/home/pi/stoneScanner/data/videos/"
# File names
VIDEO_FILE_IDLE = "01-Idel.mp4"
VIDEO_FILE_SCANNING = "02-Scanning.mp4"
VIDEO_FILE_SCANNING_CMP = "03-1-ScanningCompleted.mp4"
VIDEO_FILE_SEE_STORY = "03-3-SeeStory.mp4"
VIDEO_FILE_SCAN_ERR = "04-ScanningError.mp4"
VIDEO_FILE_PRT_CMP = "05-PrintComplete.mp4"
VIDEO_FILE_FULL = "full.mp4"
IMG_BACKGROUD_FILE = "background.jpg"

bgPlayer = OMXPlayer(VIDEO_PATH, args=['--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer0')
player = OMXPlayer(VIDEO_PATH, dbus_name='org.mpris.MediaPlayer2.omxplayer1')



#dpSubprocess.load_background_image(image='background.jpg')


def motionDT(workState):
	# 開啟網路攝影機

	if (player.playback_status == "Playing"):
		return

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
			workState.put(1)
			#print("have something in...")
	
		cv2.imshow("Color Frame",frame)
		key=cv2.waitKey(1)

		if key==ord('q'):
			if status==1:
				times.append(datetime.now())
			break

	#Clean up, Free memory
	video.release()
	cv2.destroyAllWindows


def playBGVideo(video, startPos):
	video_path = VIDEO_PATH + video
	player_log = logging.getLogger("Stone Player - BG")

	try:
		
		bgPlayer = OMXPlayer(video_path, args=['--loop'], dbus_name='org.mpris.MediaPlayer2.omxplayer0')
	

		if bgPlayer.playback_status() == "Playing":
			return
		


		bgPlayer.playEvent += lambda _: player_log.info("Play")
		bgPlayer.pauseEvent += lambda _: player_log.info("Pause")
		bgPlayer.stopEvent += lambda _: player_log.info("Stop")
		
		# global playbackStatus
		# playbackStatus = player.playback_status()
		
		sleep(5)
		bgPlayer.set_position(startPos) #seconds from the start of the video
		# player.pause()

		# sleep(2)

		# player.set_aspect_mode('stretch')
		# player.set_video_pos(0, 0, 200, 200)
		bgPlayer.play()
		bgPlayer.quit()

	except Exception as err:
		print("bgPlayer ERROR:", str(err))


def playVideo(video, startPos):
	video_path = VIDEO_PATH + video
	player_log = logging.getLogger("Stone Player")

	try:
		player = OMXPlayer(video_path, dbus_name='org.mpris.MediaPlayer2.omxplayer1')

		if bgPlayer.playback_status() == "Playing":
			bgPlayer.pause()
			bgPlayer.hide_video()
		
		player.playEvent += lambda _: player_log.info("Play")
		player.pauseEvent += lambda _: player_log.info("Pause")
		player.stopEvent += lambda _: player_log.info("Stop")
		
		sleep(5)
		player.set_position(startPos) #seconds from the start of the video
		# player.pause()

		# sleep(2)

		# player.set_aspect_mode('stretch')
		# player.set_video_pos(0, 0, 200, 200)

		player.play()
		player.quit()

	except Exception as err:
		print("Player ERROR:", str(err))


	
def lablePrint():
	#lablePrint = subprocess.run(["sudo","brother_ql","-b",backend,"-p",printer,"-m",pModel,"print","-l","62","--red","/home/pi/stoneScanner/data/pic/text_text_red.jpg"],stdout=subprocess.PIPE)
	lablePrint = subprocess.run(["sudo","brother_ql","-b","linux_kernel","-p","/dev/usb/lp0","-m","QL-800","print","-l","62","--red","/home/pi/stoneScanner/data/pic/text_text_red.jpg"],stdout=subprocess.PIPE)




def main():
	try:
		#player = OMXPlayer(VIDEO_PATH, dbus_name='org.mpris.MediaPlayer2.omxplayer1')
		workState = mp.Queue()
		p1 = mp.Process(target=motionDT, args=(workState,))
		p1.start()
		pid = p1.pid
		sleep(5.0)
		#playBGVideo(VIDEO_FILE_IDLE, 0)
		#lablePrint()
		while(1):
			# if player.playback_status() == "Playing":
			# 	print("one video is playing")
			# 	break
			res1 = workState.get()
			print(res1)
			pause = psutil.Process(pid)
			if res1 == 1:
				# pause = psutil.Process(pid)
				pause.suspend()
				playVideo(VIDEO_FILE_SCANNING, 0)
				# pause.resume()
				q.put(0)
			if res1!=1:
				pause.resume()
				
			sleep(1)
		p1.join()
	except Exception as e:
		print("Program terminated: ",e)
		sys.exit()

if __name__ == '__main__':
	main()	
