import pygame
from time import sleep

class Joystick():
    def __init__(self,sleepTime=0.04,keyboard=False) -> None:
        
        self.sleepTime = sleepTime
        self.keboard = keyboard
        
        pygame.joystick.init()
        
        try:
            self.thustmaster = pygame.joystick.Joystick(0)
        except:
            print("no joystick avalable")
            
        pygame.init()
        
        if self.keboard:
            window = pygame.display.set_mode((300, 300))
            rect = pygame.Rect(0, 0, 20, 20)
            rect.center = window.get_rect().center
        
        self.macro_stockage_1_2_3 = 0
        self.macro_repliement = False
        self.macro_position_zero = False
        self.macro_frotti_poussière = False
        self.prelevement_1_2_3 = 0
        self.modification_mode_index = 0
        self.modification_mode_list = ["solide","liquide","frottis","poussière"]
        self.on_off_camera = False
        self.on_off_lumiere = False

        self.effecteur_x_vitesse = 0
        self.effecteur_y_vitesse = 0
        self.effecteur_z_vitesse = 0
        self.effecteur_x_y_and_pince_sensibilite = 2
        self.effecteur_x_y_and_pince_threshold = 0.1
        self.effecteur_z_vitesse_constant = 0.05

        # négatif pour rotation gauche, positif pour rotation droite,
        self.rotation_pince_vitesse = 0
        self.rotation_vitesse_constant = 1
        self.rotation_base_vitesse = 0

        self.degre_ouverture_pince = round((self.thustmaster.get_axis(3)+1)/2,self.effecteur_x_y_and_pince_sensibilite)

        # TODO pub init
    
    def joystickUpdate(self):
        for event in pygame.event.get():
            button_even = ""
            
            if event.type == pygame.KEYDOWN and self.keyboard:
                if event.key == pygame.K_KP1:
                    self.prelevement_1_2_3 = 1
                if event.key == pygame.K_KP2:
                    self.prelevement_1_2_3 = 2
                if event.key == pygame.K_KP3:
                    self.prelevement_1_2_3 = 3
                
                if event.key == pygame.K_KP4:
                    self.macro_stockage_1_2_3 = 1
                if event.key == pygame.K_KP5:
                    self.macro_stockage_1_2_3 = 2
                if event.key == pygame.K_KP6:
                    self.macro_stockage_1_2_3 = 3
                    
            if event.type == pygame.KEYUP and self.keyboard:
                if event.key in (pygame.K_KP1,pygame.K_KP2,pygame.K_KP3):
                    self.prelevement_1_2_3 = 0
                
                if event.key in (pygame.K_KP4,pygame.K_KP5,pygame.K_KP6):
                    self.macro_stockage_1_2_3 = 0
                    
            if event.type == pygame.QUIT:
                exit()

            if event.type == pygame.JOYBUTTONUP:

                # effecteur Z press reset
                if event.dict["button"] in [0,1]:
                    self.effecteur_z_vitesse = 0
                    # TODO pub self.effecteur_z_vitesse
                
                # rotations press reset
                if event.dict["button"] in [2,3]:
                    self.rotation_pince_vitesse = 0
                    # TODO pub self.rotation_pince_vitesse

                # macro stockage reset
                if event.dict["button"] in [4,5,6]:
                    self.macro_stockage_1_2_3 = 0
                    button_even = "Macro stockage : {}".format(self.macro_stockage_1_2_3)
                    # print(button_even)
                    # TODO pub self.macro_stockage_1_2_3
                
                # macro repliement press reset
                if event.dict["button"] == 7:
                    self.macro_repliement = False
                    button_even = "Macro repliement : {}".format(self.macro_repliement)
                    # print(button_even)
                    # TODO pub self.macro_repliement
                
                # macro position zero press reset
                if event.dict["button"] == 8:
                    self.macro_position_zero = False
                    button_even = "Macro position zero : {}".format(self.macro_position_zero)
                    # print(button_even)
                    # TODO pub self.macro_position_zero

                # macro frotti poussière press reset
                if event.dict["button"] == 9:
                    self.macro_frotti_poussière = False
                    button_even = "Macro frotti/poussière : {}".format(self.macro_frotti_poussière)
                    # print(button_even)
                    # TODO pub self.macro_frotti_poussière

                # prélèvement press reset
                if event.dict["button"] in [10,11,12]:
                    self.prelevement_1_2_3 = 0
                    button_even = "Prélèvement : {}".format(self.prelevement_1_2_3)
                    # print(button_even)
                    # TODO pub self.prelevement_1_2_3

            if event.type == pygame.JOYBUTTONDOWN:

                # effecteur Z moins press
                if event.dict["button"] == 0:
                    self.effecteur_z_vitesse = -self.effecteur_z_vitesse_constant
                    # TODO pub self.effecteur_z_vitesse
                
                # effecteur Z plus press
                if event.dict["button"] == 1:
                    self.effecteur_z_vitesse = self.effecteur_z_vitesse_constant
                    # TODO pub self.effecteur_z_vitesse

                # rotation pince gauche press
                if event.dict["button"] == 2:
                    self.rotation_pince_vitesse = -self.rotation_vitesse_constant
                    # TODO pub self.rotation_pince_vitesse

                # rotation pince droite press
                if event.dict["button"] == 3:
                    self.rotation_pince_vitesse = self.rotation_vitesse_constant
                    # TODO pub self.rotation_pince_vitesse

                # macro stockage press
                if event.dict["button"] in [4,5,6]:
                    if event.dict["button"] == 4:
                        self.macro_stockage_1_2_3 = 1
                    elif event.dict["button"] == 5:
                        self.macro_stockage_1_2_3 = 2
                    else:
                        self.macro_stockage_1_2_3 = 3
                    button_even = "Macro stockage : {}".format(self.macro_stockage_1_2_3)
                    # print(button_even)
                    # TODO pub self.macro_stockage_1_2_3

                # macro repliement press
                if event.dict["button"] == 7:
                    self.macro_repliement = True
                    button_even = "Macro repliement : {}".format(self.macro_repliement)
                    # print(button_even)
                    # TODO pub self.macro_repliement

                # macro position zero press
                if event.dict["button"] == 8:
                    self.macro_position_zero = True
                    button_even = "Macro position zero : {}".format(self.macro_position_zero)
                    # print(button_even)
                    # TODO pub self.macro_position_zero

                # macro frotti poussière press
                if event.dict["button"] == 9:
                    self.macro_frotti_poussière = True
                    button_even = "Macro frotti/poussière : {}".format(self.macro_frotti_poussière)
                    # print(button_even)
                    # TODO pub self.macro_frotti_poussière

                # macro stockage press
                if event.dict["button"] in [10,11,12]:
                    if event.dict["button"] == 10:
                        self.prelevement_1_2_3 = 1
                    elif event.dict["button"] == 11:
                        self.prelevement_1_2_3 = 2
                    else:
                        self.prelevement_1_2_3 = 3
                    button_even = "Prélèvement : {}".format(self.prelevement_1_2_3)
                    # print(button_even)
                    # TODO pub self.prelevement_1_2_3

                # mode prélèvement switch
                if event.dict["button"] == 13:
                    self.modification_mode_index += 1
                    if self.modification_mode_index >= 4:
                        self.modification_mode_index = 0
                    button_even = "Mode prélèvement : {}".format(self.modification_mode_list[self.modification_mode_index])
                    # print(button_even)
                    # TODO pub modification_mode

                # camera switch
                if event.dict["button"] == 14:
                    self.on_off_camera = not(self.on_off_camera)
                    button_even = "Camera : {}".format(self.on_off_camera)
                    # print(button_even)
                    # TODO pub self.on_off_camera

                # lumière switch
                if event.dict["button"] == 15:
                    self.on_off_lumiere = not(self.on_off_lumiere)
                    button_even = "Lumière : {}".format(self.on_off_lumiere)
                    # print(button_even)
                    # TODO pub self.on_off_lumiere

            # if event.type == pygame.JOYHATMOTION:
            #     print(self.thustmaster.get_hat(0))

            if event.type == pygame.JOYAXISMOTION:

                if event.dict["axis"] == 0:
                    if self.effecteur_x_vitesse != round(self.thustmaster.get_axis(0),self.effecteur_x_y_and_pince_sensibilite):
                        self.effecteur_x_vitesse = round(self.thustmaster.get_axis(0),self.effecteur_x_y_and_pince_sensibilite)
                        if abs(self.effecteur_x_vitesse) <= self.effecteur_x_y_and_pince_threshold:
                            self.effecteur_x_vitesse = 0
                        # TODO pub self.effecteur_x_vitesse

                if event.dict["axis"] == 1:
                    if self.effecteur_y_vitesse != -round(self.thustmaster.get_axis(1),self.effecteur_x_y_and_pince_sensibilite):
                        self.effecteur_y_vitesse = -round(self.thustmaster.get_axis(1),self.effecteur_x_y_and_pince_sensibilite)
                        if abs(self.effecteur_y_vitesse) <= self.effecteur_x_y_and_pince_threshold:
                            self.effecteur_y_vitesse = 0
                        # TODO pub self.effecteur_y_vitesse

                if event.dict["axis"] == 2:
                    if self.rotation_base_vitesse != -round(self.thustmaster.get_axis(2),self.effecteur_x_y_and_pince_sensibilite):
                        self.rotation_base_vitesse = -round(self.thustmaster.get_axis(2),self.effecteur_x_y_and_pince_sensibilite)
                        if abs(self.rotation_base_vitesse) <= self.effecteur_x_y_and_pince_threshold:
                            self.rotation_base_vitesse = 0
                        # TODO pub self.rotation_base_vitesse
                
                if event.dict["axis"] == 3:
                    if self.degre_ouverture_pince != round((self.thustmaster.get_axis(3)+1)/2,self.effecteur_x_y_and_pince_sensibilite):
                        self.degre_ouverture_pince = round((self.thustmaster.get_axis(3)+1)/2,self.effecteur_x_y_and_pince_sensibilite)
                        # TODO pub self.degre_ouverture_pince
            
            print(" "*100, end="\r")
            print("X : {} Y : {} Z : {} R : {} PINCE : {} BASE : {} BUTTON : {}"
                  .format(str(self.effecteur_x_vitesse).ljust(5),
                          str(self.effecteur_y_vitesse).ljust(5),
                          str(self.effecteur_z_vitesse).ljust(5),
                          str(self.rotation_pince_vitesse).ljust(5),
                          str(self.degre_ouverture_pince).ljust(5),
                          str(self.rotation_base_vitesse).ljust(5),
                          button_even), end="\r")



if __name__ == '__main__':
    joystick = Joystick()
    while True:
        joystick.joystickUpdate()
        sleep(0.1)

