#!/usr/bin/env python3

import rospy
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
# from openCV_utils import *
from colorama import Fore, Style

import os
os.environ['OPENCV_LOG_LEVEL'] = "SILENT"
os.environ['GST_DEBUG'] = "0"

def imPub(camera_path,camera_topic,hz):
    # camera init
    capture = cv2.VideoCapture()
    capture.open(camera_path)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    if not capture.isOpened():
        print(Fore.RED + 'Pas de camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
    else:
        print(Fore.GREEN + 'Camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
    
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
                print(Fore.RED + 'Pas de camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
                rospy.Rate(0.5).sleep()
            else:
                print(Fore.GREEN + 'Camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
            
    capture.release()


if __name__ == '__main__':
    # integrated camera on vmBox
    camera_path = "/dev/v4l/by-path/pci-0000:00:06.0-usb-0:2:1.0-video-index0"
    camera_topic = "vision_globale"
    hz = 10
    try:
        imPub(camera_path,camera_topic,hz)
    except rospy.ROSInterruptException:
        pass
    



