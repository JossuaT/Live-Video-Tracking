from packages.utils import get_video_id

video_path = "./video/video_4-crop.mp4"


video_id = get_video_id(video_path, JSON_file="./data/JSON/video_hashes.json")
print(f"🎬 ID de la vidéo : {video_id}")

stub_path = './stubs/' + video_id + '_tracks_stubs.pkl'
print(f"Nom du fichier stub : {stub_path}")