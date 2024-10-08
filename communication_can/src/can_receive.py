#!/usr/bin/env python

import can
import time
import struct
import os
import threading
import rospy
import numpy as np
from std_msgs.msg import Bool, Float32MultiArray

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
Data_Angle = [0,0,0,0,0,0]

def Receive_CAN(adress):
    message = bus.recv()
    if message.arbitration_id == adress:
        return struct.unpack('f', message.data)[0]
    else :
        return None
    
ValidationHome = True

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
    Data_prev = Data

def Thread_Reception():
    while True:
        Reception()

def Test_Home_Fait():
    for Moteur in Data:
        if Moteur[1] == 1:
            return True
    return False

def callback(data):
    global ValidationHome   
    if data.data:
        ValidationHome = True
    else:
        ValidationHome = False

def publisher():
    rospy.init_node('can_data_publisher', anonymous=True)
    pub_home = rospy.Publisher('/home', Bool, queue_size=10)
    pub_angle = rospy.Publisher('IHM/moteurs/retours_positions', Float32MultiArray, queue_size=10)
    rospy.Subscriber('/home', Bool, callback)
    rate = rospy.Rate(10)  # 10hz
    while not rospy.is_shutdown():
        if Test_Home_Fait() and ValidationHome:
            pub_home.publish(False)
        msg = Float32MultiArray()
        for Axe in range(len(Data)):
            Data_Angle[Axe] = Data[Axe][0]
        msg.data = np.array(Data_Angle).flatten().tolist()
        pub_angle.publish(msg)
        rate.sleep()

thread_reception = threading.Thread(target=Thread_Reception)
thread_reception.daemon = True #permet l'arret du code avec CTRL C
thread_reception.start()

if __name__ == '__main__':
    publisher()