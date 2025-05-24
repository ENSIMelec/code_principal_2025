import importlib
import json
import RPi.GPIO as GPIO
import time
import threading
import serial
import logging
import logging.config
import signal
import sys
import matplotlib.pyplot as plt
from LidarScan import LidarScanner
from GraphPlotter import GraphPlotter
from InterfaceGraphique2024.INTERFACE.Interface import *
from Globals_Variables import *
from GraphPlotter_FinMatch import GraphPlotterFinal
from comptage_pts import comptage_pts


class MainCode:
    def __init__(self, json_path="/home/pi/code_principal_2024/Stratégies/StrategieBleuGoTo.json", interface=None):
        self.interface=interface
        self.json_path = json_path
        logging.config.fileConfig(LOGS_CONF_PATH,disable_existing_loggers=False)
        self.logger = logging.getLogger('Main')
        self.thread_action = None
        self.lidar_scanner = None
        self.graph_plotter = None
        self.dic_class = {}
        self.data = None

        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)


        self.logger.info("Main Code initialized.")

    # def lire_serial_stm32(self):
    #     while True:
    #         try:
    #             if self.ser.in_waiting > 0:
    #                 ligne = self.ser.readline().decode(errors="ignore").strip()
    #                 if ligne:
    #                     print(f"[STM32] {ligne}")
    #         except Exception as e:
    #             print(f"[STM32] Erreur lecture série : {e}")

    def lire_serial_stm32(self):
        while True:
            try:
                if self.ser.in_waiting > 0:
                    #ligne = self.ser.readline().decode(errors="ignore").strip()
                    ligne = self.ser.readline().decode("utf-8", errors="replace").strip()

                    if ligne:
                        print(f"[STM32] {ligne}")

                        # 🔍 Traitement des ticks finaux
                        if ligne.startswith("TICKS_RESULT:"):
                            try:
                                valeurs = ligne.replace("TICKS_RESULT:", "").split(",")
                                ticks_g = int(valeurs[0])
                                ticks_d = int(valeurs[1])

                                self.dic_class['Asserv'].ticks_G = ticks_g
                                self.dic_class['Asserv'].ticks_D = ticks_d

                                print(f"Ticks reçus : G={ticks_g} | D={ticks_d}")
                            except Exception as e:
                                print(f"[STM32] Erreur parsing TICKS_RESULT : {e}")

            except Exception as e:
                print(f"[STM32] Erreur lecture série : {e}")


    def init_json(self):
        self.logger.info("Initialisation du JSON...")
        with open(self.json_path) as f:
            self.data = json.load(f)
        self.dic_class = {}
        for module_name in self.data['initialisation']:
            if module_name.startswith('AX12'):
                module = importlib.import_module('AX12_Python.' + module_name)
            else:
                module = importlib.import_module(module_name)
            self.logger.info(f"Initialisation de {module}")
            self.dic_class[module_name] = getattr(module, module_name)(interface=self.interface)
        self.logger.info("JSON initialisé.")
        return True

    def actions(self):
        if self.interface == None :
            for action in self.data['actions']:
                self.logger.debug(f"Action {action['methode']} de la classe {action['classe']} avec les arguments {action['arguments']}")
                while not(getattr(self.dic_class[action['classe']], action['methode'])(*action['arguments'])):
                    time.sleep(0.1)
        else :
            for action in self.data['actions']:
                self.logger.debug(f"Action {action['methode']} de la classe {action['classe']} avec les arguments {action['arguments']}")
                # self.interface.after(0, self.interface.update_action(action['methode']))
                self.interface.after(0, lambda m=action['methode']: self.interface.update_action(m))

                while not(getattr(self.dic_class[action['classe']], action['methode'])(*action['arguments'])):
                    time.sleep(0.1)

       
    def check_jack_removed(self):
        jack_state = GPIO.input(PIN_JACK)
        if jack_state == GPIO.HIGH:
            self.logger.info("Jack retiré")
            if self.interface != None :
                self.interface.after(0, self.interface.jack_retired)
                self.interface.after(0, self.interface.mainStart)
                self.interface.after(500, self.interface.clear_jack_message)

            return True
        else:
            # self.logger.debug("Jack non retiré")
            return False

    def signal_handler(self, sig, frame):
        # Arrêter les moteurs
        self.logger.warning("Vous avez appuyé sur Ctrl+C !")
        self.stop()
        sys.exit(0)

    def set_graph_plotter(self, graph_plotter):
        self.graph_plotter = graph_plotter

    def stop(self):
        if self.interface == None :
            self.logger.info("Arrêt des moteurs")
            self.dic_class['Asserv'].stopmove()
            # Arrêter le scanner Lidar

            # Étape 1 : désactiver le scan Lidar en douceur
            self.lidar_scanner.disable()
            self.logger.info("Attente de l'arrêt propre du thread lidar...")
            time.sleep(0.3)  # Laisser le temps au thread de quitter la boucle

            # Étape 2 : arrêt matériel complet du Lidar
            self.logger.info("Arrêt du scanner Lidar")
            self.lidar_scanner.stop_lidarScan()

            self.logger.info("Arrêt du thread Action")
            if self.thread_action and self.thread_action.is_alive():
                self.thread_action.join()
        else :
            self.interface.after(0, self.interface.mainStop())
            self.logger.info("Arrêt des moteurs")
            self.dic_class['Asserv'].stopmove()
            # Arrêter le scanner Lidar

            # Étape 1 : désactiver le scan Lidar en douceur
            self.lidar_scanner.disable()
            self.logger.info("Attente de l'arrêt propre du thread lidar...")
            time.sleep(0.3)  # Laisser le temps au thread de quitter la boucle

            # Étape 2 : arrêt matériel complet du Lidar
            self.logger.info("Arrêt du scanner Lidar")
            self.lidar_scanner.stop_lidarScan()

            self.logger.info("Arrêt du thread Action")
            if self.thread_action and self.thread_action.is_alive():
                self.thread_action.join()

    def plot_asserv_data(self):
        """Affichage du graphe à la fin"""
        self.logger.info("Affichage des graphes Asserv")

        asserv = self.dic_class['Asserv']

        # Nettoyage des données
        x = [v for v in asserv.x if v is not None]
        y = [v for v in asserv.y if v is not None]
        angle = [v for v in asserv.angle if v is not None]
        vitesse_g = [v for v in asserv.vitesse_G if v is not None]
        vitesse_d = [v for v in asserv.vitesse_D if v is not None]

        plt.figure()
        plt.plot(x, y, label="Trajectoire X-Y")
        plt.xlabel("X (mm)")
        plt.ylabel("Y (mm)")
        plt.legend()

        plt.figure()
        plt.plot(angle, label="Angle mesuré")
        plt.xlabel("Échantillons")
        plt.ylabel("Angle (°)")
        plt.legend()

        plt.figure()
        plt.plot(vitesse_g, label="Vitesse Gauche")
        plt.plot(vitesse_d, label="Vitesse Droite")
        plt.xlabel("Échantillons")
        plt.ylabel("Vitesse")
        plt.legend()

        plt.show()

    def run(self):
        if self.interface == None :
            GPIO.setmode(GPIO.BCM)
            self.logger.info("Initialisation broche GPIO Jack")
            GPIO.setup(PIN_JACK, GPIO.IN)

            self.init_json()
            self.logger.info("Activation du debug pour Asserv")
            self.dic_class['Asserv'].debug_enable()


            self.logger.info("Initialisation du Lidar")
            self.lidar_scanner = LidarScanner()
            self.logger.info("Don de asserv à Lidar")
            self.lidar_scanner.set_asserv_obj(self.dic_class['Asserv'])
            self.dic_class["Lidar"] = self.lidar_scanner


            # #Ajout pour graphPlotter
            # self.graph_plotter = GraphPlotter(graph_config=2)
            # self.graph_plotter.set_asserv_obj(self.dic_class['Asserv'])
            # #self.graph_plotter.run(blocking=True)
            # self.graph_plotter.run()
            # self.after(100, self.update_graph)

            # #fin modif pour graphPlotter

            signal.signal(signal.SIGINT, lambda sig, frame: self.signal_handler(sig,frame))
            signal.signal(signal.SIGTERM, lambda sig, frame: self.signal_handler(sig,frame))

            lidar_thread = threading.Thread(target=self.lidar_scanner.scan)
            lidar_thread.daemon = True
            # self.logger.info("Démarrage du thread de scanner Lidar")
            # lidar_thread.start()

            self.logger.info("Waiting for jack removal...")
            while not self.check_jack_removed():
                time.sleep(0.1)

            time_launch = time.time()
            self.logger.info(f"Démarrage du robot à {time_launch} secondes")

            self.thread_action = threading.Thread(target=self.actions)
            self.thread_action.daemon = True
            time.sleep(0.5)
            self.logger.info("Démarrage du thread d'actions")
            self.thread_action.start()

            self.logger.info("Démarrage du chrono")

            while time.time() < (time_launch + MATCH_TIME) and self.thread_action.is_alive():
                self.logger.debug(f"Match en cours... (T = {time.time()-time_launch})")
                #ajout pour write asserv data
                #self.write_asserv_data(self.dic_class['Asserv'])
                time.sleep(0.1)

            self.logger.info("Fin du match ou chrono")

            time.sleep(1)
            self.stop()


            print("\n--- DEBUG BUFFER DISTANCE ---")
            print("Distance mesurée :", [v for v in self.dic_class['Asserv'].distance if v is not None])
            # print("Distance mesurée gauche :", [v for v in self.dic_class['Asserv'].vitesse_G if v is not None])
            # print("Distance mesurée droite :", [v for v in self.dic_class['Asserv'].vitesse_D if v is not None]) 

            # # print("Correction PID gauche :", [v for v in self.dic_class['Asserv'].Output_PID_vitesse_G if v is not None])
            # # print("Correction PID droite :", [v for v in self.dic_class['Asserv'].Output_PID_vitesse_D if v is not None])

            # print("Correction PID :", [v for v in self.dic_class['Asserv'].Output_PID_distance if v is not None])
            # print("Commande Cible :", [v for v in self.dic_class['Asserv'].cmd_distance if v is not None])

            # # print("Commande Cible gauche :", [v for v in self.dic_class['Asserv'].cmd_vitesse_G if v is not None])
            # # print("Commande Cible droite :", [v for v in self.dic_class['Asserv'].cmd_vitesse_D if v is not None])

            # print("--------------------------------")


            # #Ajout pour le plot du graph
            # self.logger.info("Affichage des graphes PID")
            # graph = GraphPlotterFinal(self.dic_class['Asserv'], graph_config=1)  # 0 = Angle, 1 = Distance, 2 = Vitesses
            # graph.plot()

            print("\n--- DEBUG BUFFER TICKS ---")
            print("Ticks mesurés G :", self.dic_class['Asserv'].ticks_G)
            print("Ticks mesurés D :", self.dic_class['Asserv'].ticks_D)


        else :
            self.interface.after(0, self.interface.mainStart())
            GPIO.setmode(GPIO.BCM)
            self.logger.info("Initialisation broche GPIO Jack")
            GPIO.setup(PIN_JACK, GPIO.IN)

            self.init_json()
            self.logger.info("Activation du debug pour Asserv")
            self.dic_class['Asserv'].debug_enable()


            self.logger.info("Initialisation du Lidar")
            self.lidar_scanner = LidarScanner(self.interface)
            self.logger.info("Don de asserv à Lidar")
            self.lidar_scanner.set_asserv_obj(self.dic_class['Asserv'])

            self.logger.info("Waiting for jack removal...")
            self.interface.after(0, self.interface.waiting_jack)

            while not self.check_jack_removed():
                time.sleep(0.1)
            self.interface.after(0, self.interface.jack_retired)

            time_launch = time.time()
            self.logger.info(f"Démarrage du robot à {time_launch} secondes")

            self.thread_action = threading.Thread(target=self.actions)
            self.thread_action.daemon = True
            lidar_thread = threading.Thread(target=self.lidar_scanner.scan)
            lidar_thread.daemon = True

            time.sleep(0.5)
            self.logger.info("Démarrage du thread d'actions")
            self.thread_action.start()
            # self.logger.info("Démarrage du thread de scanner Lidar")
            # lidar_thread.start()

            self.logger.info("Démarrage du chrono")

            t = time.time()
            while t < (time_launch + MATCH_TIME) and self.thread_action.is_alive():
                # self.logger.debug(f"Match en cours... (T = {t})")
                self.interface.after(0, self.interface.time_update(t-time_launch))
                #ajout pour write asserv data
                #self.write_asserv_data(self.dic_class['Asserv'])
                time.sleep(0.1)
                t = time.time()

            self.logger.info("Fin du match ou chrono")

            time.sleep(1)
            self.stop()

# # Utilisation exemple
if __name__ == "__main__":

    #main_code = MainCode("/home/pi/code_principal_2024/Stratégies/Jaune/StrategieFaireGradin.json")
    main_code = MainCode("/home/pi/code_principal_2024/Stratégies/Jaune/StrategieTestAsservissement.json")
    #main_code = MainCode("/home/pi/code_principal_2024/Stratégies/")

    # # Lancer le thread de lecture série STM32
    #serial_thread = threading.Thread(target=main_code.lire_serial_stm32, daemon=True)
    #serial_thread.start()

    main_code.run()
    

# Utilisation exemple
# if __name__ == "__main__":
#     import tkinter as tk
#     import threading
#     from comptage_pts import Application  # Assure-toi que Application est bien ici

#     def lancer_main(interface):
#         main_code = MainCode(
#             json_path="/home/pi/code_principal_2024/Stratégies/Jaune/StrategieTestAsservissement.json",
#             interface=interface
#         )
#         main_code.run()

#     # Initialisation de l'interface Tkinter 
#     root = tk.Tk()
#     app = Application(root)

#     # Lancer MainCode dans un thread pour garder l'interface fluide
#     thread_main = threading.Thread(target=lancer_main, args=(app,))
#     thread_main.start()

#     # Démarrage de la boucle Tkinter
#     root.mainloop()


# if __name__ == "__main__":
#     import tkinter as tk

#     root = tk.Tk()
#     root.withdraw()  # Cache la fenêtre principale car tu n'utilises pas d'interface graphique Tk ici

#     main_code = MainCode("/home/pi/code_principal_2024/Stratégies/StrategieTestAsservissement.json")
#     graph = GraphPlotter(graph_config=2)

#     main_code.set_graph_plotter(graph)

#     def start():
#         main_code.run()

#     def update_graph():
#         graph.update()
#         root.after(100, update_graph)

#     root.after(0, start)
#     graph.run()
#     update_graph()

#     root.mainloop()


