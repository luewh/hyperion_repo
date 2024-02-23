import can
import time
import struct
import os
import threading
import rospy
from std_msgs.msg import Bool, Float32MultiArray

os.system('sudo ip link set can0 up type can bitrate 500000')

# Configuration du bus CAN
can_interface = 'can0'  # Nom de l'interface CAN
bitrate = 500000  # Débit en bits/s
bus = can.interface.Bus(channel = can_interface, bitrate=bitrate, bustype='socketcan')

# Définition des adresses CAN
# 1 : Base
# 2 : Epaule Translate
# 3 : Coude Rotate
# 4 : Poignet
# 5 : Pince

Adresse_Angle_Reel = 2
Adresse_Home_Fait = 4
Adresse_Verin_Fait = 6

Data = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] # [Angle_Reel, Home_Fait, Verin_Fait]

def Receive_CAN(adress):
    message = bus.recv()
    if message.arbitration_id == adress:
        return struct.unpack('f', message.data)[0]
    else : 
        return None

def Reception():
    message = bus.recv()
    for i in range(0,5):
        if message.arbitration_id == 100 + 10 * (i+1) + Adresse_Angle_Reel:
            Data[i][0]=struct.unpack('f', message.data)[0]
        elif message.arbitration_id == 100 + 10 * (i+1) + Adresse_Home_Fait:
            Data[i][1]=struct.unpack('f', message.data)[0]
        elif message.arbitration_id == 100 + 10 * (i+1) + Adresse_Verin_Fait:
            Data[i][2]=struct.unpack('f', message.data)[0]
        time.sleep(0.01)

def Thread_Reception():
    while True:
        Reception()
        time.sleep(0.05)

def Test_Home_Fait():
    for EachMotor in Data:
        if EachMotor[1] == 0:
            return False
    return True

def publisher():
    rospy.init_node('can_data_publisher', anonymous=True)
    pub_home = rospy.Publisher('/home', Bool, queue_size=10)
    #pub_angle = rospy.Publisher('IHM/moteurs/retours_positions', Float32MultiArray, queue_size=10) A TESTER
    
    rate = rospy.Rate(10)  # 10hz
    while not rospy.is_shutdown():
        if Test_Home_Fait() == True:
            pub_home.publish(False)
        #pub_angle.publish(Data[0])
        rate.sleep()

thread_reception = threading.Thread(target=Thread_Reception)
thread_reception.daemon = True #permet l'arret du code avec CTRL C
thread_reception.start()

if __name__ == '__main__':
    publisher()