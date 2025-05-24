import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from Asserv import Asserv  # Assuming the class is imported from another file
import numpy as np
import sys

# Parse the command-line argument
try:
    graph_config = int(sys.argv[1])  # Expecting an integer argument
except (IndexError, ValueError):
    print("Please provide a valid integer argument for the graph configuration.")
    sys.exit(1)

# Initialize the Asserv class
asserv = Asserv()

# Define plot configurations
plots_config = {
    0: {"labels": ("Angle Mesuré", "Angle PID", "Commande Angle"), "getters": ("get_angle", "get_output_pid_angle", "get_cmd_angle"), "ylabel": "Angle", "ylim" : ("-10","10")},
    1: {"labels": ("Distance Mesuré", "Distance PID", "Commande Distance"), "getters": ("get_distance", "get_output_pid_distance", "get_cmd_distance"), "ylabel": "Distance", "ylim" : ("-1000","1000")},
    2: {"labels": (
        ("Speed Mesuré Droit", "Speed PID Droit", "Speed Commande Droit"), 
        ("Speed Mesuré Gauche", "Speed PID Gauche", "Speed Commande Gauche")
    ), "getters": (
        ("get_vitesse_d", "get_output_pid_vitesse_d", "get_cmd_vitesse_d"), 
        ("get_vitesse_g", "get_output_pid_vitesse_g", "get_cmd_vitesse_g")
    ), "ylabel": "Speed (units/s)", "ylim" : ("-1000","1000")}
}

# Check if the configuration is valid
if graph_config not in plots_config:
    print("Invalid configuration. Please choose a valid option (0-2).")
    sys.exit(1)

# Prepare the figures and axes
if graph_config == 2:
    # Two separate figures for Right and Left motors
    fig1, ax1 = plt.subplots()
    fig1.suptitle("Motor Data - Right")
    fig2, ax2 = plt.subplots()
    fig2.suptitle("Motor Data - Left")
    axes = [ax1, ax2]
else:
    # Single figure for other data types
    fig, ax = plt.subplots()
    fig.suptitle(plots_config[graph_config]["ylabel"])
    axes = [ax]  # To keep processing consistent

# Initialize line objects for the selected graph(s)
lines = []
for idx, ax in enumerate(axes):
    if graph_config == 2:
        labels = plots_config[graph_config]["labels"][idx]
        getters = plots_config[graph_config]["getters"][idx]
        for label, getter in zip(labels, getters):
            line, = ax.plot([], [], label=label)
            lines.append((line, getter))
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(plots_config[graph_config]["ylabel"])
        ax.legend()
    else:
        labels = plots_config[graph_config]["labels"]
        getters = plots_config[graph_config]["getters"]
        for label, getter in zip(labels, getters):
            line, = ax.plot([], [], label=label)
            lines.append((line, getter))
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(plots_config[graph_config]["ylabel"])
        ax.legend()


# Data cache for x-axis and y-axis values
xdata = []

def init():
    for ax in axes:
        ax.set_xlim(0, 100)
        ax.set_ylim(int(plots_config[graph_config]["ylim"][0]), int(plots_config[graph_config]["ylim"][1]))  # Adjust this range based on expected data range
    return [line[0] for line in lines]

def update(frame):
    xdata.append(frame)
    for line, getter in lines:
        new_data = getattr(asserv, getter)()
        line_data = list(line.get_ydata())
        line_data.append(new_data)
        line.set_data(xdata, line_data)

        # Scroll graph if necessary
        if len(xdata) > 100:
            for ax in axes:
                ax.set_xlim(xdata[-100], xdata[-1])

    return [line[0] for line in lines]

ani = FuncAnimation(fig1 if graph_config == 2 else fig, update, frames=np.arange(0, 2000), init_func=init, blit=True)

plt.show()
