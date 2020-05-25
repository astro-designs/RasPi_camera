from os import system

print('Converting *.jpg to gif...')

FRAME_INTERVAL = 5

system('convert -delay 500 -loop 1 /home/pi/timelapse/img*.jpg animation.gif')

print('Done')
