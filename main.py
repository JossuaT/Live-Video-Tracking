import cv2
import os
import pickle
from utils import read_video, save_video
from trackers import Tracker
from teams_assigner import TeamAssigner
from rapport import RapportGenerator, generate_heatmap
from config import API_KEY

def get_center(bbox):
    x_min, y_min, x_max, y_max = bbox
    return ((x_min + x_max) // 2, (y_min + y_max) // 2)

def compute_distance(center1, center2):
    return ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5

def main():
    video_path = "video/video_4.mp4"
    
    # Calcul de la durée de la vidéo
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration = frame_count / fps if fps != 0 else 0
    cap.release()
    print(f"Durée de la vidéo : {video_duration:.2f} secondes")
    
    # Chargement des frames de la vidéo
    video_frames = read_video(video_path)
    
    # Instanciation du Tracker
    tracker = Tracker('models_weight/yolo11x.pt')
    
    # Définir le chemin du stub
    stub_path = "stubs/tracks_stubs.pkl"
    
    # Récupération des bounding boxes via le stub
    bounding_boxes = tracker.get_bounding_boxes(video_frames, read_from_stub=True, stub_path=stub_path)
    
    # Attribution des équipes
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(bounding_boxes[0])
    for frame_idx, frame_players in enumerate(bounding_boxes):
        for player in frame_players:
            team = team_assigner.get_player_team(player["color"])
            player["team"] = team
            player["team_color"] = team_assigner.team_color[team]
    
    # Annotation des frames
    annotated_frames = tracker.draw_annotations(video_frames, bounding_boxes)
    
    # Sauvegarde de la vidéo annotée
    save_video(annotated_frames, "output_videos/output_video.avi", video_path)
    print("Vidéo annotée sauvegardée avec succès.")
    
    # Partie statistiques
    unique_players = set()
    recognized_players = set()
    ball_owner_counts = {}
    ball_passes = []
    previous_owner = None
    candidate_owner = None
    candidate_count = 0
    stability_threshold = 5

    for frame_boxes in bounding_boxes:
        ball = None
        players = []
        for detection in frame_boxes:
            if detection["object_class"] == "Sport Ball":
                ball = detection
            elif detection["object_class"] == "Player":
                players.append(detection)
                unique_players.add(detection["id"])
                if detection.get("face_detected", False) and detection.get("face_identity") is not None:
                    recognized_players.add(detection["id"])
        if ball and players:
            ball_center = get_center(ball["bbox"])
            closest_player = None
            min_distance = float('inf')
            for player in players:
                player_center = get_center(player["bbox"])
                distance = compute_distance(ball_center, player_center)
                if distance < min_distance:
                    min_distance = distance
                    closest_player = player
            if closest_player:
                current_owner = closest_player["id"]
                ball_owner_counts[current_owner] = ball_owner_counts.get(current_owner, 0) + 1
                if previous_owner is None:
                    previous_owner = current_owner
                else:
                    if current_owner == previous_owner:
                        candidate_owner = None
                        candidate_count = 0
                    else:
                        if candidate_owner == current_owner:
                            candidate_count += 1
                            if candidate_count >= stability_threshold:
                                ball_passes.append((previous_owner, current_owner))
                                previous_owner = current_owner
                                candidate_owner = None
                                candidate_count = 0
                        else:
                            candidate_owner = current_owner
                            candidate_count = 1

    if ball_owner_counts:
        overall_ball_owner = max(ball_owner_counts, key=ball_owner_counts.get)
        frames_with_ball = ball_owner_counts[overall_ball_owner]
    else:
        overall_ball_owner = None
        frames_with_ball = 0

    # Construction du mapping ID -> Nom à partir de recognized_player_ids
    recognized_mapping = {v: k for k, v in tracker.recognized_player_ids.items()}

    stats = {
        "Nombre de frames traitées": len(video_frames),
        "Durée de la vidéo (secondes)": video_duration,
        "Nombre de joueurs uniques": len(unique_players),
        "Joueurs reconnus (IDs)": list(recognized_players),
        "Joueurs reconnus (ID: Nom)": recognized_mapping,
        "Ballon possédé par (ID) et nombre de frames": (overall_ball_owner, frames_with_ball),
        "Passes de ballon (du joueur A vers le joueur B)": ball_passes
    }
    print("Statistiques collectées :", stats)
    
    # Mise à jour du stub avec les nouvelles données
    with open(stub_path, 'wb') as f:
        data = {
            "bounding_boxes": bounding_boxes,
            "recognized_player_ids": tracker.recognized_player_ids,
            "deepface_results": tracker.deepface_results
        }
        pickle.dump(data, f)
    print(f"Stub mis à jour sauvegardé dans {stub_path}")

    # Génération des heatmaps via le module Rapport/heatmap.py
    # Ajustez field_size selon les dimensions de votre vidéo ou terrain
    # N'utiliser que sur des plan de long.
    # generate_heatmap(player_positions, title="Heatmap des positions des joueurs", bins=50, field_size=(1920, 1080))
    # generate_heatmap(ball_positions, title="Heatmap des positions du ballon", bins=50, field_size=(1920, 1080))

    
    # Génération du rapport via ChatGPT
    generator = RapportGenerator(api_key=API_KEY)
    generator.create_rapport(stats, filename="Rapport.txt")
    
if __name__ == '__main__':
    main()