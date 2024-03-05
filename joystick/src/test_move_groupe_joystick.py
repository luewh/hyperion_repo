#! /usr/bin/env python3

import rospy
import moveit_commander
import geometry_msgs.msg

from std_msgs.msg import Bool, Int8
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Quaternion, Point

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
        self.scene = moveit_commander.PlanningSceneInterface()
        
        group_name_arm = "scara_arm"
        self.move_group_arm = moveit_commander.MoveGroupCommander(group_name_arm)
        # self.printYellow("Doing home...", end='\r')
        # self.move_group_arm.go([0,0,0,0], wait=True)
        
        group_name_hand = "scara_hand"
        self.move_group_hand = moveit_commander.MoveGroupCommander(group_name_hand)
        # self.move_group_hand.go([0,0], wait=True)
        # self.printGreen("home done")
        
        self.scale_pos = scale_pos
        self.scale_rotation = scale_rotation
        
        self.prelevFrottisPose = [[2.33, 0, 4.53, 2.73],
                                  [1.97, 0, 4.45, 2.86],
                                  [2.01, 0, 4.30, 3.14]]
        
        self.prelevLiquidePose = [[2.20, 0, 4.41, 3.67],
                                  [1.88, 0, 4.39, 1.34],
                                  [1.92, 0, 4.24, 2.23]]
        
        self.prelevPoussierePose = [2.33,0,4.53,2.73]
        
        self.stockPose = [[2.00,0,3.90,3.49],
                          [2.39,0,4.10,3.89],
                          [2.80,0,4.12,4.05]]
        
        self.pince_max = 0.8346
        self.degre_ouverture_pince_prev = None
        self.degre_ouverture_pince_prev_prev = None
        self.base_max = 6.35
        self.poignet_max = 6.35
        
        self.poseCommand_prev = [None, None, None]
        
        # # home init
        # self.macro_position_zero_prev = None
        # self.homeDone = None
        # self.home_pub = rospy.Publisher('/home', Bool, queue_size=1, latch=True)
        # rospy.Subscriber('/home', Bool, self.homeCallback)
        
        # tcp init
        tcp_marker_points_lenght = 10
        self.tcp_pub = rospy.Publisher('/tcp', Marker, queue_size = tcp_marker_points_lenght, latch=True)
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
        
        # init liquide
        self.liqude_pub = rospy.Publisher('/liquide', Int8, queue_size=1, latch=True)
        self.liqude_pub.publish(0)
        
        # init preleve mode
        self.modification_mode_index_prev = self.modification_mode_index
        self.preleveMode_pub = rospy.Publisher('IHM/prelevement/PrelevSelectAct', Int8, queue_size=1, latch=True)
        self.preleveMode_pub.publish(self.modification_mode_index+1)
        
        # init preleve etat
        # ["poussière","solide","liquide","frottis"]
        # 1 = "Boite vide",
        # 2 = "Outil équipé",
        # 3 = "Stockage en cours",
        # 4 = "Prélèvement fini",
        # 5 = "Défaut"]
        self.preleveEtat1 = [0]*4
        self.preleveEtat1_prev = [None]*4
        self.preleveEtat2 = [0]*4
        self.preleveEtat2_prev = [None]*4
        self.preleveEtat3 = [0]*4
        self.preleveEtat3_prev = [None]*4
        self.preleveEtat1_pub = rospy.Publisher('IHM/prelevement/PrelevEtat1', Int8, queue_size=1, latch=True)
        self.preleveEtat2_pub = rospy.Publisher('IHM/prelevement/PrelevEtat2', Int8, queue_size=1, latch=True)
        self.preleveEtat3_pub = rospy.Publisher('IHM/prelevement/PrelevEtat3', Int8, queue_size=1, latch=True)
        self.preleveEtat1_pub.publish(0)
        self.preleveEtat2_pub.publish(0)
        self.preleveEtat3_pub.publish(0)
        
        # plateau init
        self.poseStampedFrottis = geometry_msgs.msg.PoseStamped()
        self.poseStampedFrottis.header.frame_id = "electrique"
        self.poseStampedFrottis.pose.orientation.x = 0.7068
        self.poseStampedFrottis.pose.orientation.w = 0.7074
        self.poseStamped = copy.deepcopy(self.poseStampedFrottis)
        self.poseStamped.pose.position = Point(-0.037,-0.005,0.0625)
        self.meshPath = __file__.replace("/joystick/src/test_move_groupe_joystick.py","/klampt/meshes/")
        self.scene.remove_world_object("poussière_plateau")
        self.scene.remove_world_object("liquide_plateau")
        self.scene.remove_world_object("frottis_plateau")
        
        
    def printRed(self,text, end='\r\n'):
        # print(" "*120, end='\r')
        print("{}{}{}".format('\033[91m',text,'\033[0m'), end=end)
    
    def printGreen(self,text, end='\r\n'):
        # print(" "*120, end='\r')
        print("{}{}{}".format('\033[92m',text,'\033[0m'), end=end)
    
    def printYellow(self,text, end='\r\n'):
        # print(" "*120, end='\r')
        print("{}{}{}".format('\033[93m',text,'\033[0m'), end=end)
    
    def armMove(self,poseCommand,wait=False,collision=True):
        if poseCommand == [0,0,0]:
            if self.poseCommand_prev != [0,0,0]:
                self.move_group_arm.stop()
            return
        
        # combine position
        self.move_group_arm.stop()
        waypoints = []
        wpose = self.move_group_arm.get_current_pose().pose
        wpose.position.x += self.scale_pos * poseCommand[0]
        wpose.position.y += self.scale_pos * poseCommand[1]
        wpose.position.z += self.scale_pos * poseCommand[2]
        waypoints.append(copy.deepcopy(wpose))
        # compute plan
        (plan, fraction) = self.move_group_arm.compute_cartesian_path(
            waypoints,  # waypoints to follow 
            0.001,       # eef_step
            0,      # jump_threshold
            avoid_collisions=collision)
        # check singularity
        points = plan.joint_trajectory.points
        singularity = False
        thresholdSingularity  = 0.2
        for pointIndex in range(len(points)-1):
            for jointIndex in range(4):
                diff = abs(points[pointIndex].positions[jointIndex] - points[pointIndex+1].positions[jointIndex])
                if diff > thresholdSingularity:
                    singularity = True
                    break
        # execute plan
        if singularity:
            self.printRed("singularity")
        else:
            self.move_group_arm.execute(plan, wait=wait)
        
        colonne_value = self.move_group_arm.get_current_joint_values()
        verin_value = self.move_group_hand.get_current_joint_values()
        # if colonne at top and verin not at top
        if (colonne_value[1] + self.scale_pos * poseCommand[2] > 0) and (round(verin_value[0],2) != 0):
            # TODO pub verin action
            self.move_group_arm.stop()
            # verin got to top
            verin_value[0] = 0
            self.printYellow("Please wait...",end='\r')
            self.move_group_hand.go(verin_value, wait=True)
            # colonne down verin length
            colonne_value[1] -= 0.15
            self.move_group_arm.go(colonne_value, wait=True)
            self.printGreen("verin in done")
            
        # if colonne at bottom and verin not at bottom
        if (colonne_value[1] + self.scale_pos * poseCommand[2] < -0.2789) and (round(verin_value[0],2) != -0.15):
            # TODO pub verin action
            self.move_group_arm.stop()
            # colonne up verin length
            colonne_value[1] += 0.15
            self.printYellow("Please wait...",end='\r')
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
            self.printRed("Wrong length for self.handMove()")
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
        # arm go pick/drop pose
        self.move_group_arm.go(pickPose, wait=True)
        
        if event.is_set():
            return
        if pick:
            # open pince at 15%
            self.handMove([False, 0.15],wait=True,abs=True)
        else:
            # no action needed
            pass
        
        if event.is_set():
            return
        # arm down cartesian
        self.armMove([0,0,-pickDist],wait=True)
        
        if event.is_set():
            return
        if pick:
            # close pince
            self.handMove([False, 0],wait=True,abs=True)
        else:
            self.handMove([False, 0.15],wait=True,abs=False)
        
        if event.is_set():
            return
        # arm up cartesian
        self.armMove([0,0,pickDist],wait=True,collision=False)
        
        if event.is_set():
            return
        if not pick:
            # close pince
            self.handMove([False, 0],wait=True,abs=True)
            
    def preleveFrottisLiquide(self, preleveMode):
        if self.prelevement_1_2_3 == 0:
            return
        
        # check gripper to be closed
        current_joints = self.move_group_hand.get_current_joint_values()
        if current_joints[1] > 0.1:
            self.printRed("please close the gripper", end="\r")
            return
        
        # remember preleve number
        numberPreleve = self.prelevement_1_2_3
        
        pickLiquide = True
        # get preleve position
        if preleveMode == "frottis":
            pickPose = self.prelevFrottisPose[numberPreleve - 1]
        elif preleveMode == "liquide":
            if numberPreleve == 1 and self.preleveEtat1[self.modification_mode_index] == 1:
                pickLiquide = False
            if numberPreleve == 2 and self.preleveEtat2[self.modification_mode_index] == 1:
                pickLiquide = False
            if numberPreleve == 3 and self.preleveEtat3[self.modification_mode_index] == 1:
                pickLiquide = False
            pickPose = self.prelevLiquidePose[numberPreleve - 1]
            
        # init thread
        event = Event()
        moveTask = Thread(target=self.pickDropMove,
                          args=(pickPose, 0.106/self.scale_pos, pickLiquide, event))
        
        # run thread
        moveTask.start()
        self.printGreen("commencer prise d'outil {} {}".format(numberPreleve,preleveMode))
        # update joystick while preleve number not changed and thread not end
        while self.prelevement_1_2_3 == numberPreleve and moveTask.is_alive():
            self.joystickUpdate()
            self.rate.sleep()
        
        # preleve number changed during pick
        if moveTask.is_alive():
            self.printRed("Aborted preleve {}".format(numberPreleve))
            # end thread
            event.set()
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            # set at current joint position
            current_joints = self.move_group_arm.get_current_joint_values()
            self.move_group_arm.go(current_joints, wait=True)
        # thread end properly
        else:
            # update frottis or liquide preleve state to "Outil équipé"
            if numberPreleve == 1:
                self.preleveEtat1[self.modification_mode_index] = int(pickLiquide)
                self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            if numberPreleve == 2:
                self.preleveEtat2[self.modification_mode_index] = int(pickLiquide)
                self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            if numberPreleve == 3:
                self.preleveEtat3[self.modification_mode_index] = int(pickLiquide)
                self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
            self.printYellow("Finished, please release the button...")
            # wait till preleve button released
            while self.prelevement_1_2_3 != 0:
                self.joystickUpdate()
                self.rate.sleep()
            self.printGreen("preleve {} done".format(numberPreleve))
    
    def prelevePoussiere(self):
        if self.prelevement_1_2_3 == 0:
            return
        
        # check gripper to be closed
        current_joints = self.move_group_hand.get_current_joint_values()
        if current_joints[1] > 0.1:
            self.printRed("please close the gripper", end="\r")
            return
        
        
        # init thread
        event = Event()
        moveTask = Thread(target=self.pickDropMove,
                          args=(self.prelevPoussierePose, 0.09/self.scale_pos, True, event))
        
        # run thread
        moveTask.start()
        # update joystick while preleve number not changed and thread not end
        while self.prelevement_1_2_3 != 0 and moveTask.is_alive():
            self.joystickUpdate()
            self.rate.sleep()
        
        # preleve number changed during pick
        if moveTask.is_alive():
            self.printRed("Aborted preleve poussière")
            # end thread
            event.set()
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            # set at current joint position
            current_joints = self.move_group_arm.get_current_joint_values()
            self.move_group_arm.go(current_joints, wait=True)
        # thread end properly
        else:
            # update poussière preleve state to "Outil équipé"
            self.preleveEtat1[self.modification_mode_index] = 1
            self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            self.preleveEtat2[self.modification_mode_index] = 1
            self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            self.preleveEtat3[self.modification_mode_index] = 1
            self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
            self.printYellow("Finished, please release the button...")
            # wait till preleve button released
            while self.prelevement_1_2_3 != 0:
                self.joystickUpdate()
                self.rate.sleep()
            self.printGreen("preleve poussière done")
    
    def stockSolideFrottis(self):
        if self.macro_stockage_1_2_3 == 0:
            return
        
        # remember stock number
        numberStock = self.macro_stockage_1_2_3
        
        # update preleve etat
        if numberStock == 1 and self.preleveEtat1[self.modification_mode_index] != 3:
            self.preleveEtat1[self.modification_mode_index] = 2
            self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            
        if numberStock == 2 and self.preleveEtat2[self.modification_mode_index] != 3:
            self.preleveEtat2[self.modification_mode_index] = 2
            self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            
        if numberStock == 3 and self.preleveEtat3[self.modification_mode_index] != 3:
            self.preleveEtat3[self.modification_mode_index] = 2
            self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
        
        # get stock position
        dropPose = self.stockPose[numberStock - 1]
        # init drop thread
        event = Event()
        dropTask = Thread(target=self.pickDropMove,
                          args=(dropPose, 0, False, event))
        
        # run thread
        dropTask.start()
        # update joystick while stock number not changed
        # and drop thread not end
        while self.macro_stockage_1_2_3 == numberStock and dropTask.is_alive():
            self.joystickUpdate()
            self.rate.sleep()
        
        # preleve number changed during drop
        if dropTask.is_alive():
            self.printRed("Aborted stock {}".format(numberStock))
            # end thread
            event.set()  
            self.move_group_arm.stop()
            self.move_group_hand.stop()
            # set at current joint position
            current_joints = self.move_group_arm.get_current_joint_values()
            self.move_group_arm.go(current_joints, wait=True)
            
            # update preleve etat
            if numberStock == 1 and self.preleveEtat1[self.modification_mode_index] != 3:
                self.preleveEtat1[self.modification_mode_index] = 1
                self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
                
            if numberStock == 2 and self.preleveEtat2[self.modification_mode_index] != 3:
                self.preleveEtat2[self.modification_mode_index] = 1
                self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
                
            if numberStock == 3 and self.preleveEtat3[self.modification_mode_index] != 3:
                self.preleveEtat3[self.modification_mode_index] = 1
                self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
                
        # pick drop thread end properly
        else:
            # update preleve etat
            if numberStock == 1:
                self.preleveEtat1[self.modification_mode_index] = 3
                self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
                
            if numberStock == 2:
                self.preleveEtat2[self.modification_mode_index] = 3
                self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
                
            if numberStock == 3:
                self.preleveEtat3[self.modification_mode_index] = 3
                self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
                
            self.printYellow("Finished, please release the button...")
            # wait till preleve button released
            while self.macro_stockage_1_2_3 != 0:
                self.joystickUpdate()
                self.rate.sleep()
            self.printGreen("stock {} done".format(numberStock))
    
    def stockPoussiere(self):
        pass
    
    def stockLiquide(self):
        if self.macro_stockage_1_2_3 == 0:
            return
        
        # remember liquide number
        numberLiquide = self.macro_stockage_1_2_3
        # if outil équipé
        
        # update liquide preleve state to "Stockage en cours"
        if numberLiquide == 1:
            if self.preleveEtat1[self.modification_mode_index] != 1:
                self.printRed("Equipez l'outil {} pour faire du prélèvement liquide".format(numberLiquide))
                return
            self.preleveEtat1[self.modification_mode_index] = 2
            self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            
        if numberLiquide == 2:
            if self.preleveEtat2[self.modification_mode_index] != 1:
                self.printRed("Equipez l'outil {} pour faire du prélèvement liquide".format(numberLiquide))
                return
            self.preleveEtat2[self.modification_mode_index] = 2
            self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            
        if numberLiquide == 3:
            if self.preleveEtat3[self.modification_mode_index] != 1:
                self.printRed("Equipez l'outil {} pour faire du prélèvement liquide".format(numberLiquide))
                return
            self.preleveEtat3[self.modification_mode_index] = 2
            self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
        
        # start pump
        self.liqude_pub.publish(numberLiquide)
        self.printGreen("pump {} start".format(numberLiquide))
        # update joystick while liquide number not changed
        while self.macro_stockage_1_2_3 == numberLiquide:
            self.joystickUpdate()
            self.rate.sleep()
        # stop pump
        self.liqude_pub.publish(0)
        self.printYellow("pump {} stop".format(numberLiquide))
        
        # update liquide preleve state to "Outil équipé"
        if numberLiquide == 1:
            self.preleveEtat1[self.modification_mode_index] = 1
            self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            
        if numberLiquide == 2:
            self.preleveEtat2[self.modification_mode_index] = 1
            self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            
        if numberLiquide == 3:
            self.preleveEtat3[self.modification_mode_index] = 1
            self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
            
    
    # def home(self):
    #     if self.macro_position_zero and not self.macro_position_zero_prev:
    #         # tell physical scara to go home
    #         self.home_pub.publish(True)
    #         # scara arm and hand go home
    #         self.move_group_arm.go([0,0,0,0], wait=True)
    #         self.move_group_hand.go([0,0], wait=True)
            
    #         # waiting physical scara home done
    #         self.homeDone = False
    #         while not self.homeDone:
    #             self.printYellow("Waiting physical home to be done...", end='\r')
    #             self.rate.sleep()
            
    #     self.macro_position_zero_prev = self.macro_position_zero
            
    # def homeCallback(self, home):
    #     if not home.data:
    #         self.printGreen("physical home done")
    #         self.homeDone = True
    
    def tcpUpdate(self):
        while not rospy.is_shutdown():
            try:
                verinPos, doigtAngles = self.move_group_hand.get_current_joint_values()
                doigtAngles -= 0.40387
                toolCenterPoint = self.move_group_arm.get_current_pose().pose.position
                toolCenterPoint.z += -0.049 -0.025 -0.072 -math.cos(doigtAngles)*0.11509 +verinPos
                self.tcp_marker.points = self.tcp_marker.points[1:] + [toolCenterPoint]
                self.tcp_pub.publish(self.tcp_marker)
                self.rate.sleep()
            except:
                pass
        self.printGreen("\ntcp exit")
    
    def preleveModeUpdate(self,preleveMode):
        if self.modification_mode_index != self.modification_mode_index_prev:
            self.preleveMode_pub.publish(self.modification_mode_index+1)
            
            # pub and update corresponding preleve state
            self.preleveEtat1_pub.publish(self.preleveEtat1[self.modification_mode_index])
            self.preleveEtat1_prev[self.modification_mode_index] = self.preleveEtat1[self.modification_mode_index]
            self.preleveEtat2_pub.publish(self.preleveEtat2[self.modification_mode_index])
            self.preleveEtat2_prev[self.modification_mode_index] = self.preleveEtat2[self.modification_mode_index]
            self.preleveEtat3_pub.publish(self.preleveEtat3[self.modification_mode_index])
            self.preleveEtat3_prev[self.modification_mode_index] = self.preleveEtat3[self.modification_mode_index]
            
            # change plateau
            if preleveMode == "poussière":
                self.printGreen("adding poussière plateau")
                self.scene.add_mesh("poussière_plateau", self.poseStamped,
                                    self.meshPath+"5_ZoneElec_plateau_poussiere.stl")
            elif preleveMode == "liquide":
                self.printGreen("adding liquide plateau")
                self.scene.add_mesh("liquide_plateau", self.poseStamped,
                                    self.meshPath+"5_ZoneElec_plateau_liquide_optimized.stl")
            elif preleveMode == "frottis":
                self.printGreen("adding frottis plateau")
                self.scene.add_mesh("frottis_plateau", self.poseStampedFrottis,
                                    self.meshPath+"5_ZoneElec_plateau_frottis_optimized.stl")
            
            if self.modification_mode_list[self.modification_mode_index_prev] == "poussière":
                self.scene.remove_world_object("poussière_plateau")
            elif self.modification_mode_list[self.modification_mode_index_prev] == "liquide":
                self.scene.remove_world_object("liquide_plateau")
            elif self.modification_mode_list[self.modification_mode_index_prev] == "frottis":
                self.scene.remove_world_object("frottis_plateau")
                
            self.modification_mode_index_prev = self.modification_mode_index
    
    def frottisMacroThread(self, event):
        self.move_group_arm.stop()
        self.move_group_hand.stop()
        
        # TODO orientation
        
        if event.is_set():
            return
        # go top left
        self.armMove([0.063/self.scale_pos,0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # down
        self.armMove([-0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # right
        self.armMove([0,-0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # up
        self.armMove([0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # right
        self.armMove([0,-0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # down
        self.armMove([-0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # go center
        self.armMove([0.063/self.scale_pos,0.048/self.scale_pos,0],wait=True,collision=True)
        
        
        # second round
        if event.is_set():
            return
        # go top left
        self.armMove([0.063/self.scale_pos,0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # down
        self.armMove([-0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # right
        self.armMove([0,-0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # up
        self.armMove([0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # right
        self.armMove([0,-0.048/self.scale_pos,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # down
        self.armMove([-0.126/self.scale_pos,0,0],wait=True,collision=True)
        
        if event.is_set():
            return
        # go center
        self.armMove([0.063/self.scale_pos,0.048/self.scale_pos,0],wait=True,collision=True)

    def macroFrottis(self):
        if self.macro_frotti_poussière:
            
            # init frottis macro thread
            event = Event()
            moveTask = Thread(target=self.frottisMacroThread, args=(event,))
            
            # run thread
            moveTask.start()
            # update joystick while macro button still pressed
            # and frottis macro thread not end
            while self.macro_frotti_poussière and moveTask.is_alive():
                self.joystickUpdate()
                self.rate.sleep()
                
            # macro button changed during pick
            if moveTask.is_alive():
                self.printRed("Aborted preleve macro frottis")
                # end thread
                event.set()
                self.move_group_arm.stop()
                self.move_group_hand.stop()
                # set at current joint position
                current_joints = self.move_group_arm.get_current_joint_values()
                self.move_group_arm.go(current_joints, wait=True)
            # frottis macro thread end properly
            else:
                self.printYellow("Finished, please release the button...")
                # wait till preleve button released
                while self.macro_frotti_poussière != 0:
                    self.joystickUpdate()
                    self.rate.sleep()
                self.printGreen("frottis macro done")
    
    # movement control loop
    def run(self):
        while not rospy.is_shutdown():
            self.joystickUpdate()
            
            # joint movement, wait=True
            self.poignetMove()
            self.baseMove()
            self.pinceMove()
            
            # arm movement, wait=False
            poseCommand = [self.effecteur_x_vitesse,self.effecteur_y_vitesse,self.effecteur_z_vitesse]
            self.armMove(poseCommand, wait=False)
            self.poseCommand_prev = poseCommand
            
            # macro movement, thread
            # self.home()
            self.macroFrottis()
            
            preleveMode = self.modification_mode_list[self.modification_mode_index]
            self.preleveModeUpdate(preleveMode)
            
            if preleveMode in ["frottis","liquide"]:
                self.preleveFrottisLiquide(preleveMode)
            elif preleveMode == "poussière":
                self.prelevePoussiere()
            elif preleveMode == "solide" and self.prelevement_1_2_3 != 0:
                self.printYellow("Pas d'outil de prélèvement en mode solide")
                
            if preleveMode in ["solide","frottis"]:
                self.stockSolideFrottis()
            elif preleveMode == "liquide":
                self.stockLiquide()
            elif preleveMode == "poussière":
                self.stockPoussiere()
            
            # TODO pub lum cam
            self.rate.sleep()
        
        self.printGreen("joystick exit")
        

if __name__ == '__main__':
    try:
        joystick_moveGroupe = Joystick_MoveGroupe(
            scale_pos=0.02, # max 2cm
            scale_rotation=0.05, # max 1deg
            sleepTime=0.1)
        joystick_moveGroupe.run()
    except rospy.ROSInterruptException:
        print("stop")
        pass
    





