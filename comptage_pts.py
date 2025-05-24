import tkinter as tk

# class Application:
#     def __init__(self, master, interface=None):
#         self.master = master
#         master.title("Comptage de points")

#         self.score_label = tk.Label(master, text="Score actuel : 0")
#         self.score_label.pack()

#         # self.calculs_intermediaires_label = tk.Label(master, text="")
#         self.calculs_intermediaires_label = tk.Label(master,text="",justify="left",anchor="w",font=("Arial", 11),wraplength=400)
#         self.calculs_intermediaires_label.pack(fill="both", expand=True)

#         self.calculs_intermediaires_label.pack()

#     def Comptage_pts_initialized(self):
#         print("[UI] Module comptage_pts initialisé")

#     def mettre_a_jour_score(self, nouveau_score, calcul_intermediaire):
#         print(f"[UI] Mise à jour interface : score = {nouveau_score}")
#         # self.score_label.config(text=f"Score actuel : {nouveau_score}")
#         # self.calculs_intermediaires_label.config(text=calcul_intermediaire)
#         if self.interface and hasattr(self.interface, 'update_score'):
#             self.interface.update_score(self.score)

class comptage_pts:
    def __init__(self, interface=None):
        self.interface = interface
        self.score = 0
        self.historique = [] 
        self.last_displayed_index = 0

        if self.interface and hasattr(self.interface, 'Comptage_pts_initialized'):
            self.interface.Comptage_pts_initialized()

    def mettre_a_jour_score(self):
        print(f"[SCORE] Score actuel : {self.score}")
        
        # nouvelles_lignes = self.historique[self.last_displayed_index:]
        # if not nouvelles_lignes:
        #     print("[DEBUG] Aucune nouvelle ligne à afficher.")
        # else:
        #     for ligne in nouvelles_lignes:
        #         print(ligne, end="")  # chaque ligne a déjà un \n
        #     self.last_displayed_index = len(self.historique)

        # if self.interface and hasattr(self.interface, 'mettre_a_jour_score'):
        #     texte_complet = "".join(self.historique)
        #     self.interface.mettre_a_jour_score(self.score, texte_complet)

        if self.interface and hasattr(self.interface, 'update_score'):
            self.interface.update_score(self.score)
            

    def pts_gradin(self, nombre_etage):
        pts_equivalence_etage = {1: 4, 2: 8, 3: 16}
        points_gradins = pts_equivalence_etage.get(nombre_etage, 0)
        self.score += points_gradins
        # self.historique.append(f"Ajout de {points_gradins} points pour {nombre_etage} étage(s) monté(s)\n")
        self.mettre_a_jour_score()
        return True

    def pts_banderole(self):
        points_banderole = 20
        self.score += points_banderole
        # self.historique.append("Ajout de 20 points pour la promotion avec une banderole\n")
        self.mettre_a_jour_score()
        return True

    def pts_zone_finale(self):
        points_zone_finale = 10
        self.score += points_zone_finale
        # self.historique.append("Ajout de 10 points pour avoir atteint la zone finale\n")
        self.mettre_a_jour_score()
        return True


# if __name__ == "__main__":
#     # Initialisation de Tkinter
#     root = tk.Tk()

#     # Création de l'application
#     app = Application(root)

#     # Exemple d'utilisation
#     comptage = comptage_pts(interface=app)
#     comptage.pts_gradin(2)
#     comptage.pts_banderole()
#     comptage.pts_zone_finale()

#     # Lancement de la boucle principale de Tkinter
#     root.mainloop()
