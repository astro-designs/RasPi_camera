

from picamera import PiCamera
import time
import RPi.GPIO as GPIO
import argparse

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

arguments = parser.parse_args()

# Read arguments...
NumFrames = int(arguments.NumFrames)
FrameInterval = float(arguments.FrameInterval)
VideoDuration = float(arguments.VideoDuration)
Trigger = arguments.Trigger
CountdownToFrame = float(arguments.Countdown)
Caption = arguments.Caption
Mode = arguments.Mode
Filename = arguments.Filename

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
camera.rotation = 0
camera.resolution = (1920, 1080)
camera.framerate = 15
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
	
	TimeNow = time.time()
	NextCaptureTime = TimeNow + Delay
	#camera.start_preview()
	
	for i in range(NumFrames):
		camera.start_preview()

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
		TimeStr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(TimeNow))
		Filepath = "../media/" + Filename + "_" + TimeStr + ".jpg"
		print(Filepath)
		
		# Hold preview until trigger released if in PreviewTrigger mode...
		if PreviewWait == 1: # Wait for PreviewTrigger to be released
			while GPIO.input(PreviewTrigger) == 1:
				time.sleep(0.1)
		
		# Image capture mode...
		if Mode == 'image':
			print("Capturing image...")
			camera.capture(Filepath)
			#camera.capture('/home/pi/Desktop/image%s.jpg' % i)
		
		# Video capture mode...
		elif Mode == 'video':
			print("Capturing video...")
			#camera.start_recording('/home/pi/Desktop/video.h264')
			time.sleep(VideoDuration)
			#camera.stop_recording()

		camera.stop_preview()	
		GPIO.output(StatusLED, False)
		NextCaptureTime = NextCaptureTime + FrameInterval
		time.sleep(3)

	#camera.stop_preview()

def TriggerMonitor():
	global TimeNow, NextCaptureTime, Finished
	
	if Trigger == "GPIO":
		TimeNow = time.time()
		StatusLEDSlow = (TimeNow % 2 == 0)
		if GPIO.input(ImmediateTrigger) == False: # Note trigger is active-low
			GPIO.output(StatusLED, True)
			Capture(0,0)
		elif GPIO.input(PreviewTrigger) == False: # Note trigger is active-low
			Capture(1,0)
	
	elif Trigger == "countdown":
		if NextCaptureTime - TimeNow > 1:
			GPIO.output(StatusLED, StatusLEDFast)		
		else:
			GPIO.output(StatusLED, StatusLEDSlow)
		GPIO.output(StatusLED, True)
		Capture(0, CountdownToFrame)

	elif Trigger == "immediate":
		GPIO.output(StatusLED, True)
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

