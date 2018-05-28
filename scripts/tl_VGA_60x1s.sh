raspistill -h 640 -w 480 -vf -t 60000 -tl 1000 -o tl_$1_%04d.jpg
avconv -r 10 -i tl_$1_%04d.jpg -r 10 -vcodec libx264 -crf 20 -g 15 tl_$1.mp4

