import time
import logging

class Temps:
    def __init__(self, interface=None):
        self.interface = interface  # Optionnel, utile si tu veux faire des logs plus tard
        self.logger = logging.getLogger("Temps")
        self.time_launch = None
        if self.interface != None :
            self.interface.after(0, self.interface.Temps_initialized)

    def set_time_launch(self, time_launch):
        self.logger.info(f"Time launch reçu : {time_launch}")
        self.time_launch = time_launch

    def attendre_85s(self):
            """Attend que 85 secondes se soient écoulées depuis le lancement du match"""
            if self.time_launch is None:
                self.logger.error("time_launch n'a pas été initialisé.")
                return False

            while True:
                elapsed = time.time() - self.time_launch
                if elapsed >= 85:
                    self.logger.info("85 secondes écoulées, on peut passer à l’action suivante.")
                    return False
                time.sleep(0.1)  # pour éviter de surcharger le CPU

    def pause(self, duree):
        self.logger.info(f"Pause de {duree} secondes...")
        time.sleep(duree)
        self.logger.info(f"Pause terminee")
        return True
