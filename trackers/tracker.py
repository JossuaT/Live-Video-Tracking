from ultralytics import YOLO
import supervision as sv
import pickle
import os
import cv2
import sys
sys.path.append('../')
from utils import get_bbox_width, get_center_of_bbox, extract_dominant_color
import numpy as np
from PIL import Image
from supervision import BoxAnnotator, LabelAnnotator, Color

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.tracked_players = {}  # Store tracked players info across frames

        # ✅ Initialiser les annotateurs
        self.box_annotator = BoxAnnotator(color=Color.RED)  # Couleur de la bounding box
        self.label_annotator = LabelAnnotator(text_color=Color.WHITE)  # Couleur du texte

    def detect_and_track_frames(self, frames, conf=0.25, imgsz=1280, classes=[0, 32]):
        """Détecte et suit les joueurs sur toutes les frames avec YOLO et ByteTrack."""
        all_tracked_boxes = []
        
        for frame_idx, frame in enumerate(frames):
            # Convert frame path to image if necessary
            if isinstance(frame, str):
                frame = cv2.imread(frame)
            
            # Get detections for current frame
            detections = self.model.predict(frame, conf=conf, imgsz=imgsz, classes=classes)[0]
            
            # Convert detections to supervision format
            detections_sv = sv.Detections.from_ultralytics(detections)
            
            # Track detections
            tracked_detections = self.tracker.update_with_detections(detections=detections_sv)
            
            frame_boxes = []
            if len(tracked_detections) > 0:
                boxes = tracked_detections.xyxy  # Get bounding boxes
                track_ids = tracked_detections.tracker_id  # Get track IDs
                confidences = tracked_detections.confidence
                
                for idx, (bbox, track_id, confidence) in enumerate(zip(boxes, track_ids, confidences)):
                    x_min, y_min, x_max, y_max = map(int, bbox)
                    
                    # Only extract color if this is a new player or if we need to update
                    if track_id not in self.tracked_players:
                        cropped = frame[y_min:y_max, x_min:x_max]
                        dominant_color = extract_dominant_color(cropped)
                        self.tracked_players[track_id] = {
                            "color": dominant_color,
                            "first_seen": frame_idx,
                            "last_seen": frame_idx
                        }
                    else:
                        self.tracked_players[track_id]["last_seen"] = frame_idx
                        dominant_color = self.tracked_players[track_id]["color"]

                    player_data = {
                        "id": int(track_id),
                        "bbox": [x_min, y_min, x_max, y_max],
                        "confidence": float(confidence),
                        "color": dominant_color
                    }
                    frame_boxes.append(player_data)
                    
            all_tracked_boxes.append(frame_boxes)
            
            # Optional: Clean up players that haven't been seen for a while
            self._cleanup_old_players(frame_idx, max_frames_missing=30)
            
        return all_tracked_boxes

    def _cleanup_old_players(self, current_frame, max_frames_missing=30):
        """Remove players that haven't been seen for a while."""
        players_to_remove = []
        for track_id, player_info in self.tracked_players.items():
            if current_frame - player_info["last_seen"] > max_frames_missing:
                players_to_remove.append(track_id)
        
        for track_id in players_to_remove:
            del self.tracked_players[track_id]

    def get_bounding_boxes(self, frames, conf=0.25, imgsz=1280, classes=[0, 32], read_from_stub=False, stub_path=None):
        """
        Récupère les bounding boxes enrichies avec ID, couleur dominante et score de confiance.
        Utilise le tracking pour maintenir la cohérence des IDs.
        """
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                bounding_boxes = pickle.load(f)
                print(f'✅ Track chargé depuis {stub_path}')
                print(f'🔎 Structure des bounding_boxes (extrait) : {bounding_boxes[0][:2]}')
            return bounding_boxes

        bounding_boxes = self.detect_and_track_frames(frames, conf, imgsz, classes)

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(bounding_boxes, f)
            print(f'✅ Track sauvegardé dans {stub_path}')
            print(f'🔎 Structure finale des bounding_boxes (Frame 0) : {bounding_boxes[0][:2]}')

        return bounding_boxes

    def draw_annotations(self, frames, bounding_boxes):
        """
        🎨 Annoter chaque frame avec :
        - Boîte de délimitation colorée selon équipe ou arbitre
        - ID unique
        - Équipe ou "Referee"
        - Taux de confiance (%)
        """
        annotated_frames = []

        for frame_idx, frame in enumerate(frames):
            for player in bounding_boxes[frame_idx]:
                # 📏 Données joueur
                x_min, y_min, x_max, y_max = player["bbox"]
                player_id = player["id"]
                confidence = player.get("confidence", 0) * 100
                team = player.get("team", "Unknown")
                team_color = player.get("team_color", (0, 255, 0))

                # 🎨 Conversion couleur
                if isinstance(team_color, list) or isinstance(team_color, np.ndarray):
                    team_color = tuple(map(int, team_color))

                # 🏃 **Bounding box couleur d'équipe/arbitre**
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), team_color, 2)

                # 🏷️ **Label : ID - Équipe - Confiance**
                label = f"{'Referee' if team == 'Referee' else f'Player {player_id} - {team}'} - {confidence:.1f}%"
                cv2.putText(frame, label, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, team_color, 2)

            annotated_frames.append(frame)

        return annotated_frames