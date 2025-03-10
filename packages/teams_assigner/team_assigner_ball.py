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
        - Arbitre (choisi comme le groupe avec le moins de joueurs)

        Ajout : si l'objet est un ballon (par exemple player["object_class"] == "Sport Ball"),
        on l'ignore dans le regroupement et on ne modifie pas son annotation.
        """
        # 1. Construction d'une liste des indices de joueurs humains (on exclut le ballon)
        valid_indices = []
        colors = []
        for idx, player in enumerate(frame_players):
            # Condition : si c'est un ballon, on passe
            if player.get("object_class") == "Sport Ball":
                continue
            # On ne prend que ceux qui ont une clé "color"
            if "color" in player:
                valid_indices.append(idx)
                colors.append(player["color"])

        # S'il n'y a aucune couleur à traiter, on s'arrête
        if not colors:
            return

        # 2. KMeans pour regrouper en 3 clusters : 2 équipes + arbitre
        jersey_colors_array = np.array(colors)
        kmeans = KMeans(n_clusters=3, random_state=0).fit(jersey_colors_array)
        cluster_centers = kmeans.cluster_centers_
        labels = kmeans.labels_

        # 3. Identifier le cluster avec le moins de joueurs comme arbitre
        unique, counts = np.unique(labels, return_counts=True)
        cluster_counts = dict(zip(unique, counts))
        referee_cluster = min(cluster_counts, key=cluster_counts.get)
        other_clusters = [i for i in range(3) if i != referee_cluster]

        self.team_color["Referee"] = tuple(map(int, cluster_centers[referee_cluster]))
        self.team_color["Team_1"] = tuple(map(int, cluster_centers[other_clusters[0]]))
        self.team_color["Team_2"] = tuple(map(int, cluster_centers[other_clusters[1]]))

        print(f"🎨 Couleur Team_1 : {self.team_color['Team_1']}")
        print(f"🎨 Couleur Team_2 : {self.team_color['Team_2']}")
        print(f"🟨 Couleur Arbitre : {self.team_color['Referee']}")

        # 4. Assigner les étiquettes uniquement aux joueurs humains
        for idx_label, idx_player in enumerate(valid_indices):
            player = frame_players[idx_player]
            cluster_label = labels[idx_label]

            if cluster_label == referee_cluster:
                player["team"] = "Referee"
                player["team_color"] = self.team_color["Referee"]
            elif cluster_label == other_clusters[0]:
                player["team"] = "Team_1"
                player["team_color"] = self.team_color["Team_1"]
            else:
                player["team"] = "Team_2"
                player["team_color"] = self.team_color["Team_2"]

        # Remarque : 
        # Les objets de type "Sport Ball" ne sont pas modifiés (pas de "team" ni "team_color" assignés).
        # Leur annotation de base est donc conservée.

    def get_player_team(self, player_color):
        """
        🏃 Retourne l'équipe ou "Referee" la plus proche de la couleur du joueur.
        """
        def color_distance(c1, c2):
            return np.linalg.norm(np.array(c1) - np.array(c2))

        distances = {
            team: color_distance(player_color, color)
            for team, color in self.team_color.items()
            if color is not None  # au cas où une couleur n'est pas encore définie
        }

        # Si aucun cluster n’a encore été défini (cas extrême), on peut retourner None
        if not distances:
            return None

        return min(distances, key=distances.get)