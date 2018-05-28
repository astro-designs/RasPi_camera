#!/bin/sh
USERNAME=ftp@cantrills.com
PASSWORD=L0st!nspace
SERVER=ftp.gridhost.co.uk
 
# local directory to pickup *.tar.gz file
FTPFILE="cam.jpg"
 
# remote server directory to upload backup
FTPDIR="public_html/cameras/pigeon_cam"
 
cd /home/pi
 
# Take a picture
raspistill -o cam.jpg
 
# login to remote server
ftp -n -i $SERVER <<EOF
user $USERNAME $PASSWORD
cd $FTPDIR
mput $FTPFILE
quit
EOF
