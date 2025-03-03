# scripts/tracking_recognition_pipeline.py
import cv2
import os
import numpy as np
from utils import read_video
from utils import save_video
from trackers import Tracker
from teams_assigner import TeamAssigner
from utils import predict_identity

# Charger le classificateur Haar Cascade pour la détection des visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def draw_triangle(frame, x_min, y_min, x_max):
    """
    Dessine un triangle rouge au-dessus du joueur reconnu.
    """
    center_x = x_min + (x_max - x_min) // 2
    pt1 = (center_x, max(0, y_min - 40))
    pt2 = (center_x - 20, max(0, y_min - 10))
    pt3 = (center_x + 20, max(0, y_min - 10))
    points = [pt1, pt2, pt3]
    cv2.polylines(frame, [np.array(points)], isClosed=True, color=(0, 0, 255), thickness=3)

def run_tracking_recognition(video_path, tracker_model_path, output_video_path, stub_path=None):
    """
    Orchestre le pipeline complet : tracking, attribution d'équipe, reconnaissance faciale,
    annotation (incluant le dessin d'un triangle rouge) et sauvegarde de la vidéo annotée.
    
    Args:
        video_path: Chemin de la vidéo d'entrée.
        tracker_model_path: Chemin vers le modèle YOLO (pour le Tracker).
        output_video_path: Chemin où sauvegarder la vidéo annotée.
        stub_path: (Optionnel) Chemin vers le fichier stub pour les bounding boxes.
    """
    # 1. Lecture de la vidéo
    video_frames = read_video(video_path)
    
    # 2. Tracking avec détection et suivi
    tracker = Tracker(tracker_model_path)
    bounding_boxes = tracker.get_bounding_boxes(video_frames, read_from_stub=(stub_path is not None), stub_path=stub_path)
    
    # 3. Attribution d'équipe
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(bounding_boxes[0])
    for frame_idx, frame_players in enumerate(bounding_boxes):
        for player in frame_players:
            team = team_assigner.get_player_team(player["color"])
            player["team"] = team
            player["team_color"] = team_assigner.team_color[team]
    
    # 4. Reconnaissance faciale sur chaque joueur
    for frame_idx, frame in enumerate(video_frames):
        for player in bounding_boxes[frame_idx]:
            x_min, y_min, x_max, y_max = player["bbox"]
            # Extraire le crop du joueur
            player_crop = frame[y_min:y_max, x_min:x_max]
            # Convertir en niveaux de gris pour la détection de visage
            gray_crop = cv2.cvtColor(player_crop, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=5)
            if len(faces) == 0:
                player["recognized"] = False
                continue
            for (fx, fy, fw, fh) in faces:
                face_crop = player_crop[fy:fy+fh, fx:fx+fw]
                try:
                    predicted_name, conf = predict_identity(face_crop)
                except Exception as e:
                    print(f"Erreur pour le track_id {player.get('id')}: {e}")
                    predicted_name = "Unknown"
                # Si le joueur est reconnu, on note cette information
                if predicted_name == "Antoine Dupont":
                    player["recognized"] = True
                    print(f"✅ Antoine Dupont détecté pour track_id {player.get('id')} en frame {frame_idx} (conf: {conf:.2f})")
                    break
                else:
                    player["recognized"] = False
    
    # 5. Annotation des frames (bounding boxes, labels, équipe, et triangle pour le joueur reconnu)
    for frame_idx, frame in enumerate(video_frames):
        for player in bounding_boxes[frame_idx]:
            x_min, y_min, x_max, y_max = player["bbox"]
            player_id = player["id"]
            confidence = player.get("confidence", 0) * 100
            team = player.get("team", "Unknown")
            team_color = player.get("team_color", (0, 255, 0))
    
            # Dessiner la bounding box et le label de l'équipe/ID
            cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), team_color, 2)
            label = f"{'Referee' if team == 'Referee' else f'Player {player_id} - {team}'} - {confidence:.1f}%"
            cv2.putText(frame, label, (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, team_color, 2)
            # Si le joueur est reconnu (Antoine Dupont), dessiner le triangle rouge
            if player.get("recognized"):
                draw_triangle(frame, x_min, y_min, x_max)
    
    # 6. Sauvegarder la vidéo annotée
    save_video(video_frames, output_video_path, video_path)
    print(f"🎉 Vidéo annotée sauvegardée dans : {output_video_path}")