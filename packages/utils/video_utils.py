import cv2

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

def save_video(output_video_frames, output_video_path, video_path):
    if not output_video_frames:
        print("No frames to save.")
        return

    # Utilisation de la première image pour obtenir la taille et les paramètres de la vidéo
    frame_height, frame_width = output_video_frames[0].shape[:2]
    fps = 24  # Par défaut, on utilise 24 FPS

    # Vérification de la fréquence d'images de la vidéo source
    cap = cv2.VideoCapture(video_path)
    if cap.isOpened():
        fps = cap.get(cv2.CAP_PROP_FPS)
        cap.release()
    
    # Création du Writer avec le codec MJPG
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    
    # Sauvegarde des images
    for frame in output_video_frames:
        out.write(frame)
    out.release()
    # print("Video saved successfully.")

