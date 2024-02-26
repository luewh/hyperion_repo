#! /usr/bin/env python3

import rospy
import moveit_commander

from std_msgs.msg import Bool
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Quaternion, Pose, Point

import sys
import copy
import math
# from time import sleep
from threading import Thread, Event

from joystick import Joystick
from euler_quaternion import euler_to_quaternion, quaternion_to_euler

import logging
logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

class Joystick_MoveGroupe (Joystick):
    def __init__(self,
                 scale_pos=1.0,
                 scale_rotation=1.0,
                 sleepTime=0.1) -> None:
        
        # init joystick
        super().__init__(sleepTime=sleepTime,keyboard=False)

        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node("move_group_hyperion",
                        anonymous=False,
                        log_level=1,
                        disable_rostime=True,
                        disable_rosout=True)
        
        self.rate = rospy.Rate(1/self.sleepTime)

        self.robot = moveit_commander.RobotCommander()
        
        group_name_arm = "scara_arm"
        self.move_group_arm = moveit_commander.MoveGroupCommander(group_name_arm)
        self.move_group_arm.go([0,0,0,0], wait=True)
        
        group_name_hand = "scara_hand"
        self.move_group_hand = moveit_commander.MoveGroupCommander(group_name_hand)
        self.move_group_hand.go([0,0], wait=True)
        
        self.scale_pos = scale_pos
        self.scale_rotation = scale_rotation
        
        self.prelevPose = [[2.75,0,4.65,3.10],
                           [2.44,0,4.64,2.80],
                           [2.04,0,4.44,2.60]]
        
        self.stockPose = [[2.01,0,4.01,3.51],
                          [2.44,0,4.22,3.73],
                          [2.79,0,4.24,4.06]]
        
        self.pince_max = 0.8346
        self.degre_ouverture_pince_prev = None
        self.degre_ouverture_pince_prev_prev = None
        
        self.base_max = 6.35
        self.poignet_max = 6.35
        
        self.pose_prev = [None, None, None]
        
        # home init
        self.macro_position_zero_prev = None
        self.homeDone = None
        self.home_pub = rospy.Publisher('/home', Bool, queue_size=1)
        rospy.Subscriber('/home', Bool, self.homeCallback)
        
        # tcp init
        tcp_marker_points_lenght = 10
        self.tcp_pub = rospy.Publisher('/tcp', Marker, queue_size = tcp_marker_points_lenght)
        self.tcp_marker = Marker()
        self.tcp_marker.header.frame_id = "world"
        self.tcp_marker.type = Marker.POINTS
        self.tcp_marker.action = Marker.ADD
        self.tcp_marker.lifetime = rospy.Duration(0)
        self.tcp_marker.color.a = 0.8
        self.tcp_marker.color.b = 1.0
        self.tcp_marker.scale.x = 0.01
        self.tcp_marker.scale.y = 0.01
        self.tcp_marker.scale.z = 0.01
        self.tcp_marker.pose.orientation = Quaternion(0,0,0,1)
        self.tcp_marker.points = [Point(0,0,0)]*tcp_marker_points_lenght
        # tcp run thread
        tcpTask = Thread(target=self.tcpUpdate)
        tcpTask.start()
        
        
    def printRed(self,text, end='\r\n'):
        print(" "*120, end='\r')
        print("{}{}{}".format('\033[91m',text,'\033[0m'), end=end)
    
    def printGreen(self,text, end='\r\n'):
        print(" "*120, end='\r')
        print("{}{}{}".format('\033[92m',text,'\033[0m'), end=end)
    
    def printYellow(self,text, end='\r\n'):
        print(" "*120, end='\r')
        print("{}{}{}".format('\033[93m',text,'\033[0m'), end=end)
    
    def armMove (self,pose,wait=False):
        if pose == [0,0,0]:
            if self.pose_prev != [0,0,0]:
                self.move_group_arm.stop()
            return
        
        self.move_group_arm.stop()
        waypoints = []
        wpose = self.move_group_arm.get_current_pose().pose
        wpose.position.x += self.scale_pos * pose[0]
        wpose.position.y += self.scale_pos * pose[1]
        wpose.position.z += self.scale_pos * pose[2]
        waypoints.append(copy.deepcopy(wpose))
        
        (plan, fraction) = self.move_group_arm.compute_cartesian_path(
            waypoints,  # waypoints to follow 
            0.005,       # eef_step
            0,      # jump_threshold
            avoid_collisions=True)
        self.move_group_arm.execute(plan, wait=wait)
        
        colonne_value = self.move_group_arm.get_current_joint_values()
        verin_value = self.move_group_hand.get_current_joint_values()
        # if colonne at top and verin not at top
        if (colonne_value[1] + self.scale_pos * pose[2] > 0) and (round(verin_value[0],2) != 0):
            # TODO pub verin action
            self.move_group_arm.stop()
            # verin got to top
            verin_value[0] = 0
            self.printYellow("please wait...")
            self.move_group_hand.go(verin_value, wait=True)
            # colonne down verin length
            colonne_value[1] -= 0.15
            self.move_group_arm.go(colonne_value, wait=True)
            self.printGreen("verin in done")
            
        # if colonne at bottom and verin not at bottom
        if (colonne_value[1] + self.scale_pos * pose[2] < -0.285) and (round(verin_value[0],2) != -0.15):
            # TODO pub verin action
            self.move_group_arm.stop()
            # colonne up verin length
            colonne_value[1] += 0.15
            self.printYellow("please wait...")
            self.move_group_arm.go(colonne_value, wait=True)
            # verin got to bottom
            verin_value[0] = -0.15
            self.move_group_hand.go(verin_value, wait=True)
            self.printGreen("verin out done")
        
    def poignetMove(self):
        if self.rotation_pince_vitesse != 0:
            self.move_group_arm.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[-1] += self.rotation_pince_vitesse * self.scale_rotation
            # limit min
            if current_joints[-1] < 0:
                current_joints[-1] = 0
                self.printYellow("poignet min", end='\r')
            # limit max
            if current_joints[-1] > self.poignet_max:
                current_joints[-1] = self.poignet_max
                self.printYellow("poignet max", end='\r')
            self.move_group_arm.go(current_joints, wait=True)
        
    def baseMove(self):
        if self.rotation_base_vitesse != 0:
            self.move_group_arm.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[0] += self.rotation_base_vitesse * self.scale_rotation
            # limit min
            if current_joints[0] < 0:
                current_joints[0] = 0
                self.printYellow("base min", end='\r')
            # limit max
            if current_joints[0] > self.base_max:
                current_joints[0] = self.base_max
                self.printYellow("base max", end='\r')
            self.move_group_arm.go(current_joints, wait=True)
    
    def pinceMove(self):
        # TODO go with collision
        if (self.degre_ouverture_pince_prev_prev != self.degre_ouverture_pince_prev
            and self.degre_ouverture_pince_prev == self.degre_ouverture_pince):
            joint_to_go = [False, self.degre_ouverture_pince*self.pince_max]
            self.handMove(joint_to_go, wait=True, abs=True)
            
        self.degre_ouverture_pince_prev_prev = self.degre_ouverture_pince_prev
        self.degre_ouverture_pince_prev = self.degre_ouverture_pince
    
    def handMove(self,joints,wait=False,abs=True):
        current_joints = self.move_group_hand.get_current_joint_values()
        # joint assert
        if len(current_joints) != len(joints):
            self.printRed("Wrong length")
            return
        # stop hand move
        self.move_group_hand.stop()
        # get joint goal
        for index in range(len(joints)):
            if type(joints[index]) != bool:
                if abs:
                    current_joints[index] = joints[index]
                else:
                    current_joints[index] += joints[index]
        # limit min
        if current_joints[1] < 0:
            current_joints[1] = 0
            self.printYellow("pince min", end='\r')
        # limit max
        if current_joints[1] > self.pince_max:
            current_joints[1] = self.pince_max
            self.printYellow("pince max", end='\r')
        # execute
        self.move_group_hand.go(current_joints, wait=wait)
    
    def pickDropMove(self, pickPose, pickDist, pick: bool, event: Event):
        self.move_group_arm.stop()
        self.move_group_hand.stop()
        
        if event.is_set():
            return
        # verin go top
        self.handMove([0, False],wait=True,abs=True)
        
        if event.is_set():
            return
        # arm go prelevement pose
        self.move_group_arm.go(pickPose, wait=True)
        
        if event.is_set():
            return
        if pick:
            # open pince at 22%
            self.handMove([False, 0.22],wait=True,abs=True)
        else:
            # no action needed
            pass
        
        if event.is_set():
            return
        # arm down cartesian
        self.armMove([0,0,-pickDist],wait=True)
        
        if pick:
            # close pince
            self.handMove([False, 0],wait=True,abs=True)
        else:
            # open pince 5% to release object
            self.handMove([False, 0.05],wait=True,abs=False)
        
        if event.is_set():
            return
        # arm up cartesian
        self.armMove([0,0,pickDist],wait=True)
        
    def preleve(self):
        if self.prelevement_1_2_3 == 0:
            return
        
        # check gripper to be closed
        current_joints = self.move_group_hand.get_current_joint_values()
        if current_joints[1] > 0.1:
            self.printRed("please close the gripper", end="\r")
            return
        
        # remember preleve number
        numberPreleve = self.prelevement_1_2_3
        # get preleve position
        pickPose = self.prelevPose[numberPreleve - 1]
        # init pick thread
        event = Event()
        moveTask = Thread(target=self.pickDropMove, args=(pickPose, 0.07/self.scale_pos, True, event))
        
        # run thread
        moveTask.start()
        # update joystick while preleve number not changed
        # and pick thread not end
        while self.prelevement_1_2_3 == numberPreleve and moveTask.is_alive():
            self.joystickUpdate()
            self.rate.sleep()
        
        # preleve number changed during pick
        if moveTask.is_alive():
            self.printRed("aborted preleve {}".format(numberPreleve))
            # end thread
            event.set()  
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            # set at current joint position
            current_joints = self.move_group_arm.get_current_joint_values()
            self.move_group_arm.go(current_joints, wait=True)
        # pick drop thread end properly
        else:
            self.printYellow("finished, please release the button...", end="\r")
            # wait till preleve button released
            while self.prelevement_1_2_3 != 0:
                self.joystickUpdate()
                self.rate.sleep()
            self.printGreen("preleve {} done".format(numberPreleve))
    
    def stock(self):
        if self.macro_stockage_1_2_3 == 0:
            return
        
        # remember stock number
        numberStock = self.macro_stockage_1_2_3
        # get stock position
        dropPose = self.stockPose[numberStock - 1]
        # init drop thread
        event = Event()
        dropTask = Thread(target=self.pickDropMove, args=(dropPose, 0.1/self.scale_pos, False, event))
        
        # run thread
        dropTask.start()
        # update joystick while stock number not changed
        # and drop thread not end
        while self.macro_stockage_1_2_3 == numberStock and dropTask.is_alive():
            self.joystickUpdate()
            self.rate.sleep()
        
        # preleve number changed during drop
        if dropTask.is_alive():
            self.printRed("aborted stock {}".format(numberStock))
            # end thread
            event.set()  
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            # set at current joint position
            current_joints = self.move_group_arm.get_current_joint_values()
            self.move_group_arm.go(current_joints, wait=True)
        # pick drop thread end properly
        else:
            self.printYellow("finished, please release the button...", end="\r")
            # wait till preleve button released
            while self.macro_stockage_1_2_3 != 0:
                self.joystickUpdate()
                self.rate.sleep()
            self.printGreen("stock {} done".format(numberStock))
    
    def home(self):
        if self.macro_position_zero and not self.macro_position_zero_prev:
            # tell physical scara to go home
            self.home_pub.publish(True)
            # scara arm and hand go home
            self.move_group_arm.go([0,0,0,0], wait=True)
            self.move_group_hand.go([0,0], wait=True)
            
            # waiting physical scara home done
            self.homeDone = False
            while not self.homeDone:
                self.printYellow("Waiting physical home to be done...", end='\r')
                self.rate.sleep()
            
        self.macro_position_zero_prev = self.macro_position_zero
            
    def homeCallback(self, home):
        if not home.data:
            self.printGreen("Physical home done")
            self.homeDone = True
    
    def tcpUpdate(self):
        while True:
            verinPos, doigtAngles = self.move_group_hand.get_current_joint_values()
            doigtAngles -= 0.40387
            toolCenterPoint = self.move_group_arm.get_current_pose().pose.position
            toolCenterPoint.z += -0.085 -0.025 -0.072 -math.cos(doigtAngles)*0.11509 +verinPos
            self.tcp_marker.points = self.tcp_marker.points[1:] + [toolCenterPoint]
            self.tcp_pub.publish(self.tcp_marker)
            self.rate.sleep()
            
    # movement control loop
    def run(self):
        while True:
            try:
                self.joystickUpdate()
                # joint movement, wait=True
                self.poignetMove()
                self.baseMove()
                self.pinceMove()
                # arm movement, wait=False
                pose = [self.effecteur_x_vitesse,self.effecteur_y_vitesse,self.effecteur_z_vitesse]
                self.armMove(pose, wait=False)
                self.pose_prev = pose
                # macro movement, wait=True
                self.preleve()
                self.stock()
                self.home()
                
                # TODO pub lum cam modePre
                self.rate.sleep()
            except KeyboardInterrupt:
                self.printRed("Exiting...")
        

if __name__ == '__main__':
    
    joystick_moveGroupe = Joystick_MoveGroupe(
        scale_pos=0.2, # max 20cm
        scale_rotation=0.1, # max 1deg
        sleepTime=0.1)
    
    joystick_moveGroupe.run()





