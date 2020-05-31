#!/usr/bin/env python

from time import sleep
import picamera

WAIT_TIME = 5

print('Capturing every ' + str(WAIT_TIME) + ' seconds...')

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    for filename in camera.capture_continuous('/home/pi/timelapse/img{timestamp:%H-%M-%S-%f}.jpg'):
        sleep(WAIT_TIME)
