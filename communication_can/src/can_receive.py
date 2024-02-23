import can
import time
import struct
import os
import threading

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

# Angle_Reel = 0
# Home_Fait = 0
# Verin_Fait = 0

Data = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]] # [Angle_Reel, Home_Fait, Verin_Fait]
DernierDataEnvoye = [[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]

startTime = time.monotonic()

def Send_CAN(id, data):
    message = can.Message(arbitration_id=id, data=data, is_extended_id=False)
    return bus.send(message)

def Receive_CAN(adress):
    message = bus.recv()
    if message.arbitration_id == adress:
        return struct.unpack('f', message.data)[0]
    else : 
        return None

def Reception():
    while True:
        message = bus.recv()
        for i in range(0,5):
            if message.arbitration_id == 100 + 10 * (i+1) + Adresse_Angle_Reel:
                Data[i][0]=struct.unpack('f', message.data)[0]
            elif message.arbitration_id == 100 + 10 * (i+1) + Adresse_Home_Fait:
                Data[i][1]=struct.unpack('f', message.data)[0]
            elif message.arbitration_id == 100 + 10 * (i+1) + Adresse_Verin_Fait:
                Data[i][2]=struct.unpack('f', message.data)[0]
        time.sleep(0.01)

def Thread_Debug():
    while True:
        for i in range(0,5):
            print("Reception uStepper ID : " + str(i+1) + " | Angle reel : " + str(Data[i][0]) + " | Home fait : " + str(Data[i][1]) + " | Verin fait : " + str(Data[i][2]))
        print("------------------------------------------------------------------------------------------------------------------------")
        time.sleep(0.5)

thread_debug = threading.Thread(target=Thread_Debug)
thread_debug.start()

Reception()