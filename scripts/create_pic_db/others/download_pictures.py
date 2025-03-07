
"""
Télécharger les photos des joueurs depuis le fichier json issu du script collect_players_pic.py

/!\ Il faut lancer le script rm_empty_pic.py après celui-ci afin de supprimer les photos vides
"""

import os
import json
import requests
from PIL import Image
from io import BytesIO

# Charger le fichier JSON
json_path = "data/players_pictures.json"
with open(json_path, "r", encoding="utf-8") as f:
    players_data = json.load(f)

# Dossier racine pour stocker les images
root_dir = "data/players_pictures"
os.makedirs(root_dir, exist_ok=True)

# User-Agent pour éviter le blocage des requêtes
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Parcourir chaque équipe
# Parcourir chaque équipe
for equipe, joueurs in players_data.items():
    equipe_dir = os.path.join(root_dir, equipe)  # Dossier de l'équipe
    os.makedirs(equipe_dir, exist_ok=True)  # Créer s'il n'existe pas

    # Parcourir chaque joueur et télécharger l'image
    for joueur, image_url in joueurs.items():
        try:
            # Télécharger l'image
            response = requests.get(image_url, headers=headers, timeout=10)
            response.raise_for_status()  # Vérifier si la requête a réussi

            # Charger l'image
            image = Image.open(BytesIO(response.content))
            image = image.convert("RGB")  # Convertir en RGB pour éviter les erreurs

            # Nettoyer le nom du joueur (éviter caractères spéciaux)
            joueur_clean = "".join(c if c.isalnum() or c in " _-" else "_" for c in joueur)

            # Créer le dossier du joueur
            joueur_dir = os.path.join(equipe_dir, joueur_clean)
            os.makedirs(joueur_dir, exist_ok=True)

            # Déterminer le numéro de la prochaine image (1.jpeg, 2.jpeg, etc.)
            existing_images = [f for f in os.listdir(joueur_dir) if f.endswith(".jpeg")]
            next_index = len(existing_images) + 1
            image_filename = f"{next_index}.jpeg"
            image_path = os.path.join(joueur_dir, image_filename)

            # Sauvegarder l'image
            image.save(image_path, "JPEG", quality=95)

            print(f"✅ Image sauvegardée : {image_path}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur de téléchargement pour {joueur} ({image_url}) : {e}")
        except Exception as e:
            print(f"⚠️ Erreur lors du traitement de l'image pour {joueur} : {e}")

print("🎉 Téléchargement terminé !")
