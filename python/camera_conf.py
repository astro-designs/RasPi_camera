# Camera configuration

# ********************************************
# *** General configuration / options:     ***
# ********************************************

# Trigger option
#Trigger = 'immediate'
Trigger = 'GPIO'
#Trigger = 'motion' # Not currently supported

# Define the (BCM) pins used for trigger & status...
PreviewPin = 2
CapturePin = 3
StatusPin = 4
ReadyPin = 17

# Countdown option - start capture after the count down delay (seconds)
Countdown = 0

# Capture mode - still image, video or webcam
Mode = 'image'
#Mode = 'video'
#Mode = 'webcam'

# Supported resolutions:
# All versions of the Raspberry Pi camera are supported here but some resolutions are only supported on some versions of the camera
#resolution=(640,480)
resolution=(800,600)
#resolution=(1024,768)
#resolution=(1920,1080)
#resolution=(1296,972)
#resolution=(2592,1944) # 5MP sensor resolution
#resolution=(3280,2464) # 8MP sensor resolution
#resolution=(4056,3040) # 12.3MP sensor resolution

# Frame rate
#framerate=0.1
#framerate=24
#framerate=48
framerate=25
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

# Add caption to image or video (use 'None' for no caption)
Caption = str(resolution[0]) + "x" + str(resolution[1])

# Control shutter speed
# 0 = automatic
shutter_speed = 0

# Control exposure time
# 0 = automatic
iso = 0

# Control the exposure mode (see PiCamera documentation)
exposure_mode = 'sports'

# Image effects
image_effect = 'none'
image_effect_params = 'none'

# Preview mode:
# Supports preview over HDMI (the usual way) or via ethernet as a WebCam server
PreviewMode = 'HDMI'
#PreviewMode = 'Webcam'
#PreviewMode = 'Both'


# ********************************************
# *** Still / single-shot capture options: ***
# ********************************************

# Number of frames to capture:
NumFrames = 1

# Output filename and path
Filename = 'output.jpg'
Filepath = '../media/'

# Image format:
format = 'jpeg'
#format = 'bmp'
#format = 'tif' # Not supported?
#format = 'gif'
#format = 'png'


# ********************************************
# *** Video capture options:               ***
# ********************************************

# Video duration (seconds)
VideoDuration = 10

# Video format:
#format = 'mpg'
#format = 'h264'


# ********************************************
# *** FTP settings                         ***
# ********************************************
ftp = 'no'
ftp_server = 'ftp.gridhost.co.uk'
ftp_user = 'ftp@cantrills.com'
ftp_password = '**********'
ftp_path = 'public_html/cameras/media'


# ********************************************
# *** Webcam settings                      ***
# ********************************************
webcam_port = 8005

# Webcam page
PAGE="""\
<html>
<head>
<title>Raspberry Pi WebCam</title>
</head>
<body>
<center><h1>Raspberry Pi WebCam</h1></center>
<center><img src="stream.mjpg" width=\"""" + str(resolution[0]) + '\" ' + " height=\"" + str(resolution[1]) + '\"' + """></center>
</body>
</html>
"""
