#!/usr/bin/env python3

import rospy
from image_publisher import imPub

camera_path = "/dev/v4l/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.1:1.0-video-index0"
camera_topic = "prelevement"
hz = 9
try:
    imPub(camera_path,camera_topic,hz)
except rospy.ROSInterruptException:
    pass