import cv2
import os
import numpy as np
from PIL import Image

# Chemin vers le dataset d'entraînement
relative_path_to_dataset = 'players_dataset\\'
dataset_path = os.path.join(os.path.dirname(__file__), relative_path_to_dataset)

# Initialiser le modèle LBPH pour la reconnaissance faciale
recognizer_model = cv2.face.LBPHFaceRecognizer_create()

# Charger le classificateur Haar Cascade pour détecter les visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Fonction pour obtenir les visages et les labels à partir des images dans le dataset
def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.')]
    face_samples = []
    face_labels = []
    
    for image_path in image_paths:
        # Convertir l'image en niveaux de gris / array
        gray_img = Image.open(image_path).convert('L')
        img = np.array(gray_img, 'uint8')

        # Extraire le nom du joueur
        face_name = int(os.path.split(image_path)[-1].split(".")[0])

        # Détecter les visages dans l'image
        faces = face_cascade.detectMultiScale(img)

        # Ajouter chaque visage détecté et son label à la liste d'entraînement
        for (x, y, w, h) in faces:
            face_samples.append(img[y:y+h, x:x+w])
            face_labels.append(face_name)

    return face_samples, face_labels

# Charger les images et les étiquettes (labels)
faces, labels = get_images_and_labels(dataset_path)

# Entraîner le modèle LBPH
recognizer_model.train(faces, np.array(labels))

# Enregistrer le modèle entraîné
recognizer_model.save('face_recognition_model.yml')

print(f"Modèle entraîné avec {len(set(labels))} personnes et {len(faces)} visages.")
