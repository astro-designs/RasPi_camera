#!/usr/bin/env python

from picamera import PiCamera
import time
import RPi.GPIO as GPIO
from ftplib import FTP
import argparse
import camera_conf as conf

parser = argparse.ArgumentParser(description='Raspberry Pi Camera Capture Controller')

parser.add_argument('-Filename', action='store', dest='Filename', default='output.jpg',
                    help='Name of file to save')

parser.add_argument('-NumFrames', action='store', dest='NumFrames', default=1,
                    help='Number of frames to capture')

parser.add_argument('-FrameInterval', action='store', dest='FrameInterval', default=1, help='Frame-to-frame timing (s)')
parser.add_argument('-VideoDuration', action='store', dest='VideoDuration', default=10, help='Video recording duration (s)')
parser.add_argument('-Trigger', action='store', dest='Trigger', default='immediate', help='Trigger option (immediate, GPIO, countdown (s), network')
parser.add_argument('-Countdown', action='store', dest='Countdown', default=0, help='Frame trigger countdown (s)')
parser.add_argument('-Caption', action='store', dest='Caption', default='None', help='Caption option (text string)')
parser.add_argument('-Mode', action='store', dest='Mode', default='image', help='Capture image or video')
parser.add_argument('-ftp', action='store', dest='ftp', default='no', help='Use -ftp yes to send image(s) over ftp')

# These next arguments are exactly as supported by the raspistill program:
parser.add_argument('-o', action='store', dest='Filename', default='output.jpg', help='Output file')
parser.add_argument('-e', action='store', dest='encoding', default='jpg', help='Encoding to use for output file (jpg, bmp, gif, png')

arguments = parser.parse_args()

# Read arguments...
NumFrames = int(arguments.NumFrames)
FrameInterval = float(arguments.FrameInterval)
VideoDuration = float(arguments.VideoDuration)
CountdownToFrame = float(arguments.Countdown)
Caption = arguments.Caption
Mode = arguments.Mode
ftp_image = arguments.ftp

# Use filename from configuration file unless argument is not the default value
if arguments.Filename != 'output.jpg':
	Filename = arguments.Filename
else:
	Filename = conf.Filename

# Use Trigger from configuration file unless argument is not the default value
if arguments.Trigger != 'immediate':
	Trigger = arguments.Trigger
else:
	Trigger = conf.Trigger

# Use Format from configuration file unless argument is not the default value
if arguments.encoding != 'jpg':
	Format = arguments.encoding
else:
	Format = conf.format
	
# Set the GPIO modes...
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Setup the trigger GPIO...
PreviewPin = conf.PreviewPin
CapturePin = conf.CapturePin
StatusPin = conf.StatusPin
ReadyPin = conf.ReadyPin

GPIO.setup(PreviewPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CapturePin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(StatusPin, GPIO.OUT)
GPIO.setup(ReadyPin, GPIO.OUT)
GPIO.output(StatusPin, False)
GPIO.output(ReadyPin, False)

# Setup camera...
camera = PiCamera()
camera.rotation = conf.rotation
camera.resolution = conf.resolution
camera.framerate = conf.framerate
camera.annotate_text_size = 50

if arguments.Caption != 'None':
	camera.annotate_text = arguments.Caption
elif conf.Caption != 'None':
	camera.annotate_text = conf.Caption


# Set filename extension based on selected image format
x = Filename.split('.')
File_name = x[0]
File_ext = Format

# Some misc initialisation...
TimeNow = time.time()
NextCaptureTime = TimeNow
Finished = False
PreviewActive = False
StatusPinFast = False

def Capture(Delay = 0):
	global TimeNow, NextCaptureTime, File_name, File_ext, PreviewActive
	
	if ftp_image == 'yes':
		ftp = FTP(conf.ftp_server)
		ftp.login(user=conf.ftp_user, passwd = conf.ftp_password)
		ftp.cwd(conf.ftp_path)
	   
	TimeNow = time.time()
	NextCaptureTime = TimeNow + Delay

	# Start preview...
	if PreviewActive == False:
		#print("Starting preview...")
		camera.start_preview()
	
	for i in range(NumFrames):

		# Delay for countdown timer or FrameInterval
		StatusPinFast = False
		while TimeNow < NextCaptureTime:
			#print("Waiting...")
			StatusPinSlow = ((NextCaptureTime - TimeNow) % 2 < 1)
			StatusPinFast = not StatusPinFast
			if NextCaptureTime - TimeNow < 1:
				GPIO.output(StatusPin, StatusPinFast)		
			else:
				GPIO.output(StatusPin, StatusPinSlow)
			time.sleep(0.1)
			TimeNow = time.time()
		
		# Create filename...	
		TimeNow = time.time()
		TimeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(TimeNow))
		Filename = File_name + "_" + TimeStr + '.' + File_ext
		Filepath = "../media/" + Filename
				
		# Image capture mode...
		if Format == 'jpg' or Format == 'bmp' or Format == 'gif' or Format == 'png':
			GPIO.output(StatusPin, True)		
			print("Capturing image...")
			if Format == 'jpg':
				camera.capture(Filepath, 'jpeg')
			else:
				camera.capture(Filepath, Format)
			print("Captured!")

		# Video capture mode...
		elif Format == 'mjpeg' or Format == 'h264':
			GPIO.output(StatusPin, True)		
			print("Capturing video...")
			if Format == 'mjpeg':
				camera.start_recording(Filepath, 'mjpeg')
			else:
				camera.start_recording(Filepath, 'h264')
			time.sleep(VideoDuration)
			camera.stop_recording()
			print("Captured!")

		GPIO.output(StatusPin, False)
		NextCaptureTime = NextCaptureTime + FrameInterval

		# ftp image...
		if ftp_image == 'yes':
			print("Sending file over ftp")
			localfile = open(Filepath, 'rb')
			ftp.storbinary('STOR ' + Filename, localfile)
			ftp.quit()
			localfile.close()
						
	if PreviewActive == False:
		#print("Stopping preview...")
		camera.stop_preview()

def TriggerMonitor():
	global TimeNow, NextCaptureTime, Finished, PreviewActive, StatusPinFast
	
	GPIO.output(ReadyPin, True)
	#print("Waiting for trigger...")
	
	if Trigger == "GPIO":
		if GPIO.input(CapturePin) == False: # Note trigger is active-low
			GPIO.output(ReadyPin, False)
			Capture(CountdownToFrame)
		elif GPIO.input(PreviewPin) == False and PreviewActive == False: # Note trigger is active-low
			# Start preview...
			#print("Starting preview...")
			camera.start_preview()
			PreviewActive = True
		elif GPIO.input(PreviewPin) == True and PreviewActive == True: # Note trigger is active-low
			# Stop preview...
			#print("Stopping preview...")
			camera.stop_preview()
			PreviewActive = False
	
	elif Trigger == "countdown":
		GPIO.output(ReadyPin, False)
		Capture(CountdownToFrame)

	elif Trigger == "immediate":
		GPIO.output(ReadyPin, False)
		Capture(CountdownToFrame)
		Finished = True
		
	TimeNow = time.time()
	StatusPinFast = not StatusPinFast
	if PreviewActive:
		GPIO.output(StatusPin, StatusPinFast)
	else:
		GPIO.output(StatusPin, False)
	
	time.sleep(0.1)

try:	
	while Finished == False:
		TriggerMonitor()

except KeyboardInterrupt:
	print("Keyboard Interrupt (ctrl-c) detected - exiting program loop")

finally:
	GPIO.cleanup()
	print("Finished!")

