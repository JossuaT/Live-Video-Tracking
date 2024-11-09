import cv2 as cv

# Capture de l'image AVEC traitement et SANS enregistrement
facecam = cv.VideoCapture(0)
model = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_default.xml')

while True:
    ret, frame = facecam.read()
    gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    faces = model.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        start_point, end_point = (x, y), (x+w, y+h)
        color = (0, 255, 0)
        cv.rectangle(frame, start_point, end_point, color, thickness=2)
    cv.imshow('Camera', frame)

    if cv.waitKey(1) == 27:
        break

facecam.release()
cv.destroyAllWindows()