# Un-comment this section to stream to YouTube...
date >> /home/pi/cam_VGA.log
echo 'Taking picture & uploading to ftp server' >> /home/pi/cam_VGA.log
/home/pi/ftp_pic.sh
echo 'Starting Camera' >> /home/pi/cam_VGA.log
raspivid -o - -t 0 -rot 0 -w 640 -h 480 -fps 25 -b 1200000 -p 0,0,640,480 -g 50 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://x.rtmp.youtube.com/live2/m77r-kcg6-wzye-fufv &

# Uncomment this section to chose option to run motion sensing camera

# Uncomment this section to chose option to run time-lapse camera
#python /home/pi/timelapse.py

