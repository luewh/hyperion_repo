#!/usr/bin/python3

# https://deusyss.developpez.com/tutoriels/RaspberryPi/PythonEtLeGpio/#LI

# pip install RPi.GPIO
import RPi.GPIO as GPIO

import rospy
from sensor_msgs.msg import JointState
from std_msgs.msg import Int8
from time import time, sleep

class GPIOCom():
    def __init__(self) -> None:
    
        # GPIO.setmode(GPIO.BOARD) #rouge
        GPIO.setmode(GPIO.BCM) #noir
        # configuration = GPIO.getmode()
        # print(configuration)

        # motor liquide
        GPIO.setup(17, GPIO.OUT, initial=GPIO.LOW) # fwd motor 1
        GPIO.setup(18, GPIO.OUT, initial=GPIO.LOW) # bwd motor 1
        GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW) # fwd motor 2
        GPIO.setup(23, GPIO.OUT, initial=GPIO.LOW) # bwd motor 2
        GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW) # fwd motor 3
        GPIO.setup( 6, GPIO.OUT, initial=GPIO.LOW) # bwd motor 3

        # verin
        GPIO.setup(16, GPIO.OUT, initial=GPIO.LOW) # fwd motor verin
        GPIO.setup(26, GPIO.OUT, initial=GPIO.LOW) # bwd motor verin

        rospy.init_node("motor_sub", anonymous=False)
        rospy.Subscriber('/liquide', Int8, self.liquideCallback, queue_size=1)
        rospy.Subscriber("/joint_states", JointState, self.verinCallback, queue_size=1)
        self.verinPosEtat = "retraction"
        self.retractionTime = 11
        self.deploiementTime = 10
        self.pupm1Start = False
        self.pupm2Start = False
        self.pupm3Start = False

    def liquideCallback(self, data):
        # print("---\nliquide\n",data.data)
        pumpNumber = data.data
        # start pump 1
        if pumpNumber == 1 and not self.pupm1Start:
            print("start pump 1")
            self.pupm1Start = True
            GPIO.output(17, GPIO.LOW)
            GPIO.output(18, GPIO.HIGH)
        # start pump 2
        if pumpNumber == 2 and not self.pupm2Start:
            print("start pump 2")
            self.pupm2Start = True
            GPIO.output(22, GPIO.LOW)
            GPIO.output(23, GPIO.HIGH)
        # start pump 3
        if pumpNumber == 3:
            print("start pump 3")
            self.pupm3Start = True
            GPIO.output(24, GPIO.LOW)
            GPIO.output( 6, GPIO.HIGH)
        # stop all pump
        if pumpNumber == 0:
            if self.pupm1Start:
                print("stop pump 1")
                self.pupm1Start = False
                GPIO.output(17, GPIO.LOW)
                GPIO.output(18, GPIO.LOW)
            if self.pupm2Start:
                print("stop pump 2")
                self.pupm2Start = False
                GPIO.output(22, GPIO.LOW)
                GPIO.output(23, GPIO.LOW)
            if self.pupm3Start:
                print("stop pump 3")
                self.pupm3Start = False
                GPIO.output(24, GPIO.LOW)
                GPIO.output( 6, GPIO.LOW)
    
    def verinCallback(self, data):
        # print("---\nverin\n",data.position[7])
        verinPos = data.position[7]
        if verinPos > -0.075 and self.verinPosEtat == "deploiement":
            timeRetractionStart = time()
            # start verin retraction
            print("verin retract")
            GPIO.output(16, GPIO.HIGH)
            GPIO.output(26, GPIO.LOW)
            # wait retraction
            while time() - timeRetractionStart <= self.retractionTime:
                print("{}/{}".format(round(time() - timeRetractionStart,0),
                                     round(self.retractionTime)))
                sleep(1)
            self.verinPosEtat = "retraction"
            # stop verin
            print("verin stop")
            GPIO.output(16, GPIO.LOW)
            GPIO.output(26, GPIO.LOW)
        if verinPos < -0.075 and self.verinPosEtat == "retraction":
            timeDeploiementStart = time()
            # start verin deploiement
            print("verin deploie")
            GPIO.output(16, GPIO.LOW)
            GPIO.output(26, GPIO.HIGH)
            # wait deploiement
            while time() - timeDeploiementStart <= self.deploiementTime:
                print("{}/{}".format(round(time() - timeDeploiementStart,0),
                                     round(self.deploiementTime)))
                sleep(1)
            self.verinPosEtat = "deploiement"
            # stop verin
            print("verin stop")
            GPIO.output(16, GPIO.LOW)
            GPIO.output(26, GPIO.LOW)
        
    
if __name__ == '__main__':
    try:
        gpio = GPIOCom()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass
    finally:
        print("clean up")
        GPIO.cleanup()