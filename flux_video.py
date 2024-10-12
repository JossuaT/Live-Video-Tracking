import cv2 as cv

# Ouverture et configuration de la caméra 0 (cam par défaut)
facecam = cv.VideoCapture(0)
frame_width = int(facecam.get(cv.CAP_PROP_FRAME_WIDTH))
frame_height = int(facecam.get(cv.CAP_PROP_FRAME_HEIGHT))
print(frame_width, frame_height)

# CODEC et définition de l'objet
fourcc = cv.VideoWriter_fourcc(*'mp4v')
flux = cv.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

while True:
    # Lecture et affichage de l'image
    ret, frame = facecam.read()
    flux.write(frame)
    cv.imshow('Camera', frame)

    # On quitte la boucle lorsque la touche ECHAP est appuyée
    if cv.waitKey(1) == 27:
        break

# Arrêt
facecam.release()
flux.release()
cv.destroyAllWindows()