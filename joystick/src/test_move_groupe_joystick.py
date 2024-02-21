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
        
        self.stockPose = [[3.69,0,-1.72,-1.73,0],
                          [3.30,0,-1.68,-1.37,0],
                          [2.87,0,-1.41,-1.20,0]]
        
        self.degre_ouverture_pince_max = 0.8346
        self.degre_ouverture_pince_prev = None
        self.degre_ouverture_pince_prev_prev = None
        
    def printRed(self,text):
        print("{}{}{}".format('\033[93m',text,'\033[0m'))
    
    def armMove (self,pose,wait=False):
        if pose == [0,0,0]:
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
            0.001,       # eef_step
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
            print("please wait...",end="\r")
            self.move_group_hand.go(verin_value, wait=True)
            # colonne down verin length
            colonne_value[1] -= 0.15
            self.move_group_arm.go(colonne_value, wait=True)
            print("done")
            
        # if colonne at bottom and verin not at bottom
        if (colonne_value[1] + self.scale_pos * pose[2] < -0.285) and (round(verin_value[0],2) != -0.15):
            # TODO pub verin action
            self.move_group_arm.stop()
            # colonne up verin length
            colonne_value[1] += 0.15
            print("please wait...",end="\r")
            self.move_group_arm.go(colonne_value, wait=True)
            # verin got to bottom
            verin_value[0] = -0.15
            self.move_group_hand.go(verin_value, wait=True)
            print("done")
            
    def poignetMove(self):
        if self.rotation_pince_vitesse != 0:
            self.move_group_arm.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[-1] += self.rotation_pince_vitesse * self.scale_rotation
            self.move_group_arm.go(current_joints, wait=True)
        
    def baseMove(self):
        if self.rotation_base_vitesse != 0:
            self.move_group_arm.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[0] += self.rotation_base_vitesse * self.scale_rotation
            self.move_group_arm.go(current_joints, wait=True)
    
    def pinceMove(self):
        if (self.degre_ouverture_pince_prev_prev != self.degre_ouverture_pince_prev
            and self.degre_ouverture_pince_prev == self.degre_ouverture_pince):
            joint_to_go = [False, self.degre_ouverture_pince*self.degre_ouverture_pince_max]
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
        
        if pick:
            # TODO open pince
            print("open pince")
        else:
            # no action needed
            pass
        
        if event.is_set():
            return
        # arm down cartesian
        self.armMove([0,0,-pickDist],wait=True)
        # pose = self.move_group_arm.get_current_pose().pose
        # pose.position.z -= pickDist
        # (plan, fraction) = self.move_group_arm.compute_cartesian_path([pose], 0.05, 0, avoid_collisions=True)
        # self.move_group_arm.execute(plan, wait=True)
        
        if pick:
            # TODO close pince
            print("close pince")
        else:
            # TODO open pince
            print("open pince")
        
        if event.is_set():
            return
        # arm up cartesian
        self.armMove([0,0,pickDist],wait=True)
        # pose = self.move_group_arm.get_current_pose().pose
        # pose.position.z += pickDist
        # (plan, fraction) = self.move_group_arm.compute_cartesian_path([pose], 0.05, 0, avoid_collisions=True)
        # self.move_group_arm.execute(plan, wait=True)
        
    def preleve(self):
        if self.prelevement_1_2_3 == 0:
            return
        
        event = Event()
        pickPose = self.echPose[self.prelevement_1_2_3 - 1]
        moveTask = Thread(target=self.pickDropMove, args=(pickPose, 0.05, True, event))
        
        moveTask.start()
        while self.prelevement_1_2_3 != 0 and moveTask.is_alive():
            self.joystickUpdate()
            sleep(self.sleepTime)
            
        if moveTask.is_alive():
            print("aborted")
            event.set()  
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[1] = 0
            self.move_group_arm.go(current_joints, wait=True)
        else:
            print("finished")
            duration = 1
            freq = 440
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            sleep(1)
    
    def stock(self):
        if self.macro_stockage_1_2_3 == 0:
            return
        
        event = Event()
        dropPose = self.stockPose[self.macro_stockage_1_2_3 - 1]
        moveTask = Thread(target=self.pickDropMove, args=(dropPose, 0.1, False, event))
        
        moveTask.start()
        while self.macro_stockage_1_2_3 != 0 and moveTask.is_alive():
            self.joystickUpdate()
            sleep(self.sleepTime)
            
        if moveTask.is_alive():
            print("aborted")
            event.set()  
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            current_joints = self.move_group_arm.get_current_joint_values()
            current_joints[1] = 0
            self.move_group_arm.go(current_joints, wait=True)
        else:
            print("finished")
            duration = 1
            freq = 440
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
            sleep(1)
            
    # movement control loop
    def run(self):
        while True:
            try:
                self.joystickUpdate()
                self.poignetMove()
                self.baseMove()
                self.pinceMove()
                pose = [self.effecteur_x_vitesse,self.effecteur_y_vitesse,self.effecteur_z_vitesse]
                self.armMove(pose)
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





