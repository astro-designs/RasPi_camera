from time import sleep
import picamera
from os import system

with picamera.PiCamera() as camera:
  camera.resolution = (1024, 768)


WAIT_TIME = 1

with picamera.PiCamera() as camera:
    camera.resolution = (1024, 768)
    for filename in camera.capture_continuous('/home/pi/time-lapse/img{timestamp:%H-%M-%S-%f}.jpg'):
        sleep(WAIT_TIME)
