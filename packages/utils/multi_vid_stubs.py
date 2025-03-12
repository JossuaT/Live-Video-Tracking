import hashlib
import json
import os

def get_video_hash(video_path):
    """Calcule le hash SHA256 d'un fichier vidéo."""
    hasher = hashlib.sha256()
    with open(video_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def load_hash_database(JSON_file="./data/JSON/video_hashes.json"):
    """Charge la base de données des hash depuis un fichier JSON."""
    if os.path.exists(JSON_file):
        with open(JSON_file, "r") as f:
            return json.load(f)
    return {}  # Retourne un dictionnaire vide si le fichier n'existe pas

def save_hash_database(hash_dict, JSON_file="./data/JSON/video_hashes.json"):
    """Enregistre le dictionnaire des hash dans un fichier JSON."""
    with open(JSON_file, "w") as f:
        json.dump(hash_dict, f, indent=4)

def generate_new_id(hash_db):
    """Génère un nouvel ID sous la forme '0001', '0002'..."""
    existing_ids = [int(i) for i in hash_db.keys()] if hash_db else [0]
    new_id = max(existing_ids) + 1
    return f"{new_id:04d}"  # Formate en 4 chiffres

def get_video_id(video_path, JSON_file="./data/JSON/video_hashes.json"):
    """Retourne l'ID de la vidéo en fonction de son hash."""
    video_hash = get_video_hash(video_path)
    hash_db = load_hash_database(JSON_file)

    # Vérifier si la vidéo est déjà enregistrée
    for vid_id, data in hash_db.items():
        if data['hash'] == video_hash:
            print(f"✅ Vidéo déjà enregistrée avec ID : {vid_id}")
            return vid_id

    # Générer un nouvel ID et l'ajouter à la base
    new_id = generate_new_id(hash_db)
    hash_db[new_id] = {"file_name": os.path.basename(video_path), "hash": video_hash}
    save_hash_database(hash_db, JSON_file)

    print(f"🆕 Nouvelle vidéo ajoutée avec ID : {new_id}")
    return new_id