from sklearn.cluster import KMeans
import numpy as np

class TeamAssigner:
    def __init__(self):
        # 🎨 Dictionnaire pour stocker la couleur de chaque groupe
        self.team_color = {"Team_1": None, "Team_2": None, "Referee": None}

    def assign_team_color(self, frame_players):
        """
        🎨 Regrouper les couleurs extraites en 3 groupes :
        - Team 1
        - Team 2
        - Arbitre
        """
        # ✅ Extraire toutes les couleurs des joueurs détectés
        colors = [player["color"] for player in frame_players if "color" in player]

        if not colors:
            return

        # ✅ KMeans pour regrouper en 3 clusters : 2 équipes + arbitre
        jersey_colors_array = np.array(colors)
        kmeans = KMeans(n_clusters=3, random_state=0).fit(jersey_colors_array)
        cluster_centers = kmeans.cluster_centers_
        labels = kmeans.labels_

        # 🎨 Associer chaque cluster à Team_1, Team_2, Referee
        # Hypothèse : L'arbitre porte une couleur distincte (choisie comme le cluster le plus isolé)
        distances = []
        for i in range(3):
            # Somme des distances entre un cluster et les deux autres
            dist = sum(np.linalg.norm(cluster_centers[i] - cluster_centers[j])
                       for j in range(3) if j != i)
            distances.append(dist)

        referee_cluster = np.argmax(distances)  # 🎯 Cluster le plus "isolé"
        other_clusters = [i for i in range(3) if i != referee_cluster]

        self.team_color["Referee"] = tuple(map(int, cluster_centers[referee_cluster]))
        self.team_color["Team_1"] = tuple(map(int, cluster_centers[other_clusters[0]]))
        self.team_color["Team_2"] = tuple(map(int, cluster_centers[other_clusters[1]]))

        print(f"🎨 Couleur Team_1 : {self.team_color['Team_1']}")
        print(f"🎨 Couleur Team_2 : {self.team_color['Team_2']}")
        print(f"🟨 Couleur Arbitre : {self.team_color['Referee']}")

        # 🏷️ Assigner les étiquettes aux joueurs
        for idx, player in enumerate(frame_players):
            cluster_label = labels[idx]
            if cluster_label == referee_cluster:
                player["team"] = "Referee"
                player["team_color"] = self.team_color["Referee"]
            elif cluster_label == other_clusters[0]:
                player["team"] = "Team_1"
                player["team_color"] = self.team_color["Team_1"]
            else:
                player["team"] = "Team_2"
                player["team_color"] = self.team_color["Team_2"]

    def get_player_team(self, player_color):
        """
        🏃 Retourne l'équipe ou "Referee" la plus proche de la couleur du joueur.
        """
        def color_distance(c1, c2):
            return np.linalg.norm(np.array(c1) - np.array(c2))

        distances = {team: color_distance(player_color, color) 
                     for team, color in self.team_color.items()}
        return min(distances, key=distances.get)