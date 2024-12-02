import cv2 as cv2

# Charger le classificateur et ouvrir la webcam (0 = caméra par défaut)
face_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eyes_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
lowerbody_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_lowerbody.xml')
upperbody_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
fullbody_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')

facecam = cv2.VideoCapture(0)

while True:
    # Lire
    _, frame = facecam.read()                   # can collect ret
    
    # Niveaux de gris, détection et rectangles
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
    eyes = eyes_model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=6)
    lowerbodies = lowerbody_model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=2)
    upperbodies = upperbody_model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=3)
    fullbodies = fullbody_model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=2)

    for (x, y, w, h) in faces:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (0, 0, 0)
        cv2.rectangle(frame, start_point, end_point, color, thickness=2)
        cv2.putText(frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)

    for (x, y, w, h) in eyes:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (255, 255, 255)
        cv2.rectangle(frame, start_point, end_point, color, thickness=2)
        cv2.putText(frame, 'Eye', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    for (x, y, w, h) in lowerbodies:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (0, 0, 255)
        cv2.rectangle(frame, start_point, end_point, color, thickness=2)
        cv2.putText(frame, 'low_body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)

    for (x, y, w, h) in upperbodies:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (0, 0, 255)
        cv2.rectangle(frame, start_point, end_point, color, thickness=2)
        cv2.putText(frame, 'up_body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)

    for (x, y, w, h) in fullbodies:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (255, 0, 0)
        cv2.rectangle(frame, start_point, end_point, color, thickness=2)
        cv2.putText(frame, 'full_body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 1)
    
    # Afficher le flux
    cv2.imshow('Face Detection', frame)
    
    # Appuyer sur ECHAP pour quitter la boucle
    if cv2.waitKey(1) == 27:
        break

# Arrêt capture et ferme les fenêtres
facecam.release()
cv2.destroyAllWindows()
