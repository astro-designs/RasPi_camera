PAGE="""\
<html>
<head>
<title>Raspberry Pi WebCam</title>
</head>
<body>
<center><h1>Raspberry Pi WebCam</h1></center>
<center><img src="stream.mjpg" width="1920" height="1080"></center>
</body>
</html>
"""
# Output filename (can be over-ridden by the -o argument)
Filename = 'output.jpg'

# Number of frames to capture:
NumFrames = 1

# Video duration (seconds)
VideoDuration = 10

# Trigger option
#Trigger = 'immediate'
Trigger = 'GPIO'
#Trigger = 'countdown'

# Countdown option - start capture after the count down delay (seconds)
Countdown = 0

# Capture mode - still image or video
Mode = 'image'
#Mode = 'video'

# FTP option - enables automatic upload to FTP server
ftp = 'no'

# Supported raspistill options
raspistill_o = 'output.jpg'
raspistill_e = 'jpg'

# Supported resolutions:
# Be sure to set the resolution in the html above to the same resolution
#resolution=(640,480)
resolution=(800,600)
#resolution=(1024,768)
#resolution=(1920,1080)
#resolution=(1296,972)
#resolution=(2592,1944) # 5MP sensor resolution
#resolution=(3280,2464) # 8MP sensor resolution
#resolution=(4056,3040) # 12.3MP sensor resolution

# Frame rate
framerate=0.5
#framerate=24
#framerate=48
#framerate=25
#framerate=50
#framerate=29.97
#framerate=59.94
#framerate=30
#framerate=60

# Frame Interval
FrameInterval = 1/framerate

rotation=0
#rotation = 90
#rotation = 180
#rotation = 270

hflip = True
vflip = True

# Image format:
format = 'jpg'
#format = 'bmp'
#format = 'tif' # Not supported?
#format = 'gif'
#format = 'png'

# Video format:
#format = 'mpg'
#format = 'h264'

# Preview mode:
# Supports preview over HDMI (the usual way) or via ethernet as a WebCam server
PreviewMode = 'HDMI'
#PreviewMode = 'Webcam'
#PreviewMode = 'Both'

# Webcam settings...
webcam_port = 8005

# FTP settings...
ftp_server = 'ftp.gridhost.co.uk'
ftp_user = 'ftp@cantrills.com'
ftp_password = 'L0st!nspace'
ftp_path = 'public_html/cameras/media'

#Define the (BCM) pins used for trigger & status...
PreviewPin = 2
CapturePin = 3
StatusPin = 4
ReadyPin = 17

# Add caption to image or video (use 'None' for no caption)
Caption = 'Testing'
