raspivid -o - -t 0 -rot 0 -w 1280 -h 720 -fps 8 -g 50 | ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero -f h264 -i - -vcodec copy -acodec aac -ab 128k -g 50 -strict experimental -f flv rtmp://x.rtmp.youtube.com/live2/m77r-kcg6-wzye-fufv

