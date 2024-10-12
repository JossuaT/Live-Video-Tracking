import cv2 as cv

# Charger le classificateur et ouvrir la webcam (0 = caméra par défaut)
model = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')
facecam = cv.VideoCapture(0)

while True:
    # Lire et convertir l'image en niveaux de gris
    ret, frame = facecam.read()
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Détecter les visages et dessiner les rectangles
    faces = model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        cv.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    # Afficher le flux
    cv.imshow('Face Detection', frame)
    
    # Appuyer sur ECHAP pour quitter la boucle
    if cv.waitKey(1) == 27:
        break

# Libérer la capture et fermer les fenêtres
facecam.release()
cv.destroyAllWindows()
