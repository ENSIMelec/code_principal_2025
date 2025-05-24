import matplotlib.pyplot as plt

class GraphPlotterFinal:
    def __init__(self, asserv, graph_config=0):
        self.asserv = asserv
        self.graph_config = graph_config

        self.plots_config = {
            0: {"labels": ("Angle Mesuré", "Correction PID", "Commande Cible"),
                "getters": ("get_angle", "get_output_pid_angle", "get_cmd_angle"),
                "ylabel": "Angle",
                "ylim": (-10, 10)},
            1: {"labels": ("Distance Mesuré", "Correction PID", "Commande Cible"),
                "getters": ("get_distance", "get_output_pid_distance", "get_cmd_distance"),
                "ylabel": "Distance",
                "ylim": (-1000, 1000)},
            2: {"labels": (
                    ("Speed Mesuré Droit", "Correction PID Droit", "Commande Cible Droit"),
                    ("Speed Mesuré Gauche", "Correction PID Gauche", "Commande Cible Gauche")
                ),
                "getters": (
                    ("get_vitesse_d", "get_output_pid_vitesse_d", "get_cmd_vitesse_d"),
                    ("get_vitesse_g", "get_output_pid_vitesse_g", "get_cmd_vitesse_g")
                ),
                "ylabel": "Speed (units/s)",
                "ylim": (-1000, 1000)}
        }

    def plot(self):
        buffer_mapping = {
            "get_angle": "angle",
            "get_output_pid_angle": "Output_PID_angle",
            "get_cmd_angle": "cmd_angle",
            "get_distance": "distance",
            "get_output_pid_distance": "Output_PID_distance",
            "get_cmd_distance": "cmd_distance",
            "get_vitesse_d": "vitesse_D",
            "get_output_pid_vitesse_d": "Output_PID_vitesse_D",
            "get_cmd_vitesse_d": "cmd_vitesse_D",
            "get_vitesse_g": "vitesse_G",
            "get_output_pid_vitesse_g": "Output_PID_vitesse_G",
            "get_cmd_vitesse_g": "cmd_vitesse_G"
        }
        if self.graph_config == 2:
            titles = ["PID Vitesse - Droit", "PID Vitesse - Gauche"]
            for idx, title in enumerate(titles):
                fig, ax = plt.subplots()
                fig.suptitle(title)
                labels = self.plots_config[2]["labels"][idx]
                getters = self.plots_config[2]["getters"][idx]
                for label, getter in zip(labels, getters):
                    buffer_name = buffer_mapping[getter]
                    y_data = getattr(self.asserv, buffer_name)
                    y_data = [v for v in y_data if v is not None]
                    #ajout
                    x_data = list(range(len(y_data)))
                    #
                    ax.plot(range(len(y_data)), y_data, label=label, linewidth=1.5)
                ax.set_xlabel("Échantillons")
                ax.set_ylabel(self.plots_config[2]["ylabel"])
                ax.grid(True, linestyle="--", alpha=0.7)
                #ax.set_ylim(self.plots_config[2]["ylim"])
                ax.legend()
                all_y = []
                for getter in getters:
                    buffer_name = buffer_mapping[getter]
                    all_y += [v for v in getattr(self.asserv, buffer_name) if v is not None]
                if all_y:
                    ymin = min(all_y) - 10
                    ymax = max(all_y) + 10
                    ax.set_ylim(ymin, ymax)
        else:
            #fig, ax = plt.subplots()
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.suptitle(self.plots_config[self.graph_config]["ylabel"])
            labels = self.plots_config[self.graph_config]["labels"]
            getters = self.plots_config[self.graph_config]["getters"]
            for label, getter in zip(labels, getters):
                buffer_name = buffer_mapping[getter]
                y_data = getattr(self.asserv, buffer_name)
                y_data = [v for v in y_data if v is not None]
                #ajout
                x_data = list(range(len(y_data)))
                #
                #ax.plot(range(len(y_data)), y_data, label=label, linewidth=1.5)
                if "Correction" in label:
                    ax.plot(x_data, y_data, label=label, linestyle="--", linewidth=2, color="green")
                elif "Cible" in label:
                    ax.plot(x_data, y_data, label=label, linestyle="--", color="black", linewidth=1.5)
                elif "Mesuré" in label:
                    ax.plot(x_data, y_data, label=label, color="orange", linewidth=2.5)
                else:
                    ax.plot(x_data, y_data, label=label, linewidth=1.5)
            ax.set_xlabel("Échantillons")
            ax.set_ylabel(self.plots_config[self.graph_config]["ylabel"])
            ax.grid(True, linestyle="--", alpha=0.7)
            ax.legend()
            # Échelle dynamique
            all_y = []
            for getter in getters:
                buffer_name = buffer_mapping[getter]
                all_y += [v for v in getattr(self.asserv, buffer_name) if v is not None]
            if all_y:
                ymin = min(all_y) - 10
                ymax = max(all_y) + 10
                ax.set_ylim(ymin, ymax)

        plt.show()
