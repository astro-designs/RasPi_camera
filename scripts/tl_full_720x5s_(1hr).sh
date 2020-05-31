# This command will take a photo every 5s for 1 hour...
# Resolution = full
raspistill -o ../media/image_%04d.jpg -tl 5000 -t 3600000

# This command will construct a video file from the images...
avconv -r 10 -i ../media/image_%04d.jpg -r 10 -vcodec libx264 -crf 20 -g 15 timelapse.mp4
