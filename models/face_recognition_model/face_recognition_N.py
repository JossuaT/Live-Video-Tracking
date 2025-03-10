import cv2
import os
import numpy as np
from PIL import Image

# Chemin vers le dataset d'entraînement (adapté à votre structure de projet)
relative_path_to_dataset = os.path.join('..', '..', 'data', 'players_dataset')
dataset_path = os.path.join(os.path.dirname(__file__), relative_path_to_dataset)

if not os.path.exists(dataset_path):
    raise Exception(f"Le dossier du dataset n'existe pas : {dataset_path}")

# Initialiser le modèle LBPH pour la reconnaissance faciale
recognizer_model = cv2.face.LBPHFaceRecognizer_create()

# Charger le classificateur Haar Cascade pour détecter les visages
cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
if not os.path.exists(cascade_path):
    raise Exception(f"Le fichier cascade n'existe pas : {cascade_path}")
face_cascade = cv2.CascadeClassifier(cascade_path)

# Fonction pour obtenir les visages et les labels à partir des images dans le dataset
def get_images_and_labels(path):
    # Lister tous les fichiers (en ignorant ceux commençant par un point)
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.')]
    if not image_paths:
        raise Exception("Aucune image trouvée dans le dataset.")
    face_samples = []
    face_labels = []
    print("Images trouvées :", image_paths)
    
    for image_path in image_paths:
        try:
            # Ouvrir l'image et la convertir en niveaux de gris
            gray_img = Image.open(image_path).convert('L')
        except Exception as e:
            print(f"Erreur lors de l'ouverture de l'image {image_path}: {e}")
            continue
        
        img = np.array(gray_img, 'uint8')

        # Extraire le label (on suppose que le nom de l'image commence par l'identifiant, ex: "1.jpg")
        try:
            face_label = int(os.path.split(image_path)[-1].split(".")[0])
        except ValueError as e:
            print(f"Erreur pour extraire le label de {image_path}: {e}")
            continue

        # Détecter les visages dans l'image
        faces = face_cascade.detectMultiScale(img)
        if len(faces) == 0:
            print(f"Aucun visage détecté dans {image_path}")
            continue

        # Pour chaque visage détecté, ajouter la région correspondante et le label
        for (x, y, w, h) in faces:
            face_samples.append(img[y:y+h, x:x+w])
            face_labels.append(face_label)

    return face_samples, face_labels

# Charger les images et les étiquettes (labels)
faces, labels = get_images_and_labels(dataset_path)

if len(faces) == 0:
    raise Exception("Aucun visage n'a été détecté dans l'ensemble du dataset.")

# Entraîner le modèle LBPH avec les visages détectés et leurs labels
recognizer_model.train(faces, np.array(labels))

# Enregistrer le modèle entraîné dans le même dossier que ce script
model_save_path = os.path.join(os.path.dirname(__file__), 'face_recognition_model.yml')
recognizer_model.save(model_save_path)

print(f"Modèle entraîné avec {len(set(labels))} personnes et {len(faces)} visages.")