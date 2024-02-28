#!/usr/bin/env python3

import rospy
from image_publisher import imPub

camera_path = "/dev/v4l/by-path/platform-fd500000.pcie-pci-0000:01:00.0-usb-0:1.4:1.0-video-index0"
camera_topic = "vision_global"
hz = 10
rotation = 0
try:
    imPub(camera_path,camera_topic,hz,rotation)
except rospy.ROSInterruptException:
    pass