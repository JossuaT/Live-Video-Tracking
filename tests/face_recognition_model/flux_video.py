import cv2 as cv2

# Ouverture et configuration de la caméra 0 (cam par défaut)
facecam = cv2.VideoCapture(0)
frame_width = int(facecam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(frame_width, frame_height)

# Enregistrement : CODEC et définition de l'objet
#fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#flux = cv2.VideoWriter('output.mp4', fourcc, 20.0, (frame_width, frame_height))

while True:
    # Lecture et affichage de l'image
    ret, frame = facecam.read()
    cv2.imshow('Camera', frame)

    # Enregistrement : écriture
    #flux.write(frame)

    # On quitte la boucle lorsque la touche ECHAP est appuyée
    if cv2.waitKey(1) == 27:
        break

# Arrêt
facecam.release()
cv2.destroyAllWindows()

# Enregistrement : arrêt
#flux.release()