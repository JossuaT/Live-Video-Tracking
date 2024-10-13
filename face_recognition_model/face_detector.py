import cv2 as cv

# Charger le classificateur et ouvrir la webcam (0 = caméra par défaut)
model = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
facecam = cv.VideoCapture(0)

while True:
    # Lire
    ret, frame = facecam.read()
    
    # Niveaux de gris, détection et rectangles
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (0, 255, 0)
        cv.rectangle(frame, start_point, end_point, color, thickness=2)
    
    # Afficher le flux
    cv.imshow('Face Detection', frame)
    
    # Appuyer sur ECHAP pour quitter la boucle
    if cv.waitKey(1) == 27:
        break

# Arrêt capture et ferme les fenêtres
facecam.release()
cv.destroyAllWindows()
