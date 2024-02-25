#!/usr/bin/env python3
#Creation de la classe IHM; bit clignotant, couleur clignotante, maj logs
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import time
import platform
from Read_CSV import ReadCSV
from Write_CSV import WriteCSV


ctk.set_appearance_mode("light")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class IHM(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Visu Etat SYSMAP") #titre de la fenêtre
        self.geometry("1250x800")
        #self.attributes('-fullscreen', True)
        self._fg_color = "white"
        self.CouleurFondValid = "light Green"
        self.CouleurFondSelect = "light Green"
        self.CouleurFondNonValid = "red"
        self.CouleurFondNonSelect = "dark grey"
        self.bitClignotant = 0
        self.PresLogDefaut = False 
        self.pathLogDefaut = 'LogDefaut.csv'
        self.pathLogInfo = 'LogInfo.csv'
        self.AlarmeAxe1, self.AlarmeAxe2, self.AlarmeAxe3, self.AlarmeAxe4, self.AlarmeAxe5 = False, False, False, False, False
        self.ValeurTheoAxe1, self.ValeurTheoAxe2, self.ValeurTheoAxe3, self.ValeurTheoAxe4, self.ValeurTheoAxe5 = 0.00, 0.00, 0.00, 0.00, 0.00
        self.ValeurReelAxe1, self.ValeurReelAxe2, self.ValeurReelAxe3, self.ValeurReelAxe4, self.ValeurReelAxe5 = 0.00, 0.00, 0.00, 0.00, 0.00
        self.toleranceEcartValAxe = 0.1
        
        self.ReaderCSV= ReadCSV()
        self.WriterCSV = WriteCSV()
        
        # init grid        
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)
        self.grid_rowconfigure((1), weight=2)
        
        #Frame input values
        self.frame_input = ctk.CTkFrame(self)
        self.frame_input.grid(row=0, column=0, sticky="nsew")
        self.frame_input.grid_columnconfigure((0,1,2,3,4), weight=1)
        self.frame_input.grid_rowconfigure((0,1,2,3,4,5,6,7,8), weight=1)
        
        #Pos reelle moteur
        self.frame_input.labelPosReelMoteur = ctk.CTkLabel(self.frame_input, text="Position réelle moteur",font=("Verdana", 15, "bold"),
                                                           text_color="black",fg_color="dark grey",
                                                           padx=25,pady=15,corner_radius=18)
        self.frame_input.labelPosReelMoteur.grid(row=0, column=0)
        self.frame_input.labelAxe1Reel= ctk.CTkLabel(self.frame_input, text="Axe 1 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe1Reel.grid(row=1, column=0)
        self.frame_input.labelAxe2Reel= ctk.CTkLabel(self.frame_input, text="Axe 2 : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe2Reel.grid(row=2, column=0)
        self.frame_input.labelAxe3Reel= ctk.CTkLabel(self.frame_input, text="Axe 3 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe3Reel.grid(row=3, column=0)
        self.frame_input.labelAxe4Reel= ctk.CTkLabel(self.frame_input, text="Axe 4 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe4Reel.grid(row=4, column=0)
        self.frame_input.labelAxe5Reel= ctk.CTkLabel(self.frame_input, text="Axe 5 : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe5Reel.grid(row=5, column=0)
        
        
        #Pos demandee moteur
        self.frame_input.labelPosDemandeeMoteur = ctk.CTkLabel(self.frame_input, text="Position demandée moteur",font=("Verdana", 15, "bold"),
                                                           text_color="black",fg_color="dark grey",
                                                           padx=25,pady=15,corner_radius=18)
        self.frame_input.labelPosDemandeeMoteur.grid(row=0, column=1)
        self.frame_input.labelAxe1Demandee= ctk.CTkLabel(self.frame_input, text="Axe 1 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe1Demandee.grid(row=1, column=1)
        self.frame_input.labelAxe2Demandee= ctk.CTkLabel(self.frame_input, text="Axe 2 : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe2Demandee.grid(row=2, column=1)
        self.frame_input.labelAxe3Demandee= ctk.CTkLabel(self.frame_input, text="Axe 3 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe3Demandee.grid(row=3, column=1)
        self.frame_input.labelAxe4Demandee= ctk.CTkLabel(self.frame_input, text="Axe 4 : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe4Demandee.grid(row=4, column=1)
        self.frame_input.labelAxe5Demandee= ctk.CTkLabel(self.frame_input, text="Axe 5 : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=50,pady=10)
        self.frame_input.labelAxe5Demandee.grid(row=5, column=1)
        
        #pos cartesienne
        self.frame_input.labelPosCartesienne = ctk.CTkLabel(self.frame_input, text="Position cartésienne",font=("Verdana", 15, "bold"),
                                                            text_color="black",fg_color="dark grey",
                                                           padx=30,pady=15,corner_radius=15)
        self.frame_input.labelPosCartesienne.grid(row=0, column=2)
        self.frame_input.labelPosXCart=ctk.CTkLabel(self.frame_input, text="Position X : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=30,pady=10)
        self.frame_input.labelPosXCart.grid(row=1, column=2)
        self.frame_input.labelPosYCart=ctk.CTkLabel(self.frame_input, text="Position Y : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=30,pady=10)
        self.frame_input.labelPosYCart.grid(row=2, column=2)
        self.frame_input.labelPosZCart=ctk.CTkLabel(self.frame_input, text="Position Z : 000.00 mm",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=30,pady=10)
        self.frame_input.labelPosZCart.grid(row=3, column=2)
        self.frame_input.labelRotZCart=ctk.CTkLabel(self.frame_input, text="Rotation Z : 000.00 °",font=("arial", 15),
                                                    text_color="black",fg_color="dark grey",
                                                    padx=30,pady=10)
        self.frame_input.labelRotZCart.grid(row=4, column=2)
        
        #Mode prélèvement choisi
        self.frame_input.labelModePrelevChoisi = ctk.CTkLabel(self.frame_input, text="Mode prélèvement choisi",font=("Verdana", 15, "bold"),
                                                                text_color="black",fg_color="dark grey",
                                                                padx=25,pady=15,corner_radius=18)
        self.frame_input.labelModePrelevChoisi.grid(row=0, column=3)
        self.frame_input.labelModePoussiere=ctk.CTkLabel(self.frame_input, text="Prélèvement Poussière",font=("arial", 15),
                                                            text_color="black",fg_color=self.CouleurFondNonSelect,
                                                            padx=35,pady=15)
        self.frame_input.labelModePoussiere.grid(row=1, column=3)
        self.frame_input.labelModeSolide=ctk.CTkLabel(self.frame_input, text="Prélèvement Solide",font=("arial", 15),
                                                            text_color="black",fg_color=self.CouleurFondNonSelect,
                                                            padx=50,pady=15)
        self.frame_input.labelModeSolide.grid(row=2, column=3)
        self.frame_input.labelModeLiquide=ctk.CTkLabel(self.frame_input, text="Prélèvement Liquide",font=("arial", 15),
                                                            text_color="black",fg_color=self.CouleurFondNonSelect,
                                                            padx=45,pady=15)
        self.frame_input.labelModeLiquide.grid(row=3, column=3)
        self.frame_input.labelModeFrotti=ctk.CTkLabel(self.frame_input, text="Prélèvement Frotti",font=("arial", 15),
                                                      text_color="black",fg_color=self.CouleurFondNonSelect,
                                                        padx=55,pady=15)
        self.frame_input.labelModeFrotti.grid(row=4, column=3)
        

        #Divers
        #Etat prvlmt
        self.frame_input.labelEtatPrvlmt = ctk.CTkLabel(self.frame_input, text="Etat des prélèvements",font=("Verdana", 15, "bold"),
                                                                text_color="black",fg_color="dark grey",
                                                                padx=25,pady=15,corner_radius=18)
        self.frame_input.labelEtatPrvlmt.grid(row=0, column=4)
        self.frame_input.labelPrlmt1=ctk.CTkLabel(self.frame_input, text="Prélèvement 1 ",font=("arial", 15),
                                                            text_color="white",fg_color=self.CouleurFondValid,
                                                            padx=70,pady=15)    
        self.frame_input.labelPrlmt1.grid(row=1, column=4)
        self.frame_input.labelPrlmt2=ctk.CTkLabel(self.frame_input, text="Prélèvement 2 ",font=("arial", 15),
                                                            text_color="white",fg_color=self.CouleurFondValid,
                                                            padx=70,pady=15)
        self.frame_input.labelPrlmt2.grid(row=2, column=4)
        self.frame_input.labelPrlmt3=ctk.CTkLabel(self.frame_input, text="Prélèvement 3 ",font=("arial", 15),
                                                            text_color="white",fg_color=self.CouleurFondValid,
                                                            padx=70,pady=15)
        self.frame_input.labelPrlmt3.grid(row=3, column=4)
        
        
        #Etat Pompe peristaltique
        self.frame_input.labelPompePeristaltique = ctk.CTkLabel(self.frame_input, text="Etat Pompe Péristaltique",font=("Verdana", 15, "bold"),
                                                                text_color="black",fg_color="dark grey",
                                                                padx=25,pady=15,corner_radius=18)
        self.frame_input.labelPompePeristaltique.grid(row=5, column=3)
        self.frame_input.labelEtatPompePeristaltique=ctk.CTkLabel(self.frame_input, text="Init",font=("arial", 15),
                                                                text_color="white",fg_color=self.CouleurFondValid,
                                                                padx=100,pady=15)
        self.frame_input.labelEtatPompePeristaltique.grid(row=6, column=3)
        
        
        #Eclairage
        self.frame_input.labelEclairage = ctk.CTkLabel(self.frame_input, text="Etat Eclairage",font=("Verdana", 15, "bold"),
                                                        text_color="black",fg_color="dark grey",
                                                        padx=65,pady=15,corner_radius=18)
        self.frame_input.labelEclairage.grid(row=5, column=4)
        self.frame_input.labelEtatEclairage=ctk.CTkLabel(self.frame_input, text="init",font=("arial", 15),
                                                            text_color="white",fg_color=self.CouleurFondValid,
                                                            padx=100,pady=15)
        self.frame_input.labelEtatEclairage.grid(row=6, column=4)

        
        #Partie log/etat actuel
        self.frame_log = ctk.CTkFrame(self)
        self.frame_log.grid(row=1, column=0, sticky="nsew")
        self.frame_log.grid_columnconfigure((0), weight=1)
        self.frame_log.grid_columnconfigure((1,2), weight=3)
        self.frame_log.grid_rowconfigure((0), weight=0)
        self.frame_log.grid_rowconfigure((1), weight=1)
        
        #frame Etat actuel
        self.frameEtatActuel = ctk.CTkFrame(self.frame_log)
        self.frameEtatActuel.grid(row=1, column=0, sticky="nsew")
        self.frameEtatActuel.grid_rowconfigure((0,1), weight=4)
        self.frameEtatActuel.grid_rowconfigure((2,3,4,5), weight=2)
        self.frameEtatActuel.grid_columnconfigure((0), weight=1)
        #Etat Actuel
        self.frame_log.labelEtatActuel = ctk.CTkLabel(self.frame_log, text="Etat Actuel",font=("Verdana", 15, "bold"),
                                                        text_color="black",fg_color="dark grey",
                                                        padx=25,pady=15,corner_radius=18)
        self.frame_log.labelEtatActuel.grid(row=0, column=0)
        
        self.labelEtatActuel1=ctk.CTkLabel(self.frameEtatActuel,  text="init ",font=("arial", 15),
                                                            text_color="black",fg_color=self.CouleurFondNonSelect,
                                                            padx=0,pady=25)
        self.labelEtatActuel1.grid(row=0, column=0,sticky="ew")
        self.labelEtatActuel2=ctk.CTkLabel(self.frameEtatActuel, text="init ",font=("arial", 15),
                                                            text_color="black",fg_color=self.CouleurFondNonSelect,
                                                            padx=0,pady=25)
        self.labelEtatActuel2.grid(row=2, column=0,sticky="ew")
        
        #Log defaut
        self.frame_log.labelLogDefaut = ctk.CTkLabel(self.frame_log, text="Log Défauts Actifs",font=("Verdana", 15, "bold"),
                                                        text_color="black",fg_color="dark grey",
                                                        padx=25,pady=15,corner_radius=18)
        self.frame_log.labelLogDefaut.grid(row=0, column=1)
        self.frame_log.LogDefaut = ctk.CTkTextbox(self.frame_log,font=("arial", 15),
                                                text_color="dark grey",fg_color='light blue')
        self.frame_log.LogDefaut.grid(row=1, column=1,sticky="nsew")
        
        #log infos
        self.frame_log.labelLogInfos=ctk.CTkLabel(self.frame_log, text="Log Infos",font=("Verdana", 15, "bold"),
                                                        text_color="black",fg_color="dark grey",
                                                        padx=25,pady=15,corner_radius=18)
        self.frame_log.labelLogInfos.grid(row=0, column=2)
        self.frame_log.LogInfos = ctk.CTkTextbox(self.frame_log,font=("arial", 15),
                                                text_color="dark grey",fg_color="light grey")
        self.frame_log.LogInfos.grid(row=1, column=2,sticky="nsew")
 
        self.UpdateLogDefaut()
        self.UpdateLoginfo()
        
        self.Fonction_clignotante() # démarre la fonction clignotante
        print("fin init creation IHM")
        
        #self.mainloop() #ne pas remettre pb de thread; le mettre dans subscriber
        

    def Fonction_clignotante(self):
        self.bitClignotant = not self.bitClignotant
        self.after(500, self.Fonction_clignotante)
        self.comparaisonValeurAxeTheoReel() #Verif tolerance val axe
        self.UpdateElementClignotant()
        
    
    def comparaisonValeurAxeTheoReel(self):
        deltaAxe1 = abs(self.ValeurTheoAxe1 - self.ValeurReelAxe1) #calcul delta axe 1
        deltaAxe2 = abs(self.ValeurTheoAxe2 - self.ValeurReelAxe2)
        deltaAxe3 = abs(self.ValeurTheoAxe3 - self.ValeurReelAxe3)
        deltaAxe4 = abs(self.ValeurTheoAxe4 - self.ValeurReelAxe4)
        deltaAxe5 = abs(self.ValeurTheoAxe5 - self.ValeurReelAxe5)
        
        if deltaAxe1 > self.toleranceEcartValAxe :
            self.AlarmeAxe1 = True
        else :
            self.AlarmeAxe1 = False
        if deltaAxe2 > self.toleranceEcartValAxe :
            self.AlarmeAxe2 = True
        else :
            self.AlarmeAxe2 = False
        if deltaAxe3 > self.toleranceEcartValAxe :
            self.AlarmeAxe3 = True
        else :
            self.AlarmeAxe3 = False
        if deltaAxe4 > self.toleranceEcartValAxe :
            self.AlarmeAxe4 = True
        else :
            self.AlarmeAxe4 = False
        if deltaAxe5 > self.toleranceEcartValAxe :
            self.AlarmeAxe5 = True
        else :
            self.AlarmeAxe5 = False
        
    def UpdateElementClignotant(self):
        self.frame_log.labelLogDefaut.configure(fg_color= "red" if (self.PresLogDefaut and self.bitClignotant) else "dark grey",
                                                text_color = "white" if (self.bitClignotant and self.PresLogDefaut) else "black")   
        self.frame_input.labelAxe1Reel.configure(fg_color= "red" if (self.AlarmeAxe1 and self.bitClignotant) else "dark grey",
                                                text_color = "white" if (self.AlarmeAxe1 and self.bitClignotant) else "black")
        self.frame_input.labelAxe2Reel.configure(fg_color= "red" if (self.AlarmeAxe2 and self.bitClignotant) else "dark grey",
                                                text_color = "white" if (self.AlarmeAxe2 and self.bitClignotant) else "black")
        self.frame_input.labelAxe3Reel.configure(fg_color= "red" if (self.AlarmeAxe3 and self.bitClignotant) else "dark grey",
                                                text_color = "white" if (self.AlarmeAxe3 and self.bitClignotant) else "black")
        self.frame_input.labelAxe4Reel.configure(fg_color= "red" if (self.AlarmeAxe4 and self.bitClignotant) else "dark grey",
                                                text_color = "white" if (self.AlarmeAxe4 and self.bitClignotant) else "black")
        self.frame_input.labelAxe5Reel.configure(fg_color= "red" if (self.AlarmeAxe5 and self.bitClignotant) else "dark grey",
                                                 text_color = "white" if (self.AlarmeAxe5 and self.bitClignotant) else "black")
        self.frame_input.labelAxe1Demandee.configure(fg_color= "red" if (self.AlarmeAxe1 and self.bitClignotant) else "dark grey",
                                                    text_color = "white" if (self.AlarmeAxe1 and self.bitClignotant) else "black")
        self.frame_input.labelAxe2Demandee.configure(fg_color= "red" if (self.AlarmeAxe2 and self.bitClignotant) else "dark grey",
                                                    text_color = "white" if (self.AlarmeAxe2 and self.bitClignotant) else "black")
        self.frame_input.labelAxe3Demandee.configure(fg_color= "red" if (self.AlarmeAxe3 and self.bitClignotant) else "dark grey",
                                                    text_color = "white" if (self.AlarmeAxe3 and self.bitClignotant) else "black")
        self.frame_input.labelAxe4Demandee.configure(fg_color= "red" if (self.AlarmeAxe4 and self.bitClignotant) else "dark grey",
                                                    text_color = "white" if (self.AlarmeAxe4 and self.bitClignotant) else "black")
        self.frame_input.labelAxe5Demandee.configure(fg_color= "red" if (self.AlarmeAxe5 and self.bitClignotant) else "dark grey",
                                                    text_color = "white" if (self.AlarmeAxe5 and self.bitClignotant) else "black")
        
        
    def UpdateLogDefaut(self):
        i = 0
        LongNumDefaut = ''
        ListLog = []
        ListTitre = []
        self.frame_log.LogDefaut.delete(1.0,tk.END)
        ListTitre, ListLog=self.ReaderCSV.ReadCSVAndPrint(self.pathLogDefaut)
        self.frame_log.LogDefaut.insert('end',ListTitre[0]+ '               '+ ListTitre[1]+ '   '+ListTitre[2]+ '    '+ListTitre[3] + '\n') #insertion des titres
        for row in ListLog :
            if int(ListLog[i][2]) < 10 :
                LongNumDefaut = str('   ')
            if int(ListLog[i][2]) < 100 and int(ListLog[i][2]) >= 10 :
                LongNumDefaut = str(' ')
            self.frame_log.LogDefaut.insert('end', ListLog[i][0] + '   '+ ListLog[i][1]+ '          '+ ListLog[i][2]+ LongNumDefaut + '             '+ ListLog[i][3] + '\n')
            i += 1
        self.PresLogDefaut = True if i > 0 else False

    def UpdateLoginfo(self):
        i = 0
        LongNumInfo = ''
        ListLog = []
        ListTitre = []
        self.frame_log.LogInfos.delete(1.0,tk.END)
        ListTitre, ListLog=self.ReaderCSV.ReadCSVAndPrint(self.pathLogInfo)
        self.frame_log.LogInfos.insert('end',ListTitre[0]+ '     '+ ListTitre[1] + '\n') #insertion des titres
        for row in ListLog :
            if int(ListLog[i][0]) < 10 :
                LongNumInfo = str('   ')
            if int(ListLog[i][0]) < 100 and int(ListLog[i][0]) >= 10 :
                LongNumInfo = str(' ')
            self.frame_log.LogInfos.insert('end', ListLog[i][0] + LongNumInfo + '              '+ ListLog[i][1] + '\n')
            i += 1

    def AjoutLigneCSVDefaut(self,data):
        self.WriterCSV.AddlineCSV(self.pathLogDefaut,data)
        self.UpdateLogDefaut()
        
    def AjoutLigneCSVInfo(self,data):
        self.WriterCSV.AddlineCSV(self.pathLogInfo,data)
        self.UpdateLoginfo()

    def RazDataDefautInfo(self,data):
        self.WriterCSV.RazLogDefaut(self.pathLogDefaut)
        self.WriterCSV.RazLogInfo(self.pathLogInfo)
        self.UpdateLogDefaut()
        self.UpdateLoginfo()

if __name__ == "__main__":
    
    IHM = IHM()
    IHM.mainloop()
    
