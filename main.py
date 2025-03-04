from utils import read_video, save_video
from trackers import Tracker
from teams_assigner import TeamAssigner
from Rapport import RapportGenerator  # Import du module de génération du rapport

# Fonctions utilitaires pour le calcul du centre d'une bounding box et de la distance
def get_center(bbox):
    x_min, y_min, x_max, y_max = bbox
    return ((x_min + x_max) // 2, (y_min + y_max) // 2)

def compute_distance(center1, center2):
    return ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5

def main():
    # 📹 1. Charger la vidéo
    video_path = "video/video_4.mp4"
    video_frames = read_video(video_path)

    # 🎯 2. Initialiser le tracker (détection + couleurs des joueurs)
    tracker = Tracker('models_weight/yolo11x.pt')
    bounding_boxes = tracker.get_bounding_boxes(
        video_frames, read_from_stub=True, stub_path='stubs/tracks_stubs.pkl'
    )

    # ✅ 3. Initialiser l'assignateur d'équipes
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(bounding_boxes[0])
    for frame_idx, frame_players in enumerate(bounding_boxes):
        for player in frame_players:
            team = team_assigner.get_player_team(player["color"])
            player["team"] = team
            player["team_color"] = team_assigner.team_color[team]

    # 🎥 4. Annoter la vidéo avec les bounding boxes et labels
    output_frames = tracker.draw_annotations(video_frames, bounding_boxes)

    # 💾 5. Sauvegarder la vidéo annotée
    save_video(output_frames, "output_videos/output_video.avi", video_path)
    print("🎉 Vidéo annotée sauvegardée avec succès.")

    # 📊 6. Collecte des statistiques pour le rapport
    unique_players = set()          # Identifiants uniques des joueurs
    recognized_players = set()      # Joueurs dont le visage a été reconnu
    ball_owner_counts = {}          # Compte le nombre de frames où chaque joueur semble posséder le ballon

    for frame_boxes in bounding_boxes:
        ball = None
        players = []
        # Séparer les détections en joueurs et ballon
        for detection in frame_boxes:
            if detection["object_class"] == "Sport Ball":
                ball = detection
            elif detection["object_class"] == "Player":
                players.append(detection)
                unique_players.add(detection["id"])
                if detection.get("face_detected", False):
                    recognized_players.add(detection["id"])
        
        # Si un ballon est détecté et qu'il y a au moins un joueur dans la frame
        if ball and players:
            ball_center = get_center(ball["bbox"])
            closest_player = None
            min_distance = float('inf')
            # Trouver le joueur le plus proche du ballon
            for player in players:
                player_center = get_center(player["bbox"])
                distance = compute_distance(ball_center, player_center)
                if distance < min_distance:
                    min_distance = distance
                    closest_player = player
            if closest_player:
                player_id = closest_player["id"]
                ball_owner_counts[player_id] = ball_owner_counts.get(player_id, 0) + 1

    # Déterminer le joueur ayant le plus souvent le ballon
    if ball_owner_counts:
        overall_ball_owner = max(ball_owner_counts, key=ball_owner_counts.get)
        frames_with_ball = ball_owner_counts[overall_ball_owner]
    else:
        overall_ball_owner = None
        frames_with_ball = 0

    stats = {
        "Nombre de frames traitées": len(video_frames),
        "Nombre de joueurs uniques": len(unique_players),
        "Joueurs reconnus (IDs)": list(recognized_players),
        "Ballon possédé par (ID) et nombre de frames": (overall_ball_owner, frames_with_ball)
    }
    print("Statistiques collectées :", stats)

    # 🤖 7. Générer le rapport via l'API ChatGPT (GPT-3.5)
    # Remplacez "VOTRE_API_KEY" par votre clé API OpenAI (pensez à la sécuriser via une variable d'environnement)
    generator = RapportGenerator(api_key="VOTRE_API_KEY")
    generator.create_rapport(stats, filename="Rapport.txt")

if __name__ == '__main__':
    main()