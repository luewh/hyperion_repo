#! /usr/bin/env python3

import rospy
import moveit_commander
# import moveit_msgs.msg
import sys
import os
import copy
from time import sleep
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
        super().__init__(sleepTime=sleepTime,keyboard=False)

        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node("move_group_hyperion",
                        anonymous=True,
                        log_level=1,
                        disable_rostime=True,
                        disable_rosout=True)

        """Provides information such as the robot’s kinematic 
        model and the robot’s current joint states"""
        self.robot = moveit_commander.RobotCommander()

        """This object is an interface to a planning group of joints"""
        group_name_arm = "scara_arm"
        self.move_group_arm = moveit_commander.MoveGroupCommander(group_name_arm)
        group_name_hand = "scara_hand"
        self.move_group_hand = moveit_commander.MoveGroupCommander(group_name_hand)
        
        self.scale_pos = scale_pos
        self.scale_rotation = scale_rotation
        
        self.echPose = [[3.64,0,-2.09,-1.51,0],
                        [3.29,0,-2.09,-1.17,0],
                        [2.91,0,-1.89,-0.99,0]]
        
        self.stockPose = [[3.65,0,-1.72,-1.73,0],
                          [3.28,0,-1.67,-1.39,0],
                          [2.88,0,-1.45,-1.17,0]]
        
        self.pince_max = 0.8346
        self.degre_ouverture_pince_prev = None
        self.degre_ouverture_pince_prev_prev = None
        
        self.base_max = 6.35
        self.poignet_max = 6.35
        
        self.pose_prev = [None, None, None]
        
    def printRed(self,text, end='\r\n'):
        print("{}{}{}".format('\033[91m',text,'\033[0m'), end=end)
    
    def printGreen(self,text, end='\r\n'):
        print("{}{}{}".format('\033[92m',text,'\033[0m'), end=end)
    
    def printYellow(self,text, end='\r\n'):
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
        self.move_group_arm.go(pickPose[:-1], wait=True)
        
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
            # open pince 2% to release object
            self.handMove([False, 0.02],wait=True,abs=False)
        
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
        pickPose = self.echPose[numberPreleve - 1]
        # init pick thread
        event = Event()
        moveTask = Thread(target=self.pickDropMove, args=(pickPose, 0.07/self.scale_pos, True, event))
        
        # run thread
        moveTask.start()
        # update joystick while preleve number not changed
        # and pick thread not end
        while self.prelevement_1_2_3 == numberPreleve and moveTask.is_alive():
            self.joystickUpdate()
            sleep(self.sleepTime)
        
        # preleve number changed during pick
        if moveTask.is_alive():
            self.printRed("aborted")
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
                sleep(self.sleepTime)
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
            sleep(self.sleepTime)
        
        # preleve number changed during drop
        if dropTask.is_alive():
            self.printRed("aborted")
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
                sleep(self.sleepTime)
            self.printGreen("stock {} done".format(numberStock))
            
    # movement control loop
    def run(self):
        while True:
            try:
                self.joystickUpdate()
                self.poignetMove()
                self.baseMove()
                self.pinceMove()
                pose = [self.effecteur_x_vitesse,self.effecteur_y_vitesse,self.effecteur_z_vitesse]
                self.armMove(pose, wait=False)
                self.pose_prev = pose
                self.preleve()
                self.stock()
                # TODO pub lum cam modePre
                sleep(self.sleepTime)
            except KeyboardInterrupt:
                print("Exiting...")
        

if __name__ == '__main__':
    joystick_moveGroupe = Joystick_MoveGroupe(
        scale_pos=0.2, # max 20cm
        scale_rotation=0.1, # max 1deg
        sleepTime=0.1)
    joystick_moveGroupe.run()





