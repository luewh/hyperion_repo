#! /usr/bin/env python3
# roslaunch moveit_test_sysmap_collision demo.launch

from euler_quaternion import euler_to_quaternion, quaternion_to_euler

from math import pi, dist, fabs, cos
tau = 2*pi
 
import rospy
import moveit_commander
import moveit_msgs.msg
import geometry_msgs.msg
import sys
import copy

moveit_commander.roscpp_initialize(sys.argv)
rospy.init_node("move_group_python_interface_tutorial", anonymous=True)

"""Provides information such as the robot’s kinematic 
model and the robot’s current joint states"""
robot = moveit_commander.RobotCommander()

"""This provides a remote interface for getting, setting, and updating
the robot’s internal understanding of the surrounding world"""
scene = moveit_commander.PlanningSceneInterface()

"""This object is an interface to a planning group of joints"""
group_name = "scara_arm"
move_group = moveit_commander.MoveGroupCommander(group_name)

"""Create a DisplayTrajectory ROS publisher which is used
to display trajectories in Rviz:"""
display_trajectory_publisher = rospy.Publisher(
    "/move_group/display_planned_path",
    moveit_msgs.msg.DisplayTrajectory,
    queue_size=20,
)

# # We can get the name of the reference frame for this robot:
# planning_frame = move_group.get_planning_frame()
# print("============ Planning frame: %s" % planning_frame)

# # We can also print the name of the end-effector link for this group:
# eef_link = move_group.get_end_effector_link()
# print("============ End effector link: %s" % eef_link)

# # We can get a list of all the groups in the robot:
# group_names = robot.get_group_names()
# print("============ Available Planning Groups:", robot.get_group_names())

# # Sometimes for debugging it is useful to print the entire state of the robot:
# print("============ Printing robot state")
# print(robot.get_current_state())

joint_goal = move_group.get_current_joint_values()
print(joint_goal)
joint_goal = [0]*5
move_group.go(joint_goal, wait=True)
move_group.stop()

# pose_goal = geometry_msgs.msg.Pose()
# pose_goal.position.x = 0
# pose_goal.position.y = 0
# pose_goal.position.z = 0
# qx,qy,qz,qw = euler_to_quaternion(0,0,0)
# pose_goal.orientation.x = qx
# pose_goal.orientation.y = qy
# pose_goal.orientation.z = qz
# pose_goal.orientation.w = qw

# # pose_goal = move_group.get_current_pose().pose
# print(pose_goal)

# move_group.set_pose_target(pose_goal)
# success = move_group.go(wait=True)
# move_group.stop()
# move_group.clear_pose_targets()



# waypoints = []
# scale = 1.0

wpose = move_group.get_current_pose().pose
print(wpose)
# wpose.position.z += scale * 0.1  # First move up (z)
# wpose.position.y += scale * 0.2  # and sideways (y)
# waypoints.append(copy.deepcopy(wpose))

# wpose.position.x += scale * 0.1  # Second move forward/backwards in (x)
# waypoints.append(copy.deepcopy(wpose))

# wpose.position.y -= scale * 0.1  # Third move sideways (y)
# waypoints.append(copy.deepcopy(wpose))

# (plan, fraction) = move_group.compute_cartesian_path(
#     waypoints, 0.01, 0.0  # waypoints to follow  # eef_step
# )  # jump_threshold
# # print(plan, fraction)


# display_trajectory = moveit_msgs.msg.DisplayTrajectory()
# display_trajectory.trajectory_start = robot.get_current_state()
# display_trajectory.trajectory.append(plan)
# # Publish
# display_trajectory_publisher.publish(display_trajectory)

# print("0000")
# move_group.execute(plan, wait=True)






