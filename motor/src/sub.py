#!/usr/bin/env python
import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Float64

def joint_states_callback(message):
    print("---")
    print(message.position)
    return

if __name__ == '__main__':
    rospy.init_node("sub_joint_example")
    rospy.Subscriber("joint_states", JointState, joint_states_callback, queue_size=1)
    rospy.spin()