import can
import time
import struct
import os
import threading
import rospy
from sensor_msgs.msg import JointState

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

# Angle_Demande = 0
# Angle_Reel = 0
# Demande_Home = 0
# Home_Fait = 0
# Demande_Verin = 0
# Verin_Fait = 0

Data = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] # [Angle_Demande, Demande_Home, Demande_Verin]
DernierDataEnvoye = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

def callback(data):
    rospy.loginfo(data.position)
    #Data[0][0] = data.position[3]
    for i in range(5):
        Data[i][0] = data.position[i+3]
    #print(Data)
    #print(Data)    
    #rospy.loginfo(data.position[0])

    #data.poisition[0]


def Send_CAN(id, data):
    message = can.Message(arbitration_id=id, data=data, is_extended_id=False)
    return bus.send(message)

def Envoi():
    for i in range(0,5):
        Send_CAN(100 + 10 * (i+1) + Adresse_Angle_Demande, data=struct.pack('f',Data[i][0])) # Angle demande
        Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Home, data=struct.pack('f',Data[i][1]))
        Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Verin, data=struct.pack('f',Data[i][2]))
        # if DernierDataEnvoye[i][0] != Data[i][0]:
        #     Send_CAN(100 + 10 * (i+1) + Adresse_Angle_Demande, data=struct.pack('f',Data[i][0])) # Angle demande
        #     DernierDataEnvoye[i][0] = Data[i][0]

        # if DernierDataEnvoye[i][1] != Data[i][1]:
        #     Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Home, data=struct.pack('f',Data[i][1]))
        #     DernierDataEnvoye[i][1] = Data[i][1]

        # if DernierDataEnvoye[i][2] != Data[i][2]:
        #     Send_CAN(100 + 10 * (i+1) + Adresse_Demande_Verin, data=struct.pack('f',Data[i][2]))
        #     DernierDataEnvoye[i][2] = Data[i][2]

        time.sleep(0.05)

def Thread_Debug():
    while True:
        Envoi()
        # for i in range(0,5):
        #     print("Envoie uStepper ID : " + str(i+1) + " | Angle demande : " + str(DernierDataEnvoye[i][0]) + " | Home demande : " + str(DernierDataEnvoye[i][1]) + " | Verin demande : " + str(DernierDataEnvoye[i][2]))
        # print("------------------------------------------------------------------------------------------------------------------------")
        time.sleep(0.05)

def subscriber():
    rospy.init_node('joint_states_subscriber', anonymous=False) #Node name
    rospy.Subscriber("joint_states", JointState, callback) #Name of the publisher to which we subscribe
    rospy.spin()

thread_debug = threading.Thread(target=Thread_Debug)
thread_debug.start()

if __name__ == '__main__':
    subscriber()
