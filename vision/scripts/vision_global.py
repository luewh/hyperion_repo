#!/usr/bin/env python3

import rospy
from image_publisher import imPub

camera_path = "/dev/v4l/by-path/platform-bcm2835-codex-video-index0"
camera_topic = "vision_globale"
hz = 10
try:
    imPub(camera_path,camera_topic,hz)
except rospy.ROSInterruptException:
    pass