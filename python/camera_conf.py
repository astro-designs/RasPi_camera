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

# Supported resolutions:
# Be sure to set the resolution in the html above to the same resolution
#resolution=(640,480)
#resolution=(800,600)
#resolution=(1024,768)
#resolution=(1920,1080)
#resolution=(1296,972)
#resolution=(2592,1944) # 5MP sensor resolution
#resolution=(3280,2464) # 8MP sensor resolution
resolution=(4056,3040) # 12.3MP sensor resolution

framerate=1
#framerate=24
#framerate=48
#framerate=25
#framerate=50
#framerate=29.97
#framerate=59.94
#framerate=30
#framerate=60

#rotation=0
rotation = 90
#rotation = 180
#rotation = 270

# Image format:
format = jpg
#format = bmp
#format = tif # Not supported?
#format = gif
#format = png

# Webcam settings...
webcam_port = 8005

# FTP settings...
ftp_server = 'ftp.gridhost.co.uk'
ftp_user = 'ftp@cantrills.com'
ftp_password = 'L0st!nspace'
ftp_path = 'public_html/cameras/media'
