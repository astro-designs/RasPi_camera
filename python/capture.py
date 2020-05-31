

from picamera import PiCamera
import time
import RPi.GPIO as GPIO
from ftplib import FTP
import argparse
import camera_conf as conf

parser = argparse.ArgumentParser(description='Raspberry Pi Camera Capture Controller')

parser.add_argument('-Filename', action='store', dest='Filename', default='image',
                    help='Name of file to save')

parser.add_argument('-NumFrames', action='store', dest='NumFrames', default=1,
                    help='Number of frames to capture')

parser.add_argument('-FrameInterval', action='store', dest='FrameInterval', default=1, help='Frame-to-frame timing (s)')
parser.add_argument('-VideoDuration', action='store', dest='VideoDuration', default=10, help='Video recording duration (s)')
parser.add_argument('-Trigger', action='store', dest='Trigger', default='immediate', help='Trigger option (immediate, GPIO, countdown (s), network')
parser.add_argument('-Countdown', action='store', dest='Countdown', default=10, help='Frame trigger countdown (s)')
parser.add_argument('-Caption', action='store', dest='Caption', default='None', help='Caption option (text string)')
parser.add_argument('-Mode', action='store', dest='Mode', default='image', help='Capture image or video')
parser.add_argument('-ftp', action='store', dest='ftp', default='no', help='Specify ftp server to send image(s) over ftp')

# These next arguments are exactly as supported by the raspistill program:
#parser.add_argument('-e', action='store', dest='encoding', default='jpg', help='Encoding to use for output file (jpg, bmp, gif, png')

arguments = parser.parse_args()

# Read arguments...
NumFrames = int(arguments.NumFrames)
FrameInterval = float(arguments.FrameInterval)
VideoDuration = float(arguments.VideoDuration)
Trigger = arguments.Trigger
CountdownToFrame = float(arguments.Countdown)
Caption = arguments.Caption
Mode = arguments.Mode
ftp_image = arguments.ftp
Filename = arguments.Filename
#format = arguments.encoding

# https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/7

# Set the GPIO modes...
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Setup the trigger GPIO...
PreviewTrigger = 2
ImmediateTrigger = 3
StatusLED = 4
GPIO.setup(PreviewTrigger, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(ImmediateTrigger, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(StatusLED, GPIO.OUT)
GPIO.output(StatusLED, False)

# Setup camera...
camera = PiCamera()
camera.rotation = conf.rotation
camera.resolution = conf.resolution
camera.framerate = conf.framerate
camera.format = conf.format
camera.start_preview(alpha = 200)
camera.annotate_text_size = 50
if Caption != "None":
	camera.annotate_text = Caption

# Some misc initialisation...
TimeNow = time.time()
NextCaptureTime = TimeNow
Finished = False

def Capture(PreviewWait = 0, Delay = 0):
	global TimeNow, NextCaptureTime, Filename
	
	if ftp_image == 'yes':
		ftp = FTP(conf.ftp_server)
		ftp.login(user=conf.ftp_user, passwd = conf.ftp_password)
		ftp.cwd(conf.ftp_path)
	   
	TimeNow = time.time()
	NextCaptureTime = TimeNow + Delay

	# Start preview...
	print("Starting preview...")
	camera.start_preview()
	
	for i in range(NumFrames):
		# Start preview...
		#print("Starting preview...")
		#camera.start_preview()

		# Delay for countdown timer or FrameInterval
		StatusLEDFast = False
		while TimeNow < NextCaptureTime:
			print("Waiting...")
			StatusLEDSlow = ((NextCaptureTime - TimeNow) % 2 == 0)
			StatusLEDFast = not StatusLEDFast
			if NextCaptureTime - TimeNow > 1:
				GPIO.output(StatusLED, StatusLEDFast)		
			else:
				GPIO.output(StatusLED, StatusLEDSlow)
			time.sleep(0.1)
			TimeNow = time.time()
		
		# Create filename...	
		TimeNow = time.time()
		TimeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(TimeNow))
		Filename = Filename + "_" + TimeStr + ".jpg"
		Filepath = "../media/" + Filename
		print(Filepath)
		
		# Start preview...
		#print("Starting preview...")
		#camera.start_preview()
		
		# Camera warm-up time
		#print("Warming up...")
		#time.sleep(2)
		
		# Hold preview until trigger released if in PreviewTrigger mode...
		if PreviewWait == 1: # Wait for PreviewTrigger to be released
			while GPIO.input(PreviewTrigger) == False:
				StatusLEDFast = not StatusLEDFast
				GPIO.output(StatusLED, StatusLEDFast)		
				time.sleep(0.1)
		
		# Image capture mode...
		if Mode == 'image':
			GPIO.output(StatusLED, True)		
			print("Capturing image...")
			camera.capture(Filepath)

			# ftp image...
			if ftp_image == 'yes':
				print("Sending file over ftp")
				localfile = open(Filepath, 'rb')
				ftp.storbinary('STOR ' + Filename, localfile)
				ftp.quit()
				localfile.close()
				
		# Video capture mode...
		elif Mode == 'video':
			GPIO.output(StatusLED, True)		
			print("Capturing video...")
			#camera.start_recording('/home/pi/Desktop/video.h264')
			time.sleep(VideoDuration)
			#camera.stop_recording()

		#print("Stopping preview...")
		#camera.stop_preview()	
		GPIO.output(StatusLED, False)
		NextCaptureTime = NextCaptureTime + FrameInterval
		#time.sleep(3)
		
	print("Stopping preview...")
	camera.stop_preview()

def TriggerMonitor():
	global TimeNow, NextCaptureTime, Finished
	
	print("Wating for trigger...")
	
	if Trigger == "GPIO":
		if GPIO.input(ImmediateTrigger) == False: # Note trigger is active-low
			Capture(0,0)
		elif GPIO.input(PreviewTrigger) == False: # Note trigger is active-low
			Capture(1,0)
	
	elif Trigger == "countdown":
		Capture(0, CountdownToFrame)

	elif Trigger == "immediate":
		Capture(0,0)
		Finished = True

	time.sleep(0.1)

try:	
	while Finished == False:
		TriggerMonitor()

except KeyboardInterrupt:
	print("Keyboard Interrupt (ctrl-c) detected - exiting program loop")

finally:
	GPIO.cleanup()
	print("Finished!")

