import time
import logging

class Temps:
    def __init__(self, interface=None):
        self.interface = interface  # Optionnel, utile si tu veux faire des logs plus tard
        self.logger = logging.getLogger("Temps")
        if self.interface != None :
            self.interface.after(0, self.interface.Temps_initialized)

    def pause(self, duree):
        self.logger.info(f"Pause de {duree} secondes...")
        time.sleep(duree)
        self.logger.info(f"Pause terminee")
        return True
