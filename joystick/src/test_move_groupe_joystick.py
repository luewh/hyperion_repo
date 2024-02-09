import rospy
import moveit_commander
# import moveit_msgs.msg
import sys
import copy
from time import sleep

from joystick import Joystick
from euler_quaternion import euler_to_quaternion, quaternion_to_euler



class Joystick_MoveGroupe (Joystick):
    def __init__(self,
                 scale_pos=1.0,
                 scale_rotation=1.0) -> None:
        super().__init__(sleepTime=0.1)

        moveit_commander.roscpp_initialize(sys.argv)
        rospy.init_node("move_group_python_interface_tutorial", anonymous=True)

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
        posEch1 = [3.64,0,-2.09,-1.51,0]
        posEch2 = [3.29,0,-2.09,-1.17,0]
        posEch3 = [2.91,0,-1.89,-0.99,0]
        self.poseEch = [posEch1,posEch2,posEch3]
        posStock1 = [3.69,0,-1.72,-1.73,0]
        posStock2 = [3.30,0,-1.68,-1.37,0]
        posStock3 = [2.87,0,-1.41,-0.46,0]
        self.poseStock = [posStock1,posStock2,posStock3]
        self.inPreleve = False

    def armMove (self,pose):
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
            0.05,       # eef_step
            0,      # jump_threshold
            avoid_collisions=True)
        self.move_group_arm.execute(plan, wait=False)
        
        colonne_value = self.move_group_arm.get_current_joint_values()
        verin_value = self.move_group_hand.get_current_joint_values()
        # if colonne at top and verin not at top
        if (colonne_value[1] + self.scale_pos * pose[2] > 0) and (round(verin_value[0],2) != 0):
            # TODO pub verin action
            self.move_group_arm.stop()
            # verin got to top
            verin_value[0] = 0
            self.move_group_hand.go(verin_value, wait=True)
            # colonne down verin length
            colonne_value[1] -= 0.15
            self.move_group_arm.go(colonne_value, wait=True)
            
        # if colonne at bottom and verin not at bottom
        if (colonne_value[1] + self.scale_pos * pose[2] < -0.285) and (round(verin_value[0],2) != -0.15):
            # TODO pub verin action
            self.move_group_arm.stop()
            # colonne up verin length
            colonne_value[1] += 0.15
            self.move_group_arm.go(colonne_value, wait=True)
            # verin got to bottom
            verin_value[0] = -0.15
            self.move_group_hand.go(verin_value, wait=True)
            
    def pinceMove(self):
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
    
    def preleve(self):
        if self.prelevement_1_2_3 == 0:
            # if movement initiated
            if self.inPreleve:
                current_joints = self.move_group_arm.get_current_joint_values()
                self.move_group_arm.go(current_joints, wait=False)
                print("abort preleve movement")
            self.inPreleve = False
            return
        # movement init
        if self.inPreleve == False:
            self.move_group_arm.stop()
            pose = self.poseEch[self.prelevement_1_2_3-1]
            # verin go top
            self.move_group_hand.go([0], wait=True)
            result = self.move_group_arm.go(pose[:-1], wait=False)
            self.inPreleve = True
        else:
            print("innnn")
            
    
    # joystick control loop
    def run(self):
        try:
            while True:
                self.joystickUpdate()
                self.pinceMove()
                self.baseMove()
                pose = [self.effecteur_x_vitesse,self.effecteur_y_vitesse,self.effecteur_z_vitesse]
                self.armMove(pose)
                self.preleve()
                # TODO saisie pre 1_2_3
                # TODO stockage 1_2_3
                # TODO pub lum cam modePre
                sleep(self.sleepTime)
        except KeyboardInterrupt:
            print("Exiting...")
        

if __name__ == '__main__':
    joystick_moveGroupe = Joystick_MoveGroupe(scale_pos=0.2,scale_rotation=0.1)
    joystick_moveGroupe.run()





