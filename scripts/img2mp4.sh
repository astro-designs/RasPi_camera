
# This command will construct a video file from the images...
avconv -i /home/pi/time-lapse/image_%04d.jpg -r 10  timelapse.avi
