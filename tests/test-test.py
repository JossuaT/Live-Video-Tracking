import os, cv2
# Ne pas affiher les warnings tensorflow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from deepface import DeepFace


def read_video(video_path: str) -> list:
    """
    Read a video, print duration and return a list of frames and duration
    """
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    video_duration = frame_count / fps if fps != 0 else 0
    cap.release()
    print(f"Durée de la vidéo : {video_duration:.2f} secondes")
    return frames, video_duration

def recognition(frame, bbox):
    """
    Détecte un visage dans la zone spécifiée par bbox et lance la reconnaissance via DeepFace.
    Retourne : (face_crop, reconnu, identité, face_bbox)
    
    La fonction extrait le nom du joueur à partir du chemin de l'image retourné par DeepFace.
    Par exemple, si le chemin est "data/players_dataset/AntoineDupont/...", alors le nom retourné sera "AntoineDupont".
    Elle renvoie également la boîte englobante du visage (coordonnées absolues dans la frame).
    """
    x_min, y_min, x_max, y_max = bbox
    player_crop = frame[y_min:y_max, x_min:x_max]

    #face_model = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #gray_crop = cv2.cvtColor(player_crop, cv2.COLOR_BGR2GRAY)
    #faces = face_model.detectMultiScale(gray_crop, scaleFactor=1.1, minNeighbors=5)
    # =================================================================================
    detected_faces = DeepFace.extract_faces(
        img_path = player_crop,
        detector_backend = 'opencv',
        enforce_detection = False,
    )
    #print(f"Detected faces: {len(detected_faces)} \n {detected_faces}")
    faces = [f for f in detected_faces if f["confidence"] > 0.7]
    #print(f"Faces: {len(faces)} \n {faces}")

    # ???
    faces.sort(key=lambda f: f["confidence"], reverse=True)
    identity_label = None
    face_bbox = None

    if len(faces) > 0:
        for face in faces :
            print("🧑 Visage détecté dans la bounding box.")
            # Pour détection haarcascades
            #(fx, fy, fw, fh) = faces[0]

            # Pour détection opencv via Deepface
            fx, fy, fw, fh = face['facial_area']['x'], face['facial_area']['y'], face['facial_area']['w'], face['facial_area']['h']
            face_crop = player_crop[fy:fy+fh, fx:fx+fw]
            face_bbox = (x_min + fx, y_min + fy, x_min + fx + fw, y_min + fy + fh)
            print("     Démarrage de la reconnaissance pour ce visage...")
            try:
                results = DeepFace.find(
                    img_path=face_crop,
                    db_path="./data/players_dataset",
                    model_name="Facenet512",
                    enforce_detection=False,
                    silent=True
                )
                recognized = True if len(results[0]) > 0 else False
                if recognized:
                    best_similarity_pos = min(enumerate(results[0]['distance']), key=lambda x: x[1])[0]
                    identity_path = results[0]['identity'][best_similarity_pos]
                    identity_name = os.path.basename(os.path.dirname(identity_path))
                    identity_label = identity_name
                    print("     ✅ Identité reconnue :", identity_label)
                else:
                    recognized = False
                    print("     👻 Aucune correspondance.")
            except Exception as e:
                print(f"❌ Erreur DeepFace : {e}")
                recognized = False

        return face_crop, recognized, identity_label, face_bbox
    else:
        print("⚠️  Aucun visage détecté dans cette bounding box.")
        return player_crop, False, None, None

path = './data/image7.png'

frame = cv2.imread(path, cv2.IMREAD_COLOR)

print(recognition(frame, [0, 0, 1361, 599]))