# CODE A REVOIR ET CONFIRMER

import cv2
import os
import numpy as np

# Chemin vers le dataset des images d'entraînement
dataset_path = 'dataset/'

# Créer un modèle LBPH pour la reconnaissance faciale
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Charger le classificateur de Haar pour la détection de visages
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Fonction pour lire les images et les étiquettes du dataset
def get_images_and_labels(path):
    image_paths = [os.path.join(path, f) for f in os.listdir(path)]
    face_samples = []
    face_ids = []

    for image_path in image_paths:
        # Lire l'image en niveaux de gris
        gray_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        face_id = int(os.path.split(image_path)[-1].split(".")[1])  # Identifier la personne

        # Détecter le visage dans l'image
        faces = face_cascade.detectMultiScale(gray_image)

        # Ajouter le visage et l'identifiant (face_id) à la liste d'entraînement
        for (x, y, w, h) in faces:
            face_samples.append(gray_image[y:y + h, x:x + w])
            face_ids.append(face_id)

    return face_samples, face_ids

# Récupérer les images et les étiquettes
faces, ids = get_images_and_labels(dataset_path)

# Entraîner le modèle LBPH avec les visages et leurs identifiants
recognizer.train(faces, np.array(ids))

# Enregistrer le modèle entraîné dans un fichier
recognizer.save('face_trainer.yml')

# Ouvrir la webcam pour la reconnaissance faciale
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    # Convertir l'image en niveaux de gris
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Détecter les visages dans l'image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # Reconnaître les visages détectés
    for (x, y, w, h) in faces:
        face_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        # Afficher l'ID et la confiance de la reconnaissance
        if confidence < 100:
            name = f"Person {face_id} ({round(100 - confidence, 2)}%)"
        else:
            name = "Unknown"

        # Dessiner le rectangle autour du visage
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, name, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    # Afficher l'image avec les visages reconnus
    cv2.imshow('Face Recognition', frame)

    # Quitter si la touche 'q' est pressée
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer la capture et fermer les fenêtres
cap.release()
cv2.destroyAllWindows()
