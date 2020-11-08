#!/usr/bin/env python

import picamera
import io
import time
import RPi.GPIO as GPIO
from ftplib import FTP
import argparse
import socketserver
from threading import Condition
from http import server
import camera_conf as conf
import logging

#debug_sts = 0
#def print_sts():
#    global debug_sts
#    print(debug_sts)
#    debug_sts = debug_sts + 1

#print_sts()

parser = argparse.ArgumentParser(description='Raspberry Pi Camera Capture Controller')

parser.add_argument('-NumFrames', action='store', dest='NumFrames', default=conf.NumFrames, help='Number of frames to capture')
parser.add_argument('-FrameInterval', action='store', dest='FrameInterval', default=conf.FrameInterval, help='Frame-to-frame timing (s)')
parser.add_argument('-VideoDuration', action='store', dest='VideoDuration', default=conf.VideoDuration, help='Video recording duration (s)')
parser.add_argument('-Trigger', action='store', dest='Trigger', default=conf.Trigger, help='Trigger option (immediate, GPIO, countdown (s), network')
parser.add_argument('-Countdown', action='store', dest='Countdown', default=conf.Countdown, help='Frame trigger countdown (s)')
parser.add_argument('-Caption', action='store', dest='Caption', default=conf.Caption, help='Caption option (text string)')
parser.add_argument('-Mode', action='store', dest='Mode', default=conf.Mode, help='Capture image or video')
parser.add_argument('-ftp', action='store', dest='ftp', default=conf.ftp, help='Use -ftp enabled to send image(s) over ftp')
parser.add_argument('-Filename', action='store', dest='Filename', default=conf.Filename, help='Output file')
parser.add_argument('-Format', action='store', dest='Format', default=conf.format, help='Encoding to use for output file (jpeg, bmp, gif, png')

arguments = parser.parse_args()

# Read arguments...
NumFrames = int(arguments.NumFrames)
FrameInterval = float(arguments.FrameInterval)
VideoDuration = float(arguments.VideoDuration)
CountdownToFrame = float(arguments.Countdown)
Caption = arguments.Caption
Mode = arguments.Mode
ftp_image = arguments.ftp
Format = arguments.Format
Filename = arguments.Filename
Trigger = arguments.Trigger

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

# Webcam
# Based on Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

PAGE=conf.PAGE

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def Webcam():
    global camera, output, server, WebCamPreviewActive
    #camera = picamera.PiCamera()
    if WebCamPreviewActive == False:
        #with camera:
        output = StreamingOutput()
        WebCamPreviewActive = True
        camera.start_recording(output, format='mjpeg')
        #try:
        address = ('', conf.webcam_port)
        if server == 0:
            server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
        #finally:
        #camera.stop_recording()

# Setup camera...
camera = picamera.PiCamera()

camera.rotation = conf.rotation
camera.hflip = conf.hflip
camera.vflip = conf.vflip
camera.resolution = conf.resolution
camera.framerate = conf.framerate
camera.annotate_text_size = 50
camera.shutter_speed = conf.shutter_speed
camera.iso = conf.iso
camera.exposure_mode = conf.exposure_mode
camera.image_effect = conf.image_effect
if conf.image_effect != 'none':
	camera.image_effect_params = conf.image_effect_params

if conf.Caption != 'None':
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
WebCamPreviewActive = False
StatusPinFast = False
server = 0

def Capture():
	global TimeNow, NextCaptureTime, File_name, File_ext, PreviewActive, WebCamPreviewActive, CountdownToFrame

	if ftp_image == 'enabled':
		ftp = FTP(conf.ftp_server)
		ftp.login(user=conf.ftp_user, passwd = conf.ftp_password)
		ftp.cwd(conf.ftp_path)

	TimeNow = time.time()
	NextCaptureTime = TimeNow + CountdownToFrame

	# Stop WebCam preview...
	if WebCamPreviewActive == True:
		print("Stopping WebCam preview...")
		camera.stop_recording()
		time.sleep(0.1)
		WebCamPreviewActive = False

	# Start preview...
	if PreviewActive == False:
		print("Starting preview...")
		camera.start_preview()

	# Create filename...
	TimeNow = time.time()
	TimeStr = time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime(TimeNow))
	# Add time & data to filename
	Filename = File_name + "_" + TimeStr
	Filename = Filename + '_{counter:04d}.' + File_ext
	Filepath = conf.Filepath + Filename

	# Delay for countdown timer
	print(NextCaptureTime)
	StatusPinFast = False
	while TimeNow < NextCaptureTime:
		print(round(NextCaptureTime - TimeNow,1))
		StatusPinSlow = ((NextCaptureTime - TimeNow) % 2 < 1)
		StatusPinFast = not StatusPinFast
		if NextCaptureTime - TimeNow < 1:
			GPIO.output(StatusPin, StatusPinFast)
		else:
			GPIO.output(StatusPin, StatusPinSlow)
		time.sleep(0.1)
		TimeNow = time.time()

	# Image capture mode...
	if Format == 'jpeg' or Format == 'bmp' or Format == 'gif' or Format == 'png':
		GPIO.output(StatusPin, True)
		print("Capturing...")
		for i, filename in enumerate(camera.capture_continuous(Filepath, format=Format)):
			print("Captured!", i+1)
			print(filename)
			time.sleep(FrameInterval)
			if i >= NumFrames-1:
				break
			else:
				# Delay for FrameInterval
				while TimeNow <= NextCaptureTime:
					print("Waiting...")
					time.sleep(0.1)
					TimeNow = time.time()
				NextCaptureTime = NextCaptureTime + FrameInterval
				print(NextCaptureTime)

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

	# ftp image...
	if ftp_image == 'yes':
		print("Sending file over ftp")
		localfile = open(Filepath, 'rb')
		ftp.storbinary('STOR ' + Filename, localfile)
		ftp.quit()
		localfile.close()

	if PreviewActive == False:
		print("Stopping preview...")
		camera.stop_preview()

def PreviewCallback(channel):
	global WebCamPreviewActive, server
	if GPIO.input(PreviewPin) == False:
		print("Preview: Falling-edge interrupt detected")
	else:
		print("Preview: Rising-edge interrupt detected")
	if WebCamPreviewActive == True:
		print("Stopping WebCam preview...")
		camera.stop_recording()
		WebCamPreviewActive = False
		server.shutdown()

def CaptureCallback(channel):
	global WebCamPreviewActive, server

	#if GPIO.input(CapturePin) == False:
	#print("Capture: Falling-edge interrupt detected")
	if WebCamPreviewActive == True:
		print("Stopping WebCam preview...")
		camera.stop_recording()
		WebCamPreviewActive = False
		server.shutdown()
	#else:
	#	print("Capture: Rising-edge interrupt detected")


def TriggerMonitor():
	global TimeNow, NextCaptureTime, Finished, PreviewActive, WebCamPreviewActive, StatusPinFast

	if Trigger == "GPIO":
		# Start capture if Capture GPIO is asserted
		if GPIO.input(CapturePin) == False: # Note trigger is active-low
			print("Starting Capture...")
			GPIO.output(ReadyPin, False)
			Capture()
			GPIO.output(ReadyPin, True)
			print("Ready!")
		# Start preview if Preview GPIO is asserted
		elif GPIO.input(PreviewPin) == False: # Note trigger is active-low
			# Preview to HDMI screen
			if conf.PreviewMode == 'HDMI' and PreviewActive == False:
				print("Starting Preview...")
				camera.start_preview()
				PreviewActive = True
			# Preview to webcam
			elif conf.PreviewMode == 'Webcam' and WebCamPreviewActive == False:
				print("Starting WebCam Preview...")
				Webcam()
				print("WebCam closed")
		# Stop preview if Preview GPIO is de-asserted
		elif GPIO.input(PreviewPin) == True and PreviewActive == True: # Note trigger is active-low
			print("Stopping preview...")
			camera.stop_preview()
			PreviewActive = False

	elif Trigger == "immediate":
		GPIO.output(ReadyPin, False)
		Capture()
		GPIO.output(ReadyPin, True)
		print("Ready!")
		Finished = True

	TimeNow = time.time()
	StatusPinFast = not StatusPinFast
	if PreviewActive:
		GPIO.output(StatusPin, StatusPinFast)
	else:
		GPIO.output(StatusPin, False)

	time.sleep(0.1)

# Setup interrupt to monitor Preview Pin
#GPIO.add_event_detect(PreviewPin, GPIO.RISING, callback=PreviewCallback, bouncetime=100)

# Setup interrupt to monitor Capture Pin
GPIO.add_event_detect(CapturePin, GPIO.FALLING, callback=CaptureCallback, bouncetime=100)

try:
	print("Universal Camera Controller for Raspberry Pi Camera")
	GPIO.output(ReadyPin, True)
	print("Ready!")

	while Finished == False:
		TriggerMonitor()

except KeyboardInterrupt:
	print("Keyboard Interrupt (ctrl-c) detected - exiting program loop")

finally:
	if WebCamPreviewActive == True:
		print("Stopping WebCam preview...")
		camera.stop_recording()
		WebCamPreviewActive = False
		server.shutdown()
	GPIO.cleanup()
	print("Finished!")

