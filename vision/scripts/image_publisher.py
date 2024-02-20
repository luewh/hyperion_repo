#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from openCV_utils import *

import os
os.environ['OPENCV_LOG_LEVEL'] = "SILENT"
os.environ['GST_DEBUG'] = "0"

def imPub(camera_path,camera_topic,hz):
    # camera init
    if camera_topic == "vision_globale":
        capture = cv2.VideoCapture(0)
    else:
        capture = cv2.VideoCapture()
        capture.open(camera_path)
    if not capture.isOpened():
        print('Pas de camera disponible : "{}"'.format(camera_path))
    else:
        print('Camera disponible : "{}"'.format(camera_path))
    
    # publisher init
    bridge = CvBridge()
    pub = rospy.Publisher("/camera/{}".format(camera_topic), Image, queue_size=1)
    rospy.init_node("image_{}".format(camera_topic), anonymous=False)
    rate = rospy.Rate(hz)
    
    while not rospy.is_shutdown():
        try:
            # get and pub image
            _, frame = capture.read()
            msg = bridge.cv2_to_imgmsg(frame, "bgr8")
            pub.publish(msg)
            rate.sleep()
        except:
            # camera re-init
            capture.open(camera_path)
            if not capture.isOpened():
                print('Pas de camera disponible : "{}"'.format(camera_path))
                rospy.Rate(0.5).sleep()
            else:
                print('Camera disponible : "{}"'.format(camera_path))
            
    capture.release()


if __name__ == '__main__':
    camera_path = "/dev/v4l/by-path/pci-0000:00:06.0-usb-0:2:1.0-video-index0"
    camera_topic = "vision_globale"
    hz = 10
    try:
        imPub(camera_path,camera_topic,hz)
    except rospy.ROSInterruptException:
        pass
    



