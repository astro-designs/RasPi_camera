PAGE="""\
<html>
<head>
<title>Raspberry Pi WebCam</title>
</head>
<body>
<center><h1>Raspberry Pi WebCam</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

# Supported resolutions:
# Be sure to set the resolution in the html above to the same resolution
resolution='640x480'
#resolution='800x600'
#resolution='1024x768'
#resolution='1920x1080'
#resolution=1296x972'
#resolution='2592x1944'

framerate=24
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

port = 8005