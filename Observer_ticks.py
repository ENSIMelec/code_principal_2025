from Asserv import Asserv
import time

asserv = Asserv()
asserv.debug_enable()
asserv.reset_ticks()
asserv.set_position(0, 0, 0)

print("Lecture des ticks en temps réel (Ctrl+C pour quitter)\n")

try:
    while True:
        x = asserv.get_x()
        y = asserv.get_y()
        theta = asserv.get_angle()
        tg = asserv.ticks_G
        td = asserv.ticks_D

        if x is not None and y is not None and theta is not None:
            print(f"Ticks G : {tg} | Ticks D : {td} | x = {x:.1f} mm | y = {y:.1f} mm | θ = {theta:.1f} rad")
        else:
            print(f"Ticks G : {tg} | Ticks D : {td} | Position : en attente de données...")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nArrêt de l'observation.")
    asserv.debug_disable()
