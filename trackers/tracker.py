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
from deepface import DeepFace
import json

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.tracked_players = {}  # Stocke les informations des objets suivis sur plusieurs frames

        # Liste pour stocker les résultats DeepFace de chaque visage analysé
        self.deepface_results = []

        # Initialiser les annotateurs
        self.box_annotator = BoxAnnotator(color=Color.RED)
        self.label_annotator = LabelAnnotator(text_color=Color.WHITE)

    def detect_and_track_frames(self, frames, conf=0.25, imgsz=1280, classes=[0, 32]):
        """Détecte et suit les objets (Players et Sport Balls) sur toutes les frames avec YOLO et ByteTrack."""
        all_tracked_boxes = []
    
        for frame_idx, frame in enumerate(frames):
            # Si la frame est un chemin, la lire
            if isinstance(frame, str):
                frame = cv2.imread(frame)
            
            # Obtenir les détections pour la frame courante
            detections = self.model.predict(frame, conf=conf, imgsz=imgsz, classes=classes)[0]
            
            # Extraire les classes d'origine, si disponibles
            if hasattr(detections.boxes, "cls"):
                orig_class_ids = detections.boxes.cls.cpu().numpy().astype(int)
            else:
                orig_class_ids = None
            
            # Convertir les détections au format supervision
            detections_sv = sv.Detections.from_ultralytics(detections)
            # Suivre les détections
            tracked_detections = self.tracker.update_with_detections(detections=detections_sv)
            
            frame_boxes = []
            if len(tracked_detections) > 0:
                boxes = tracked_detections.xyxy  # Bounding boxes
                track_ids = tracked_detections.tracker_id  # IDs de suivi
                confidences = tracked_detections.confidence

                # Si les classes d'origine sont disponibles, on les associe (en supposant que l'ordre est préservé)
                if orig_class_ids is not None:
                    detected_classes = orig_class_ids[:len(boxes)]
                else:
                    detected_classes = [0] * len(boxes)  # Par défaut, on considère la classe 0 ("Player")
                
                for idx, (bbox, track_id, confidence, class_id) in enumerate(zip(boxes, track_ids, confidences, detected_classes)):
                    x_min, y_min, x_max, y_max = map(int, bbox)
                    
                    # Déterminer le type d'objet dès le départ
                    object_class = "Sport Ball" if class_id == 32 else "Player"
                    
                    # Gestion de la couleur dominante et tracking
                    if track_id not in self.tracked_players:
                        cropped = frame[y_min:y_max, x_min:x_max]
                        dominant_color = extract_dominant_color(cropped)
                        self.tracked_players[track_id] = {
                            "color": dominant_color,
                            "first_seen": frame_idx,
                            "last_seen": frame_idx,
                            "object_class": object_class
                        }
                    else:
                        self.tracked_players[track_id]["last_seen"] = frame_idx
                        dominant_color = self.tracked_players[track_id]["color"]
                        object_class = self.tracked_players[track_id]["object_class"]
                    
                    # Pour les objets de type "Player", effectuer la reconnaissance faciale
                    if object_class == "Player":
                        face_crop, face_detected = self.recognition(frame, (x_min, y_min, x_max, y_max))
                    else:
                        face_crop, face_detected = None, False
                        
                    # Stocker les informations de l'objet
                    player_data = {
                        "id": int(track_id),
                        "bbox": [x_min, y_min, x_max, y_max],
                        "confidence": float(confidence),
                        "color": dominant_color,
                        "object_class": object_class,
                        "face_detected": face_detected
                    }
                    frame_boxes.append(player_data)
                    
            all_tracked_boxes.append(frame_boxes)
            
            # Nettoyer les objets non vus depuis un moment
            self._cleanup_old_players(frame_idx, max_frames_missing=30)
            
        return all_tracked_boxes

    def _cleanup_old_players(self, current_frame, max_frames_missing=30):
        """Supprime les objets qui n'ont pas été vus depuis un moment."""
        players_to_remove = []
        for track_id, player_info in self.tracked_players.items():
            if current_frame - player_info["last_seen"] > max_frames_missing:
                players_to_remove.append(track_id)
        
        for track_id in players_to_remove:
            del self.tracked_players[track_id]

    def get_bounding_boxes(self, frames, conf=0.25, imgsz=1280, classes=[0, 32], read_from_stub=False, stub_path=None):
        """
        Récupère les bounding boxes enrichies (avec ID, couleur dominante, score de confiance, type et reconnaissance)
        en utilisant le tracking pour maintenir la cohérence des IDs.
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
        - Bounding box colorée selon l'objet (Player ou Sport Ball)
        - Label avec ID, type et taux de confiance (%)
        - Une flèche rouge au-dessus de la tête pour les joueurs reconnus (face_detected=True)
        """
        annotated_frames = []

        for frame_idx, frame in enumerate(frames):
            for player in bounding_boxes[frame_idx]:
                # Récupérer les données
                x_min, y_min, x_max, y_max = player["bbox"]
                player_id = player["id"]
                confidence = player.get("confidence", 0) * 100
                object_class = player.get("object_class", "Player")
                team_color = player.get("color", (0, 255, 0))

                # Dessiner la bounding box
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), team_color, 2)
                # Dessiner le label
                label = f"{object_class} {player_id} - {confidence:.1f}%"
                cv2.putText(frame, label, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, team_color, 2)
                
                # Dessiner la flèche rouge uniquement pour les Players reconnus
                if object_class == "Player" and player.get("face_detected", False):
                    arrow_tip = ((x_min + x_max) // 2, y_min)
                    arrow_tail = ((x_min + x_max) // 2, max(0, y_min - 40))
                    cv2.arrowedLine(frame, arrow_tail, arrow_tip, (0, 0, 255), 5, tipLength=0.5)

            annotated_frames.append(frame)

        return annotated_frames

    def recognition(self, frame, bbox):
        """
        Détecte un visage dans la zone spécifiée par bbox dans l'image frame,
        puis lance la reconnaissance faciale via DeepFace.
        
        Args:
            frame: L'image contenant la zone d'intérêt.
            bbox: Un tuple (x_min, y_min, x_max, y_max) définissant la région à analyser.
            
        Returns:
            tuple: (face_crop, recognized) où recognized est True si DeepFace renvoie une correspondance.
        """
        x_min, y_min, x_max, y_max = bbox
        player_crop = frame[y_min:y_max, x_min:x_max]

        # Détection du visage avec Haar Cascade
        face_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_crop = cv2.cvtColor(player_crop, cv2.COLOR_BGR2GRAY)
        faces = face_model.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=5)

        if len(faces) > 0:
            (fx, fy, fw, fh) = faces[0]
            face_crop = player_crop[fy:fy + fh, fx:fx + fw]
            print("✅ Visage détecté dans la bounding box.")
            print("Démarrage de la reconnaissance pour ce visage...")
            try:
                results = DeepFace.find(
                    img_path=face_crop,  # Attention : DeepFace.find attend souvent un chemin vers l'image.
                    db_path="/Users/nathansornet/Documents/Rugby_git/Live-Video-Tracking/data/players_dataset",
                    model_name="ArcFace",
                    enforce_detection=False
                )
                print("Résultat DeepFace:")
                print(results)
                recognized = True if len(results[0]) > 0 else False

                # Convertir le résultat en dictionnaire pour sauvegarde
                if hasattr(results[0], "to_dict"):
                    deepface_data = results[0].to_dict('records')
                else:
                    deepface_data = str(results[0])
                # Enregistrer le résultat dans la liste interne
                self.deepface_results.append({
                    "bbox": bbox,
                    "deepface_result": deepface_data,
                    "recognized": recognized
                })
            except Exception as e:
                print(f"❌ Erreur DeepFace : {e}")
                recognized = False
            return face_crop, recognized
        else:
            print("⚠️ Aucun visage détecté dans cette bounding box.")
            return player_crop, False

    def save_deepface_results(self, file_path="deepface_results.json"):
        """Sauvegarde les résultats DeepFace de tous les visages analysés dans un fichier JSON."""
        with open(file_path, "w") as f:
            json.dump(self.deepface_results, f, indent=4)
        print(f"Résultats DeepFace sauvegardés dans {file_path}")