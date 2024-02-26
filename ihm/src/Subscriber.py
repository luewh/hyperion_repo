#!/usr/bin/env python3
#Gestion des souscriptions aux topics ROS
import time
import platform
import math

if platform.system() != "Windows":
        import rospy
        import sys
        from std_msgs.msg import String,Int8,Int16,Float32,Float32MultiArray
        from geometry_msgs.msg import Twist
        from sensor_msgs.msg import JointState
        
class Subscriber() :
    def __init__(self,IHM):
        #Init variables
        #list param
        self.listPrelevEtat = ["Erreur", "Boite vide, pas de prélèvement en cours", "Prélèvement en cours","Prélèvement fini, stockage plein", "Défaut rencontré dans le cycle de prélèvement"]
        self.listCoulEtatPrelev = ["red", "dark grey", "orange", "light Green", "red"] #couleur de fond etat prelevement
        self.IHM = IHM

        #Dictionnaires
        self.DictTexteEtatActuel1 = {1 : "Action opérateur demandée", 2 : "Programme auto en cours", 3 : "Programme fini"}
        self.DictTexteEtatActuel2 = {1 : "Ouverture capot en cours", 2 : "Fermeture capot en cours", 3 : "Chargement stockage solide en cours", 4 : "Remplissage bouteille en cours", 5 : "Mouvement manuel en cours", 6 : "Prise Pad Frottis en cours",
                                     25 : "Retour en position repli", 99 : "Défaut rencontré dans un programme", 100 : "Programme fini"}
        self.DictCouleurEtatActuel1 = {1 : "violet", 2 : "orange", 3 : "light Green"}
        self.DictCouleurEtatActuel2 = {1 : "orange", 2 : "orange", 3 : "light Green", 4 : "light Green", 5 : "orange", 6 : "orange",
                                       25 : "light Green", 99 : "red", 100 : "light Green"}
        
        #Init node
        rospy.init_node('turtleturn', anonymous=True)
    
        #subscriber Prelevement
        rospy.Subscriber('IHM/prelevement/PrelevSelectAct', Int16, self.CallbackPrelevSelectAct)
                         
        rospy.Subscriber("IHM/prelevement/PrelevEtat1",Int16, self.CallbackPrelevEtat1)
        rospy.Subscriber("IHM/prelevement/PrelevEtat2",Int16, self.CallbackPrelevEtat2)
        rospy.Subscriber("IHM/prelevement/PrelevEtat3",Int16, self.CallbackPrelevEtat3)
        
        #Subscriber moteurs
        rospy.Subscriber("joint_states", JointState, self.CallbackMajPosDem)
        
        rospy.Subscriber("IHM/moteurs/retours_positions", Float32MultiArray, self.CallbackMajPosRet)
        
        #subscriber position cartésienne
        rospy.Subscriber("IHM/PositionRobot/PosX_TCP", Float32, self.CallbackMajTCP_X)
        rospy.Subscriber("IHM/PositionRobot/PosY_TCP", Float32, self.CallbackMajTCP_Y)
        rospy.Subscriber("IHM/PositionRobot/PosZ_TCP", Float32, self.CallbackMajTCP_Z)
        rospy.Subscriber("IHM/PositionRobot/RotZ_TCP", Float32, self.CallbackMajTCP_RotZ)  

        #subscriber pompe peristaltique
        rospy.Subscriber("IHM/moteurs/pompe_peristaltique/RotMotPompePeriEtat", Int16, self.CallbackMajPompePeristaltique)
        
        #subscriber led
        rospy.Subscriber("IHM/led/EclairageEtat", Int16, self.CallbackMajLed)
 
        #subscriber etat actuel
        rospy.Subscriber("IHM/Etat/EtatActuel1", Int16, self.CallbackMajEtatActuel1)
        rospy.Subscriber("IHM/Etat/EtatActuel2", Int16, self.CallbackMajEtatActuel2)
        
        #subscriber cmd clear
        rospy.Subscriber("/IHM/commande/CmdClearLogDefauts", Int16, self.CallbackCmdClear)
        
        #subscriber logs
        rospy.Subscriber("/IHM/LogsDefauts/LogDefaut", String, self.CallbackLogDefauts)
        rospy.Subscriber("/IHM/LogsInfos/LogInfos", String, self.CallbackLogInfos)
       
        print ("Fin init Subscriber")
        
        self.IHM.mainloop()
        rospy.spin()
        

    #Callbacks
    def CallbackPrelevSelectAct(self, data): #OK
        print(data)
        self.IHM.frame_input.labelModePoussiere.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 1 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeSolide.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 2 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeLiquide.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 3 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeFrotti.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 4 else self.IHM.CouleurFondNonSelect)
       
        print ("callback prelevement select act")
        
    def CallbackPrelevEtat1(self, data): #AT
        self.IHM.frame_input.labelPrlmt1.configure( text = self.listPrelevEtat[data.data],
                                                    fg_color= self.listCoulEtatPrelev[data.data])
    def CallbackPrelevEtat2(self, data):
        self.IHM.frame_input.labelPrlmt2.configure( text = self.listPrelevEtat[data.data],
                                                    fg_color= self.listCoulEtatPrelev[data.data])
    def CallbackPrelevEtat3(self, data):
        self.IHM.frame_input.labelPrlmt3.configure( text = self.listPrelevEtat[data.data],
                                                    fg_color= self.listCoulEtatPrelev[data.data])        
        
    def CallbackMajPosDem(self,data): # OK
        self.IHM.frame_input.labelAxe1Demandee.configure(text = "Axe 1 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[3])))) + " °")
        self.IHM.frame_input.labelAxe2Demandee.configure(text = "Axe 2 : " + str("{:.2f}".format((abs(float(self.MiseAFormatPosition(data.position[4]))))*1000)) + " mm")
        self.IHM.frame_input.labelAxe3Demandee.configure(text = "Axe 3 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[5])))) + " °")
        self.IHM.frame_input.labelAxe4Demandee.configure(text = "Axe 4 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[6])))) + " °")
        self.IHM.frame_input.labelAxe5Demandee.configure(text = "Axe 5 : " + str("{:.2f}".format(float(self.MiseAFormatPosition(data.position[8]))*1000) + " mm"))

    def CallbackMajPosRet(self,data): # A VALIDER
        self.IHM.frame_input.labelAxe1Reel.configure(text = "Axe 1 : " + self.MiseAFormatPosition(data.data[3])+ " °")
        self.IHM.frame_input.labelAxe2Reel.configure(text = "Axe 2 : " + self.MiseAFormatPosition(data.data[4])+ " mm")
        self.IHM.frame_input.labelAxe3Reel.configure(text = "Axe 3 : " + self.MiseAFormatPosition(data.data[5])+ " °")
        self.IHM.frame_input.labelAxe4Reel.configure(text = "Axe 4 : " + self.MiseAFormatPosition(data.data[6])+ " °")
        self.IHM.frame_input.labelAxe5Reel.configure(text = "Axe 5 : " + self.MiseAFormatPosition(data.data[7])+ " mm")
        

    def CallbackMajTCP(self,data): # A VALIDER
        Pos = self.MiseAFormatPosition(data.data)
        self.IHM.frame_input.labelPosXCart.configure(text = "Position X : " + Pos)
        self.IHM.frame_input.labelPosYCart.configure(text = "Position Y : " + Pos)
        self.IHM.frame_input.labelPosZCart.configure(text = "Position Z : " + Pos)
        self.IHM.frame_input.labelRotZCart.configure(text = "Rotation Z : " + Pos)
        
    def CallbackMajPompePeristaltique(self,data): #OK
        if data.data == 1:
            fondCouleur = self.IHM.CouleurFondSelect
            textlabel = "En marche"
        elif data.data == 2 :
            fondCouleur = self.IHM.CouleurFondNonSelect
            textlabel = "Arrêt"
        elif data.data == 3 :
            fondCouleur = self.IHM.CouleurFondNonSelect
            textlabel = "Non connecté"
        else :
            fondCouleur = self.IHM.CouleurFondNonSelect
            textlabel = "Erreur"
        self.IHM.frame_input.labelEtatPompePeristaltique.configure(fg_color = fondCouleur,
                                                              text = textlabel)
        print ("callback maj pompe peristaltique")

    def CallbackMajLed(self,data): #OK
        self.IHM.frame_input.labelEtatEclairage.configure(fg_color = self.IHM.CouleurFondSelect if (data.data == 1) else self.IHM.CouleurFondNonSelect,
                                                     text = "Allumé" if (data.data == 1) else "Eteint")
        print ("callback maj led")
        
    def CallbackMajEtatActuel1(self,data): #OK
        self.IHM.labelEtatActuel1.configure(text = self.DictTexteEtatActuel1[data.data],
                                           fg_color = self.DictCouleurEtatActuel1[data.data])
        print ("callback maj etat actuel 1")
   
    def CallbackMajEtatActuel2(self,data): #OK
        self.IHM.labelEtatActuel2.configure(text = self.DictTexteEtatActuel2[data.data],
                                        fg_color = self.DictCouleurEtatActuel2[data.data])
        print ("callback maj etat actuel 2")

    def CallbackCmdClear(self, data): #OK
        self.IHM.RazDataDefautInfo(data.data)
        print ("callback cmd clear")
        
    def CallbackLogDefauts(self, data): #AT
        self.IHM.AjoutLigneCSVDefaut(data.data)
        print ("callback log defauts")
        
    def CallbackLogInfos(self, data): #AT
        self.IHM.AjoutLigneCSVInfo(data.data)
        print ("callback log infos")
    
    
    def MiseAFormatPosition(self,data): #OK
        data = float("{:.3f}".format(data))
        Pos= str(data) #mise a format
        
        return Pos
        
        
        
        
if __name__ == "__main__":
    
    
    print("boucle utilisation subscriber")