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

def imPub(camera_path,camera_topic,hz,rotation=0):
    # camera init
    capture = cv2.VideoCapture()
    capture.open(camera_path)
    capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
    if not capture.isOpened():
        print(Fore.RED + 'Pas de camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
    else:
        print(Fore.GREEN + 'Camera disponible : "{}"'.format(camera_path) + Style.RESET_ALL)
    
    # rotation check
    rotationPossibility = [90, -90, 180, -180]
    if rotation in rotationPossibility:
        if rotation == 90:
            rotation = cv2.ROTATE_90_COUNTERCLOCKWISE
            print(Fore.GREEN + '{} Rotation 90°'.format(camera_topic) + Style.RESET_ALL)
        if rotation == -90:
            rotation = cv2.ROTATE_90_CLOCKWISE
            print(Fore.GREEN + '{} Rotation -90°'.format(camera_topic) + Style.RESET_ALL)
        if rotation == 180 or rotation == -180:
            rotation = cv2.ROTATE_180
            print(Fore.GREEN + '{} Rotation 180°'.format(camera_topic) + Style.RESET_ALL)
    else:
        rotation = None
        print(Fore.GREEN + 'Rotation 0°' + Style.RESET_ALL)
            
    
    # publisher init
    bridge = CvBridge()
    pub = rospy.Publisher("/camera/{}".format(camera_topic), Image, queue_size=1)
    rospy.init_node("image_{}".format(camera_topic), anonymous=False)
    rate = rospy.Rate(hz)
    
    while not rospy.is_shutdown():
        try:
            # get and pub image
            _, frame = capture.read()
            if rotation != None:
                frame = cv2.rotate(frame, rotation)
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
    camera_path = "/dev/v4l/by-path/pci-0000:00:06.0-usb-0:3:1.0-video-index0"
    camera_topic = "vision_globale"
    hz = 10
    rotation = 180
    try:
        imPub(camera_path,camera_topic,hz,rotation)
    except rospy.ROSInterruptException:
        pass
    



