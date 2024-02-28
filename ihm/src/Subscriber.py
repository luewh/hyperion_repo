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
        from visualization_msgs.msg import Marker
        
class Subscriber() :
    def __init__(self,IHM):
        #Init variables
        #list param
        self.listPrelevEtat = ["Prélèvement",
                               "Boite vide, pas de prélèvement en cours",
                               "Prélèvement en cours",
                               "Prélèvement fini, stockage plein",
                               "Défaut rencontré dans le cycle de prélèvement"]
        
        self.listCoulEtatPrelev = ["dark grey",
                                   "light Green",
                                   "orange",
                                   "light Green",
                                   "red"] #couleur de fond etat prelevement
        self.IHM = IHM

        #Dictionnaires
        self.DictTexteEtatActuel1 = {1 : "Action opérateur demandée", 2 : "Programme auto en cours", 3 : "Programme fini"}
        self.DictTexteEtatActuel2 = {1 : "Ouverture capot en cours", 2 : "Fermeture capot en cours", 3 : "Chargement stockage solide en cours", 4 : "Remplissage bouteille en cours", 5 : "Mouvement manuel en cours", 6 : "Prise Pad Frottis en cours",
                                     25 : "Retour en position repli", 99 : "Défaut rencontré dans un programme", 100 : "Programme fini"}
        self.DictCouleurEtatActuel1 = {1 : "violet", 2 : "orange", 3 : "light Green"}
        self.DictCouleurEtatActuel2 = {1 : "orange", 2 : "orange", 3 : "light Green", 4 : "light Green", 5 : "orange", 6 : "orange",
                                       25 : "light Green", 99 : "red", 100 : "light Green"}
        
        #Init node
        rospy.init_node('ihm_suscriber', anonymous=False)
    
        #subscriber Prelevement
        rospy.Subscriber('IHM/prelevement/PrelevSelectAct', Int8, self.CallbackPrelevSelectAct)
                         
        rospy.Subscriber("IHM/prelevement/PrelevEtat1",Int8, self.CallbackPrelevEtat1)
        rospy.Subscriber("IHM/prelevement/PrelevEtat2",Int8, self.CallbackPrelevEtat2)
        rospy.Subscriber("IHM/prelevement/PrelevEtat3",Int8, self.CallbackPrelevEtat3)
        
        #Subscriber moteurs
        rospy.Subscriber("joint_states", JointState, self.CallbackMajPosDem)
        
        rospy.Subscriber("IHM/moteurs/retours_positions", Float32MultiArray, self.CallbackMajPosRet)
        
        #subscriber position cartésienne
        rospy.Subscriber("tcp", Marker, self.CallbackMajTCP)

        #subscriber pompe peristaltique
        rospy.Subscriber("liquide", Int8, self.CallbackMajPompePeristaltique)
        
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
        
        self.IHM.mainloop()
        rospy.spin()
        

    def CallbackPrelevSelectAct(self, data):
        self.IHM.frame_input.labelModePoussiere.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 1 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeSolide.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 2 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeLiquide.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 3 else self.IHM.CouleurFondNonSelect)
        self.IHM.frame_input.labelModeFrotti.configure(fg_color=self.IHM.CouleurFondSelect if data.data == 4 else self.IHM.CouleurFondNonSelect)
        
    def CallbackPrelevEtat1(self, data): #AT
        self.IHM.frame_input.labelPrlmt1.configure( text = self.listPrelevEtat[data.data]+" 1",
                                                    fg_color= self.listCoulEtatPrelev[data.data])
    def CallbackPrelevEtat2(self, data):
        self.IHM.frame_input.labelPrlmt2.configure( text = self.listPrelevEtat[data.data]+" 2",
                                                    fg_color= self.listCoulEtatPrelev[data.data])
    def CallbackPrelevEtat3(self, data):
        self.IHM.frame_input.labelPrlmt3.configure( text = self.listPrelevEtat[data.data]+" 3",
                                                    fg_color= self.listCoulEtatPrelev[data.data])        
        
    def CallbackMajPosDem(self,data): # OK
        self.IHM.frame_input.labelAxe1Demandee.configure(text = "Axe 1 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[3])))) + " °")
        self.IHM.frame_input.labelAxe2Demandee.configure(text = "Axe 2 : " + str("{:.2f}".format(300-(abs(float(self.MiseAFormatPosition(data.position[4]))))*1000)) + " mm")
        self.IHM.frame_input.labelAxe3Demandee.configure(text = "Axe 3 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[5])))) + " °")
        self.IHM.frame_input.labelAxe4Demandee.configure(text = "Axe 4 : " + str("{:.2f}".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[6])))) + " °")
        self.IHM.frame_input.labelAxe5Demandee.configure(text = "Axe 5 : " + str("{:.2f}".format(float(self.MiseAFormatPosition(data.position[8]))*1000) + " mm"))
        self.IHM.frame_input.labelRotZCart.configure(text = "Rotation Z : {:.2f} °".format((180/math.pi)*float(self.MiseAFormatPosition(data.position[6]))))

    def CallbackMajPosRet(self,data): # A VALIDER
        self.IHM.frame_input.labelAxe1Reel.configure(text = "Axe 1 : " + self.MiseAFormatPosition(data.data[0])+ " °")
        self.IHM.frame_input.labelAxe2Reel.configure(text = "Axe 2 : " + self.MiseAFormatPosition(data.data[1])+ " mm")
        self.IHM.frame_input.labelAxe3Reel.configure(text = "Axe 3 : " + self.MiseAFormatPosition(data.data[2])+ " °")
        self.IHM.frame_input.labelAxe4Reel.configure(text = "Axe 4 : " + self.MiseAFormatPosition(data.data[3])+ " °")
        self.IHM.frame_input.labelAxe5Reel.configure(text = "Axe 5 : " + self.MiseAFormatPosition(data.data[4])+ " mm")
        

    def CallbackMajTCP(self,data):
        Pos = data.points[-1]
        Pos.x = self.MiseAFormatPosition(Pos.x * 1000)
        Pos.y = self.MiseAFormatPosition(Pos.y * 1000)
        Pos.z = self.MiseAFormatPosition(Pos.z * 1000)
        self.IHM.frame_input.labelPosXCart.configure(text = "Position X : {} mm".format(Pos.x))
        self.IHM.frame_input.labelPosYCart.configure(text = "Position Y : {} mm".format(Pos.y))
        self.IHM.frame_input.labelPosZCart.configure(text = "Position Z : {} mm".format(Pos.z))
        
    def CallbackMajPompePeristaltique(self,data):
        if data.data == 1:
            fondCouleur = self.IHM.CouleurFondSelect
            textlabel = "Pompe 1 en marche"
        elif data.data == 2 :
            fondCouleur = self.IHM.CouleurFondSelect
            textlabel = "Pompe 2 en marche"
        elif data.data == 3 :
            fondCouleur = self.IHM.CouleurFondSelect
            textlabel = "Pompe 3 en marche"
        elif data.data == 0 :
            fondCouleur = self.IHM.CouleurFondNonSelect
            textlabel = "Pompes en arrêt"
        else :
            fondCouleur = self.IHM.CouleurFondNonSelect
            textlabel = "Erreur"
            
        self.IHM.frame_input.labelEtatPompePeristaltique.configure(fg_color = fondCouleur, text = textlabel)

    def CallbackMajLed(self,data): #OK
        self.IHM.frame_input.labelEtatEclairage.configure(fg_color = self.IHM.CouleurFondSelect if (data.data == 1) else self.IHM.CouleurFondNonSelect,
                                                     text = "Allumé" if (data.data == 1) else "Eteint")
        # print ("callback maj led")
        
    def CallbackMajEtatActuel1(self,data): #OK
        self.IHM.labelEtatActuel1.configure(text = self.DictTexteEtatActuel1[data.data],
                                           fg_color = self.DictCouleurEtatActuel1[data.data])
        # print ("callback maj etat actuel 1")
   
    def CallbackMajEtatActuel2(self,data): #OK
        self.IHM.labelEtatActuel2.configure(text = self.DictTexteEtatActuel2[data.data],
                                        fg_color = self.DictCouleurEtatActuel2[data.data])
        # print ("callback maj etat actuel 2")

    def CallbackCmdClear(self, data): #OK
        self.IHM.RazDataDefautInfo(data.data)
        # print ("callback cmd clear")
        
    def CallbackLogDefauts(self, data): #AT
        self.IHM.AjoutLigneCSVDefaut(data.data)
        # print ("callback log defauts")
        
    def CallbackLogInfos(self, data): #AT
        self.IHM.AjoutLigneCSVInfo(data.data)
        # print ("callback log infos")
    
    
    def MiseAFormatPosition(self,data): #OK
        data = float("{:.3f}".format(data))
        Pos= str(data) #mise a format
        
        return Pos
        
        
        
        
if __name__ == "__main__":
    
    
    print("boucle utilisation subscriber")