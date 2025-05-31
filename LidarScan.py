import math
from adafruit_rplidar import RPLidar, RPLidarException
from serial import SerialException
from Globals_Variables import *
import logging
import logging.config
import time
from Asserv import Asserv


class LidarScanner(object):
    _instance = None
    def __new__(cls,*args,**kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

#     def __init__(self,interface=None): 
        
#         # Charger la configuration de logging
#         logging.config.fileConfig(LOGS_CONF_PATH,disable_existing_loggers=False)

#         # Créer un logger
#         self.logger = logging.getLogger("Lidar")

#         self.interface=interface
#         self.port_name = LIDAR_SERIAL
#         self.deadzone_distance = 500
#         self.lidar = RPLidar(None, self.port_name, timeout=5)
#         self.detection = False
#         self.logger.info("Lidar initialized.")
#         self.asserv = None
#         self.enable_lidar = True

#         if self.interface != None :
#             self.interface.after(0,self.interface.lidar_initialized())
            
#         self._stop_requested = False


    # def set_pwm(self, value):
    #     self.logger.info(f"Setting PWM value to {value}")
    #     self.lidar.set_pwm(value)

    #VERSION DERNIRE FONCTIONNELLE
    # def scan(self):
    #     self.set_pwm(512)
    #     try:
    #         for scan in self.lidar.iter_scans():
    #             if(not(self.enable_lidar)):
    #                 continue

    #             for (quality, angle, distance) in scan:
    #                 angle_radians = angle * (math.pi / 180)
    #                 # Calculate x-coordinate and y-coordinate based on distance and angle
    #                 if self.asserv != None:
    #                     x_coordinate = (distance + ORIGIN_LIDAR) * math.cos(angle_radians) * self.asserv.signeLidar
    #                 else :
    #                     x_coordinate = (distance + ORIGIN_LIDAR) * math.cos(angle_radians)
    #                 y_coordinate = (distance + ORIGIN_LIDAR) * math.sin(angle_radians)
                    
    #                 if (-200 <= y_coordinate <= 200) and (250 < x_coordinate < 450) and (quality > 14): # Filtering by deadzone distance
    #                     self.logger.info(f"Object detected in the deadzone at {distance} mm (x)! {angle}°. {quality}")
    #                     if not self.detection:
    #                         self.logger.warning(f"Stopping the robot. Object at {x_coordinate} mm (x) and {angle}°")
    #                         if self.asserv != None:
    #                             self.asserv.stopmove()
    #                     self.detection = True
    #                     self.time_detect = time.time()
                            
    #                 elif (self.detection) and (time.time() - self.time_detect) > 0.5 :
    #                     self.logger.info("No more object. Restarting the robot.")
    #                     if self.asserv != None:
    #                         self.asserv.restartmove()
    #                     self.detection = False  
    #     except RPLidarException as error:
    #         self.logger.error(f"RPLidarException : {error}")
    #         self.stop_lidarScan()
    #         # self.lidar = RPLidar(None, self.port_name, timeout=5)
    #         # self.scan()
        
    #     except Exception as error :
    #         self.logger.error(f"Error in LidarScan: {error}")
    #         time.sleep(0.1)

    #     except KeyboardInterrupt:
    #         self.logger.warning("Stopping the lidar scan. (KeyboardInterrupt)")
    #         self.stop_lidarScan()

   
    # def stop_lidarScan(self):
    #     self.logger.info("Stopping the lidar scan.")
    #     self.lidar.stop_motor()
    #     self.lidar.stop()
    #     self.lidar.disconnect()

    def __init__(self, interface=None):
        logging.config.fileConfig(LOGS_CONF_PATH, disable_existing_loggers=False)
        self.logger = logging.getLogger("Lidar")
        self.interface = interface
        self.port_name = LIDAR_SERIAL
        self.lidar = RPLidar(None, self.port_name, timeout=5)
        self.asserv = None
        self.enable_lidar = True
        self.logger.info("Lidar initialized.")
        self.direction = "forward"  # par défaut on regarde devant
        if self.interface is not None:
            self.interface.after(0, self.interface.lidar_initialized())

        self._stop_requested = False

    def set_pwm(self, value):
        self.logger.info(f"Setting PWM value to {value}")
        self.lidar.set_pwm(value)

    def scan(self, max_distance=400, half_angle=30):
        """
        Scanne la zone devant ou derrière le robot :
        - Si un objet est détecté dans le cône défini → stopmove()
        - Quand plus rien n’est détecté → restartmove()
        """
        self.logger.info("Début du scan Lidar")

        if self.asserv is None:
            center_angle = 0
        else:
            if self.asserv.signeLidar == 1:
                center_angle = 0
            elif self.asserv.signeLidar == -1:
                center_angle = 180
            else:
                center_angle = 0

        self.set_pwm(512)
        self.detection = getattr(self, "detection", False)
        self.time_detect = getattr(self, "time_detect", 0)

        try:
            for scan in self.lidar.iter_scans():
                for (quality, angle, distance) in scan:
                    if self._stop_requested:
                        self.logger.info("Arrêt propre demandé. Sortie du scan.")
                        break

                    if not scan:
                        continue
                    if quality < 10:
                        continue

                    angle_diff = (angle - center_angle) % 360
                    if angle_diff > 180:
                        angle_diff = 360 - angle_diff

                    if distance <= max_distance and angle_diff <= half_angle:
                        if not self.detection:
                            self.logger.warning(f"Obstacle détecté à {distance} mm, angle {angle}°")
                            #self.set_pwm(0)
                            if self.asserv is not None:
                                self.asserv.stopmove()
                        self.detection = True
                        self.time_detect = time.time()
                    elif self.detection and (time.time() - self.time_detect) > 0.5:
                        self.logger.info("Obstacle disparu, redémarrage.")
                        #self.set_pwm(512)
                        if self.asserv is not None:
                            self.asserv.restartmove()
                        self.detection = False
                #time.sleep(0.05)

        except RPLidarException as error:
            if not self._stop_requested:
                self.logger.error(f"RPLidarException : {error}")
        except Exception as error:
            if not self._stop_requested:
                self.logger.error(f"Error in LidarScan: {error}")
        except KeyboardInterrupt:
            self.logger.warning("Interruption manuelle. Arrêt du lidar.")
            self.stop_lidarScan()


    # #VERSION ELIOT
    # def scan(self, max_distance=500, half_angle=30):
    #     """
    #     Scanne la zone devant ou derrière le robot (selon signeLidar) :
    #     - Si un objet est détecté dans le cône défini → stop (pwm=0) et return 1
    #     - Sinon continue (pwm reste à 512) et return 0
    #     """
    #     self.logger.info("Début du scan Lidar")

    #     # Choix de l'angle selon la direction
    #     if self.asserv is None:
    #         center_angle = 0  # défaut = devant
    #     else:
    #         if self.asserv.signeLidar == 1:
    #             center_angle = 0       # en avant
    #         elif self.asserv.signeLidar == -1:
    #             center_angle = 180     # en arrière
    #         else:
    #             center_angle = 0       # par défaut

    #     self.set_pwm(512)  # démarre moteur normalement

    #     try:
    #         for scan in self.lidar.iter_scans():
    #             for (quality, angle, distance) in scan:
    #                 if quality < 15:
    #                     continue  # ignore mesures faibles

    #                 # Calcul de l’écart angulaire
    #                 angle_diff = (angle - center_angle) % 360
    #                 if angle_diff > 180:
    #                     angle_diff = 360 - angle_diff

    #                 # Si dans le cône de détection et à une distance raisonnable
    #                 if distance <= max_distance and angle_diff <= half_angle:
    #                     self.set_pwm(0)  # stop immédiat
    #                     return 1         # détection

    #         return 0  # rien détecté

    #     except Exception as e:
    #         self.logger.error(f"Erreur dans scan_filter : {e}")
    #         self.set_pwm(0)
    #         return 0


    # def stop_lidarScan(self):
    #     self.logger.info("Stopping the lidar scan.")
    #     try:
    #         self.lidar.stop_motor()
    #         self.lidar.stop()
    #         self.lidar.disconnect()
    #     except Exception as e:
    #         self.logger.warning(f"Erreur lors de l'arrêt du lidar : {e}")

    # VERSION PRECEDENTE
    # def scan(self):
    #     self.set_pwm(512)
    #     try:
    #         for scan in self.lidar.iter_scans():
    #             if self._stop_requested:
    #                 self.logger.info("Arrêt propre demandé. Sortie du scan.")
    #                 break

    #             if not scan:
    #                 continue

    #             for (quality, angle, distance) in scan:
    #                 if None in (quality, angle, distance):
    #                     self.logger.warning(f"Valeur invalide dans le scan : q={quality}, a={angle}, d={distance}")
    #                     continue

    #                 angle_radians = angle * (math.pi / 180)
    #                 if self.asserv is not None:
    #                     x_coordinate = (distance + ORIGIN_LIDAR) * math.cos(angle_radians) * self.asserv.signeLidar
    #                 else:
    #                     x_coordinate = (distance + ORIGIN_LIDAR) * math.cos(angle_radians)
    #                 y_coordinate = (distance + ORIGIN_LIDAR) * math.sin(angle_radians)

    #                 if (-200 <= y_coordinate <= 200) and (250 < x_coordinate < 650) and (quality > 14):
    #                     self.logger.info(f"Object detected in the deadzone at {distance} mm (x)! {angle}°. {quality}")
    #                     if not self.detection:
    #                         self.logger.warning(f"Stopping the robot. Object at {x_coordinate} mm (x) and {angle}°")
    #                         if self.asserv is not None:
    #                             self.asserv.stopmove()
    #                     self.detection = True
    #                     self.time_detect = time.time()

    #                 # elif self.detection and (time.time() - self.time_detect) > 0.5:
    #                 #     self.logger.info("No more object. Restarting the robot.")
    #                 #     if self.asserv is not None:
    #                 #         self.asserv.restartmove()
    #                 #     self.detection = False

    #     except RPLidarException as error:
    #         if not self._stop_requested:
    #             self.logger.error(f"RPLidarException : {error}")
    #     except Exception as error:
    #         if not self._stop_requested:
    #             self.logger.error(f"Error in LidarScan: {error}")
    #     except KeyboardInterrupt:
    #         self.logger.warning("Stopping the lidar scan. (KeyboardInterrupt)")
    #         self.stop_lidarScan()
   


   
    def stop_lidarScan(self):
        self._stop_requested = True

        self.logger.info("Stopping the lidar scan.")
        try:
            self.lidar.stop_motor()
        except Exception as e:
            self.logger.warning(f"Erreur lors de stop_motor : {e}")
        try:
            self.lidar.stop()
        except Exception as e:
            self.logger.warning(f"Erreur lors de stop() : {e}")
        try:
            self.lidar.disconnect()
        except Exception as e:
            self.logger.warning(f"Erreur lors de disconnect() : {e}")

    def set_asserv_obj(self, obj):
        self.asserv = obj

    def disable(self):
        self.enable_lidar = False
        return True

    def enable(self):
        self.enable_lidar = True
        return True



if __name__ == '__main__':
    # Setup the RPLidar
    lidar_scanner = LidarScanner()
    # lidar_scanner.disable()
    # time.sleep(10)
    lidar_scanner.stop_lidarScan()

