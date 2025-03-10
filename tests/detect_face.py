import cv2
from deepface import DeepFace

# Charger l'image
image_path = "data/image5.png"
image = cv2.imread(image_path)

backends = [
  'opencv', 
  'ssd', 
  'dlib', 
  'mtcnn', 
  'fastmtcnn',
  'retinaface', 
  'mediapipe',
  'yolov8',
  'yolov11s',
  'yolov11n',
  'yolov11m',
  'yunet',
  'centerface',
]

# Utiliser DeepFace pour détecter les visages
detected_faces = DeepFace.extract_faces(
    img_path=image_path,
    detector_backend=backends[5]
)

# Dessiner les bounding boxes
for face in detected_faces:
    x = face['facial_area']['x']
    y = face['facial_area']['y']
    w = face['facial_area']['w']
    h = face['facial_area']['h']
    
    # Dessiner un rectangle autour du visage
    cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

# Afficher l'image avec les bounding boxes
cv2.imshow("Face Detection", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
