import cv2
from deepface import DeepFace

# Initialisation de la webcam
cap = cv2.VideoCapture(0)  # 0 pour la webcam par défaut

while True:
    ret, frame = cap.read()
    if not ret:
        break

    try:
        # Extraction des visages
        faces = DeepFace.extract_faces(img_path=frame, enforce_detection=False)

        for face in faces:
            x, y, w, h = face["facial_area"]["x"], face["facial_area"]["y"], face["facial_area"]["w"], face["facial_area"]["h"]

            # Dessiner un rectangle autour du visage
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    except Exception as e:
        print(f"Erreur : {e}")

    # Affichage de la vidéo en temps réel
    cv2.imshow("Face Extraction", frame)

    # Quitter avec la touche 'q'
    if cv2.waitKey(27) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
