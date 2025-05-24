import math
import pygame
from Asserv import Asserv
from AX12_Python.AX12_Ascenseur import AX12_Ascenseur
from AX12_Python.AX12_Pinces import AX12_Pinces
from AX12_Python.AX12_Panneau import AX12_Panneau

# [NEW] Device 68:6C:E6:52:41:70 Xbox Wireless Controller

pygame.init()
joysticks = []
clock = pygame.time.Clock()
keepPlaying = True

asserv = Asserv()
asserv.vitesse_enable()

ascenceur = AX12_Ascenseur()
ascenceur_bas = True

pince = AX12_Pinces()
pince.close_pince(32)
pince_ouverte = False
pince_en_fermeture = False

panneau = AX12_Panneau()
panneau_ouvert_droit = False
panneau_ouvert_gauche = False



def convert_to_speed(value, min_input=-1, max_input=1, min_output=350, max_output=-350):
    # Conversion linéaire de l'intervalle [-1, 1] à l'intervalle [-350, 350]
    return min_output + (value - min_input) * (max_output - min_output) / (max_input - min_input)


# for al the connected joysticks
for i in range(0, pygame.joystick.get_count()):
    # create an Joystick object in our list
    joysticks.append(pygame.joystick.Joystick(i))
    # initialize the appended joystick (-1 means last array item)
    joysticks[-1].init()
    # print a statement telling what the name of the controller is
    print ("Detected joystick "),joysticks[-1].get_name(),"'"
while keepPlaying:
    clock.tick(60)
    for event in pygame.event.get():
        # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                print ("A")
                if pince_ouverte and not pince_en_fermeture:
                    pince.close_pince()
                    pince_ouverte = False
                    pince_en_fermeture = True
                elif not pince_ouverte and pince_en_fermeture:
                    pince.close_pince(1024)
                    pince_ouverte = False
                    pince_en_fermeture = False
              *  elif not pince_ouverte and not pince_en_fermeture:
                    pince.open_pince()
            **        pince_ouverte = True
                    pince_en_fermeture = False
            //elif event.button == 1:
                print ("B")
                if ascenceur_bas:
                    ascenceur.elevate()
                else :
                    ascenceur.lower()
                ascenceur_bas = not ascenceur_bas
            elif event.button == 3:
                print ("X")
            elif event.button == 4:
                print ("Y")
            elif event.button == 2:
                print ("double carré (au milieu)")
            elif event.button == 5:
                print ("bouton xbox")
            elif event.button == 9:
                print ("bouton menu je pense")
            elif event.button == 10:
                print ("Joystick gauche pressed")
            elif event.button == 8:
                print ("Joystick droit pressed")
            elif event.button == 6:
                print ("LB")
                if panneau_ouvert_gauche:
                    panneau.ramener_AX12_gauche()
                else :
                    panneau.bouger_panneau_gauche()
                panneau_ouvert_gauche = not panneau_ouvert_gauche
            elif event.button == 7:
                print ("RB")
                if panneau_ouvert_droit:
                    panneau.ramener_AX12_droit()
                else :
                    panneau.bouger_panneau_droit()
                panneau_ouvert_droit = not panneau_ouvert_droit
            elif event.button == 11:
                print ("haut")
                asserv.rotate(0)
            elif event.button == 12:
                print ("bas")
                asserv.rotate(-3.1413)
            elif event.button == 13:
                print ("gauche")
                asserv.rotate(-3.1413/2)
            elif event.button == 14:
                print ("droite")
                asserv.rotate(3.1413/2)
            elif event.button == 15:
                print ("bouton partage je pense")
            else:
                print ("Button pressed: ", event.button)

        if event.type == pygame.JOYAXISMOTION:
            # left stick
            if event.axis == 0 :  # Axe X ou Y du joystick gauche
                # On récupère les valeurs de l'axe X (event.axis == 0) et Y (event.axis == 1)
                value_x = joysticks[0].get_axis(0)
                # On affiche les valeurs
                print(f"Joystick gauche X: {value_x:.2f}") 
                if abs(value_x) > 0.1:
                    # Conversion en vitesse
                    speed = convert_to_speed(value_x)
                if abs(value_x) < 0.1:
                    speed = 0
                print(f"Angle vitesse: {speed:.4f}")
                asserv.manette_angle(speed)

            # right stick
            if event.axis == 3:  # Axe X ou Y du joystick gauche
                # On récupère les valeurs de l'axe X (event.axis == 0) et Y (event.axis == 1)
                value_y1 = joysticks[0].get_axis(3)
                # On affiche les valeurs
                print(f"Joystick droit Y: {value_y1:.2f}")
                if abs(value_y1) > 0.1:
                    # Conversion en vitesse
                    speed = convert_to_speed(value_y1, -1, 1, 500, -500)
                if abs(value_y1) < 0.1:
                    speed = 0
                print(f"Line vitesse: {speed:.4f}")
                asserv.manette_line(speed)
