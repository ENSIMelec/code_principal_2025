""""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from Asserv import Asserv  

asserv = Asserv()

times = []
pid_vitesse_g = []
pid_vitesse_d = []
pid_angle = []
pid_distance = []
consigne_vitesse_g = []
consigne_vitesse_d = []
cmd_angle = []
cmd_distance = []

start_time = time.time()

def update_data():
    current_time = time.time() - start_time
    times.append(current_time)
    
    c_vg = asserv.get_cmd_vitesse_g()
    c_vd = asserv.get_cmd_vitesse_d()
    p_vg = asserv.get_output_pid_vitesse_g()
    p_vd = asserv.get_output_pid_vitesse_d()
    a_pid = asserv.get_output_pid_angle()
    d_pid = asserv.get_output_pid_distance()
    
    consigne_vitesse_g.append(c_vg)
    consigne_vitesse_d.append(c_vd)
    pid_vitesse_g.append(p_vg)
    pid_vitesse_d.append(p_vd)
    pid_angle.append(a_pid)
    pid_distance.append(d_pid)

    print(f"Time: {current_time:.2f}s, Consigne VG: {c_vg}, PID VG: {p_vg}, Consigne VD: {c_vd}, PID VD: {p_vd}, PID Angle: {a_pid}, PID Distance: {d_pid}")


def animate(frame):
    update_data()
    ax.clear()
    
    # Tracer les PID pour vitesse, angle et distance sur le même graphique
    ax.plot(times, consigne_vitesse_g, label='Consigne Vitesse Gauche', linestyle='--')
    ax.plot(times, pid_vitesse_g, label='PID Vitesse Gauche')
    ax.plot(times, consigne_vitesse_d, label='Consigne Vitesse Droite', linestyle='--')
    ax.plot(times, pid_vitesse_d, label='PID Vitesse Droite')
    ax.plot(times, pid_angle, label='PID Angle')
    ax.plot(times, pid_distance, label='PID Distance')
    
    ax.set_xlabel('Temps (s)')
    ax.set_ylabel('Valeurs')
    ax.legend(loc='upper right')
    ax.set_title("Courbes PID en temps réel")


fig, ax = plt.subplots()
ani = animation.FuncAnimation(fig, animate, interval=100, cache_frame_data=False, save_count=50)  # mise à jour toutes les 100 ms

plt.show()
"""

import time
from Asserv import Asserv  # Assurez-vous que le chemin est correct

# Instanciez (ou récupérez) l'asservissement
asserv = Asserv()

start_time = time.time()

while True:
    current_time = time.time() - start_time
    
    # Récupération des données depuis l'instance asserv
    c_vg = asserv.get_cmd_vitesse_g()          # Consigne vitesse gauche
    c_vd = asserv.get_cmd_vitesse_d()          # Consigne vitesse droite
    p_vg = asserv.get_output_pid_vitesse_g()     # Sortie PID vitesse gauche
    p_vd = asserv.get_output_pid_vitesse_d()     # Sortie PID vitesse droite
    a_pid = asserv.get_output_pid_angle()        # Sortie PID angle
    d_pid = asserv.get_output_pid_distance()     # Sortie PID distance

    # Affichage des données dans la console
    print(f"Time: {current_time:.2f}s, Consigne VG: {c_vg}, PID VG: {p_vg}, Consigne VD: {c_vd}, PID VD: {p_vd}, PID Angle: {a_pid}, PID Distance: {d_pid}")
    
    # Pause pour ne pas surcharger la console (actualisation toutes les 100ms)
    time.sleep(0.1)
