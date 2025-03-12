from ultralytics import YOLO
import supervision as sv
import pickle
import os
import cv2
import sys
sys.path.append('../')
from packages.utils import get_center, compute_distance, extract_dominant_color
import numpy as np
from PIL import Image
from supervision import BoxAnnotator, LabelAnnotator, Color
from deepface import DeepFace
import json

class Tracker:
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.tracked_players = {}          # Informations des objets suivis sur plusieurs frames
        self.deepface_results = []         # Liste pour stocker les résultats DeepFace
        self.recognized_player_ids = {}    # Dictionnaire associant une identité reconnue à un ID unique

        # Initialisation des annotateurs
        self.box_annotator = BoxAnnotator(color=Color.RED)
        self.label_annotator = LabelAnnotator(text_color=Color.WHITE)

    def detect_and_track_frames(self, frames, conf=0.25, imgsz=1280, classes=[0, 32]):
        """Détecte et suit les objets (Players et Sport Ball) sur toutes les frames avec YOLO et ByteTrack."""
        all_tracked_boxes = []
        total_frames = len(frames)
        for frame_idx, frame in enumerate(frames):
            print(f"\n\n🔎 PROCESSING FRAME {frame_idx} / {total_frames}")
            if isinstance(frame, str):
                frame = cv2.imread(frame)
            
            detections = self.model.predict(frame, conf=conf, imgsz=imgsz, classes=classes)[0]
            print(f"Detections : {detections}")
            # C'est ici qu'il faut ajouter la détection des mêlées, touches etc...

            if hasattr(detections.boxes, "cls"):
                orig_class_ids = detections.boxes.cls.cpu().numpy().astype(int)
            else:
                orig_class_ids = None

            detections_sv = sv.Detections.from_ultralytics(detections)
            tracked_detections = self.tracker.update_with_detections(detections=detections_sv)
            
            frame_boxes = []
            if len(tracked_detections) > 0:
                boxes = tracked_detections.xyxy
                track_ids = tracked_detections.tracker_id
                confidences = tracked_detections.confidence

                if orig_class_ids is not None:
                    detected_classes = orig_class_ids[:len(boxes)]
                else:
                    detected_classes = [0] * len(boxes)
                
                for idx, (bbox, track_id, confidence, class_id) in enumerate(zip(boxes, track_ids, confidences, detected_classes)):
                    x_min, y_min, x_max, y_max = map(int, bbox)
                    object_class = "Sport Ball" if class_id == 32 else "Player"
                    
                    # Mise à jour du suivi
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
                    
                    # Pour les joueurs, effectuer la reconnaissance et récupérer la zone du visage
                    if object_class == "Player":
                        face_crop, face_detected, identity_label, face_bbox = self.recognition(frame, (x_min, y_min, x_max, y_max))
                    else:
                        face_crop, face_detected, identity_label, face_bbox = None, False, None, None
                        
                    player_data = {
                        "id": int(track_id),
                        "bbox": [x_min, y_min, x_max, y_max],
                        "confidence": float(confidence),
                        "color": dominant_color,
                        "object_class": object_class,
                        "face_detected": face_detected,
                        "face_identity": identity_label,
                        "face_bbox": face_bbox
                    }
                    frame_boxes.append(player_data)
                    
            all_tracked_boxes.append(frame_boxes)
            self._cleanup_old_players(frame_idx, max_frames_missing=30)
            
        return all_tracked_boxes

    def _cleanup_old_players(self, current_frame, max_frames_missing=30):
        """Supprime les objets qui n'ont pas été vus depuis un certain nombre de frames."""
        players_to_remove = []
        for track_id, player_info in self.tracked_players.items():
            if current_frame - player_info["last_seen"] > max_frames_missing:
                players_to_remove.append(track_id)
        for track_id in players_to_remove:
            del self.tracked_players[track_id]

    def get_bounding_boxes(self, frames, conf=0.25, imgsz=1280, classes=[0, 32], read_from_stub=False, stub_path=None):
        """
        Récupère les bounding boxes enrichies (avec ID, couleur dominante, taux de confiance, type, reconnaissance et face_bbox).
        En cas de reconnaissance, si un joueur a déjà été identifié, on lui attribue le même ID.
        Sauvegarde et restaure également le suivi via un fichier stub (pickle) qui cumule :
          - bounding_boxes
          - recognized_player_ids
          - deepface_results
        """

        # Lecture du fichier si les données existent
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                data = pickle.load(f)
                bounding_boxes = data.get("bounding_boxes", [])
                self.recognized_player_ids = data.get("recognized_player_ids", {})
                self.deepface_results = data.get("deepface_results", [])
                print(f"✅ Stub chargé depuis {stub_path}")
                if bounding_boxes:
                    print(f"🔎 Extrait des bounding_boxes : {bounding_boxes[0][:2]}")
                else:
                    print("🔎 Aucune bounding_box chargée.")
            return bounding_boxes

        bounding_boxes = self.detect_and_track_frames(frames, conf, imgsz, classes)

        # Ecriture du nouveau fichier pickle
        if stub_path is not None :
            with open(stub_path, 'wb') as f:
                data = {
                    "bounding_boxes": bounding_boxes,
                    "recognized_player_ids": self.recognized_player_ids,
                    "deepface_results": self.deepface_results
                }
                pickle.dump(data, f)
            print(f"✅ Stub sauvegardé dans {stub_path}")
            if bounding_boxes:
                print(f"🔎 Structure finale des bounding_boxes (Frame 0) : {bounding_boxes[0][:2]}")

        # Mise à jour des IDs pour les joueurs reconnus
        for frame_idx, frame_boxes in enumerate(bounding_boxes):
            for detection in frame_boxes:
                if detection["object_class"] == "Player":
                    identity_label = detection.get("face_identity", None)
                    if detection.get("face_detected", False) and identity_label is not None:
                        if identity_label in self.recognized_player_ids:
                            detection["id"] = self.recognized_player_ids[identity_label]
                        else:
                            self.recognized_player_ids[identity_label] = detection["id"]
        return bounding_boxes

    def draw_annotations(self, frames, bounding_boxes):
        """
        Annoter chaque frame avec :
         - Bounding box colorée selon l'objet (Player ou Sport Ball)
         - Label avec ID, type et taux de confiance (%)
         - Rectangle bleu autour de la zone du visage détecté (pour tous les visages détectés)
         - Flèche rouge indiquant la reconnaissance (dessinée uniquement si le visage est reconnu, c'est-à-dire si face_identity n'est pas None)
        """
        annotated_frames = []
        for frame_idx, frame in enumerate(frames):
            for detection in bounding_boxes[frame_idx]:
                x_min, y_min, x_max, y_max = detection["bbox"]
                player_id = detection["id"]
                confidence = detection.get("confidence", 0) * 100
                object_class = detection.get("object_class", "Player")
                team_color = detection.get("color", (0, 255, 0))
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), team_color, 2)
                label = f"{object_class} {player_id} - {confidence:.1f}%"
                cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, team_color, 2)
                if object_class == "Player":
                    face_bbox = detection.get("face_bbox")
                    if face_bbox is not None:
                        fx_min, fy_min, fx_max, fy_max = face_bbox
                        cv2.rectangle(frame, (fx_min, fy_min), (fx_max, fy_max), (255, 0, 0), 2)
                        cv2.putText(frame, "Face", (fx_min, fy_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                    # Dessiner la flèche rouge uniquement si le visage est reconnu
                    if detection.get("face_detected", False) and detection.get("face_identity") is not None:
                        arrow_tip = ((x_min + x_max) // 2, y_min)
                        arrow_tail = ((x_min + x_max) // 2, max(0, y_min - 40))
                        cv2.arrowedLine(frame, arrow_tail, arrow_tip, (0, 0, 255), 5, tipLength=0.5)
            annotated_frames.append(frame)
        return annotated_frames

    def recognition(self, frame, bbox):
        """
        Détecte un visage dans la zone spécifiée par bbox et lance la reconnaissance via DeepFace.
        Retourne : (face_crop, reconnu, identité, face_bbox)
        
        La fonction extrait le nom du joueur à partir du chemin de l'image retourné par DeepFace.
        Par exemple, si le chemin est "data/players_dataset/AntoineDupont/...", alors le nom retourné sera "AntoineDupont".
        Elle renvoie également la boîte englobante du visage (coordonnées absolues dans la frame).
        """
        x_min, y_min, x_max, y_max = bbox
        player_crop = frame[y_min:y_max, x_min:x_max]

        #face_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        #gray_crop = cv2.cvtColor(player_crop, cv2.COLOR_BGR2GRAY)
        #faces = face_model.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=5)
        # =================================================================================
        detected_faces = DeepFace.extract_faces(
            img_path = player_crop,
            detector_backend = 'opencv',
            enforce_detection = False
        )
        faces = [f for f in detected_faces if f["confidence"] > 0.7]
        # ???
        faces.sort(key=lambda f: f["confidence"], reverse=True)
        identity_label = None
        face_bbox = None

        if len(faces) > 0:
            face = faces[0]
            print("🧑 Visage détecté dans la bounding box.")
            # Pour détection haarcascades
            #(fx, fy, fw, fh) = faces[0]

            # Pour détection opencv via Deepface
            fx, fy, fw, fh = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
            face_crop = player_crop[fy:fy+fh, fx:fx+fw]
            face_bbox = (x_min + fx, y_min + fy, x_min + fx + fw, y_min + fy + fh)
            print("     Démarrage de la reconnaissance pour ce visage...")
            try:
                results = DeepFace.find(
                    img_path=face_crop,
                    db_path="./data/players_dataset",
                    model_name="Facenet512",
                    enforce_detection=False,
                    silent=True
                )
                recognized = True if len(results[0]) > 0 else False
                if recognized:
                    best_similarity_pos = min(enumerate(results[0]['distance']), key=lambda x: x[1])[0]
                    identity_path = results[0]['identity'][best_similarity_pos]
                    identity_name = os.path.basename(os.path.dirname(identity_path))
                    identity_label = identity_name
                    print("     ✅ Identité reconnue :", identity_label)
                else:
                    recognized = False
                    print("     👻 Aucune correspondance.")
            except Exception as e:
                print(f"❌ Erreur DeepFace : {e}")
                recognized = False

            self.deepface_results.append({
                "bbox": bbox,
                "face_bbox": face_bbox,
                "identity_label": identity_label,
                "recognized": recognized
            })

            return face_crop, recognized, identity_label, face_bbox
        else:
            print("⚠️  Aucun visage détecté dans cette bounding box.")
            return player_crop, False, None, None

    def save_deepface_results(self, file_path="deepface_results.json"):
        """
        Cette méthode est optionnelle si vous cumulez dans le stub.
        Ici, nous la laissons pour un éventuel usage indépendant.
        """
        with open(file_path, "w") as f:
            json.dump(self.deepface_results, f, indent=4)
        print(f"Résultats DeepFace sauvegardés dans {file_path}")