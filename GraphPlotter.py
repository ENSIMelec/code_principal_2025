import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class GraphPlotter:
    def __init__(self, graph_config=0):
        self.graph_config = graph_config
        self.asserv = None
        self.xdata = []
        self.lines = []
        self.axes = []
        self.figs = []
        self.anims = []

        self.plots_config = {
            0: {"labels": ("Angle Mesuré", "Angle PID", "Commande Angle"), 
                "getters": ("get_angle", "get_output_pid_angle", "get_cmd_angle"), 
                "ylabel": "Angle", 
                "ylim": ("-10", "10")},
            1: {"labels": ("Distance Mesuré", "Distance PID", "Commande Distance"), 
                "getters": ("get_distance", "get_output_pid_distance", "get_cmd_distance"), 
                "ylabel": "Distance", 
                "ylim": ("-1000", "1000")},
            2: {"labels": (
                    ("Speed Mesuré Droit", "Speed PID Droit", "Speed Commande Droit"), 
                    ("Speed Mesuré Gauche", "Speed PID Gauche", "Speed Commande Gauche")
                ), 
                "getters": (
                    ("get_vitesse_d", "get_output_pid_vitesse_d", "get_cmd_vitesse_d"), 
                    ("get_vitesse_g", "get_output_pid_vitesse_g", "get_cmd_vitesse_g")
                ), 
                "ylabel": "Speed (units/s)", 
                "ylim": ("-1000", "1000")}
        }

        if self.graph_config not in self.plots_config:
            raise ValueError("Invalid configuration. Please choose a valid option (0-2).")

        self._setup_plots()

    def set_asserv_obj(self, asserv_obj):
        self.asserv = asserv_obj

    def _setup_plots(self):
        if self.graph_config == 2:
            titles = ["Motor Data - Right", "Motor Data - Left"]
            self.figs = []
            self.axes = []
            self.lines = []
            for idx, title in enumerate(titles):
                fig, ax = plt.subplots()
                fig.suptitle(title)
                self.figs.append(fig)
                self.axes.append(ax)
                labels = self.plots_config[2]["labels"][idx]
                getters = self.plots_config[2]["getters"][idx]
                for label, getter in zip(labels, getters):
                    line, = ax.plot([], [], label=label)
                    self.lines.append((line, getter))
                ax.set_xlabel("Time (s)")
                ax.set_ylabel(self.plots_config[2]["ylabel"])
                ax.set_ylim(int(self.plots_config[2]["ylim"][0]), int(self.plots_config[2]["ylim"][1]))
                ax.set_xlim(0, 100)
                ax.legend()
        else:
            fig, ax = plt.subplots()
            fig.suptitle(self.plots_config[self.graph_config]["ylabel"])
            self.figs = [fig]
            self.axes = [ax]
            labels = self.plots_config[self.graph_config]["labels"]
            getters = self.plots_config[self.graph_config]["getters"]
            for label, getter in zip(labels, getters):
                line, = ax.plot([], [], label=label)
                self.lines.append((line, getter))
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(self.plots_config[self.graph_config]["ylabel"])
            ax.set_ylim(int(self.plots_config[self.graph_config]["ylim"][0]), int(self.plots_config[self.graph_config]["ylim"][1]))
            ax.set_xlim(0, 100)
            ax.legend()

    def _init(self):
        return [line[0] for line in self.lines]

    def _update(self, frame):
        if self.asserv is None:
            return []

        self.xdata.append(frame)
        for line, getter in self.lines:
            new_data = getattr(self.asserv, getter)()
            ydata = list(line.get_ydata())
            ydata.append(new_data)
            line.set_data(self.xdata, ydata)

        if len(self.xdata) > 100:
            for ax in self.axes:
                ax.set_xlim(self.xdata[-100], self.xdata[-1])

        return [line[0] for line in self.lines]

    # def run(self, blocking=True):
    #     for fig in self.figs:
    #         anim = FuncAnimation(fig, self._update, frames=np.arange(0, 2000), init_func=self._init, blit=True)
    #         self.anims.append(anim)

    #     if blocking:
    #         plt.show()

    #     else:
    #         print("plt.show() skipped: this must be called from the main thread.")

    def run(self):
            """Initialise les animations (sans bloquer l'interface)"""
            for fig in self.figs:
                anim = FuncAnimation(fig, self._update, frames=np.arange(0, 2000),
                                    init_func=self._init, blit=True)
                self.anims.append(anim)

            plt.ion()
            plt.show(block=False)

    def update(self):
        """Rafraîchit les graphes (à appeler via .after() depuis Tkinter)"""
        for fig in self.figs:
            fig.canvas.draw_idle()
            fig.canvas.flush_events()