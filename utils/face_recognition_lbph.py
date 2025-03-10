import cv2
import numpy as np
import os

# Chemin vers le modèle LBPH entraîné (assure-toi que ce fichier existe)
MODEL_PATH = "models/face_recognition_model.yml"
# if not os.path.exists(MODEL_PATH):
#     raise Exception(f"Le modèle LBPH n'a pas été trouvé à : {MODEL_PATH}")

# Charger le modèle LBPH
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(MODEL_PATH)

# Correspondance entre les labels numériques et les noms des joueurs.
# Par exemple, si l'image d'Antoine Dupont est nommée "1.jpg", alors label 1 = "Antoine Dupont"
LABELS_TO_NAMES = {
    1: "Antoine Dupont",
    # Ajoute d'autres correspondances si nécessaire
}

def predict_identity(face_crop):
    """
    Prédit l'identité à partir d'un crop de visage.
    
    Args:
        face_crop: Image du visage (couleur ou niveaux de gris).
    
    Returns:
        Un tuple (name, confidence) où 'name' est le nom prédit (ou "Unknown")
        et 'confidence' est la distance (une valeur plus faible indique une meilleure correspondance).
    """
    # Conversion en niveaux de gris si nécessaire
    if len(face_crop.shape) == 3:
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    else:
        gray = face_crop

    label, confidence = recognizer.predict(gray)
    # Pour LBPH, un score faible signifie une bonne correspondance.
    THRESHOLD = 60  # Ajuste ce seuil en fonction de tes tests
    if confidence < THRESHOLD:
        name = LABELS_TO_NAMES.get(label, "Unknown")
    else:
        name = "Unknown"
    return name, confidence