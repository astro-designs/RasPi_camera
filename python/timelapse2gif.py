from os import system

system('convert -delay 10 -loop 0 /home/pi/time-lapse/img*.jpg animation.gif')
print('done')
