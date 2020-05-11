#!/bin/bash

echo $1 >> /root/tmptest
/usr/bin/python3 /root/rclone_aria2_upload/uploadbt.py "$@" >> /root/upload.log
