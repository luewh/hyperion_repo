"""
Ce script Python permet de contrôler des joints robotiques en utilisant un bus CAN pour la communication entre les différents composants du robot. Le script s'abonne à un topic ROS pour recevoir les états des joints, puis envoie ces données sur le bus CAN pour le contrôle des différents composants.

Le script comprend les fonctionnalités suivantes :

1. Initialisation du bus CAN et des adresses CAN pour chaque composant du robot.
2. Abonnement à un topic ROS pour recevoir les états des joints.
3. Mise en liste des données reçues depuis les topic et envoi de ces messages via le bus CAN pour contrôler les composants du robot.
4. Utilisation de threading pour gérer l'envoi continu des messages CAN tout en continuant à recevoir les états des joints.

"""

import can
import time
import struct
import os
import threading
import rospy
from sensor_msgs.msg import JointState, Bool

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

Adresse_Angle_Demande = 1
Adresse_Demande_Home = 3
Adresse_Demande_Verin = 5

Data = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] # [Angle_Demande, Demande_Home, Demande_Verin]

def callback(data):
    #rospy.loginfo(data.position)
    for i in range(5):
        Data[i][0] = data.position[i+3]

def callback_home(data):
    rospy.loginfo("Home demandé : {}".format(data.data))
    for i in range(5):
        Data[i][1] = data.data

def callback_verin(data):
    rospy.loginfo("Verin demandé : {}".format(data.data))
    for i in range(5):
        Data[i][2] = data.data

def Send_CAN(id, data):
    message = can.Message(arbitration_id=id, data=data, is_extended_id=False)
    return bus.send(message)

def Envoi():
    for i in range(0,5):
        Send_CAN(100 + 10 * (i+1) + Adresse_Angle_Demande, data=struct.pack('f',Data[i][0])) # Angle demande
        Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Home, data=struct.pack('f',Data[i][1]))
        Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Verin, data=struct.pack('f',Data[i][2]))
        time.sleep(0.05)

def Thread_Envoi():
    while True:
        Envoi()
        time.sleep(0.05)

def subscriber():
    rospy.init_node('can_send', anonymous=False) #Node name
    rospy.Subscriber("joint_states", JointState, callback) #Name of the publisher to which we subscribe
    rospy.Subscriber("/home", Bool, callback_home)  # Subscribe to /home topic
    rospy.Subscriber("/verin", Bool, callback_verin)  # Subscribe to /home topic
    rospy.spin()

thread_envoi = threading.Thread(target=Thread_Envoi)
thread_envoi.daemon = True #permet l'arret du code avec CTRL C
thread_envoi.start()

if __name__ == '__main__':
    subscriber()
