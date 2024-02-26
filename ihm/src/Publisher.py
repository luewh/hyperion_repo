#!/usr/bin/env python3
import rospy
from std_msgs.msg import String,Int16,Float32
from geometry_msgs.msg import Twist
import time


def turtleTurn():    
    rospy.init_node('turtleturn')
    pub = rospy.Publisher('/IHM/LogsDefauts/LogDefaut', String, queue_size = 10)
    rate = rospy.Rate(1) #hz
    i = 0
    while not rospy.is_shutdown():
		#PUBLISH MESSAGE
        message = str("blabla")  #int(1) #float(25.055)
        
        pub.publish(message)
        
        print("le message est " + str(message))
        
        rate.sleep()

        if i > 1 :
            break
        else:
            i = i +1


if __name__ == '__main__':
   turtleTurn() #our main function
