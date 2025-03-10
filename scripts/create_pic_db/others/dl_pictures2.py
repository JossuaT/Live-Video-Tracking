"""
Télécharge les photos des joueurs dont les liens sont contenus dans le fichier json top14_players_database.json
"""

import os
import json
import requests
from PIL import Image
from io import BytesIO

# Charger le fichier JSON
json_path = "data/top14_players_database_corrected.json"
with open(json_path, "r", encoding="utf-8") as f:
    players_data = json.load(f)

# Dossier racine où sont stockées les images
root_dir = "data/players_pictures"

# Liste des joueurs dont le dossier n'existe pas
joueurs_non_trouves = []

# User-Agent pour éviter le blocage des requêtes
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def normalize_name(name):
    """
    Normalise un nom pour faciliter la comparaison :
    - Suppression des accents
    - Mise en minuscules
    - Suppression des caractères spéciaux
    """
    return "".join(c if c.isalnum() or c in " _-" else "" for c in name.lower())  # Garde seulement lettres, chiffres, espaces, tirets

def find_player_directory(player_name):
    """
    Recherche le dossier du joueur dans toutes les équipes, en tenant compte des différences d'écriture.
    Retourne le chemin du dossier s'il existe, sinon None.
    """
    normalized_player_name = normalize_name(player_name)

    for team_folder in os.listdir(root_dir):  # Parcours des dossiers d'équipes
        team_path = os.path.join(root_dir, team_folder)
        if os.path.isdir(team_path):  # Vérifie que c'est un dossier
            for player_folder in os.listdir(team_path):  # Parcours des dossiers de joueurs
                if os.path.isdir(os.path.join(team_path, player_folder)):
                    if normalize_name(player_folder) == normalized_player_name:
                        return os.path.join(team_path, player_folder)

    return None  # Si aucun dossier correspondant n'a été trouvé

def get_next_image_filename(player_dir):
    """Trouve le premier numéro disponible pour enregistrer une nouvelle image."""
    i = 1
    while os.path.exists(os.path.join(player_dir, f"{i}.jpeg")):
        i += 1
    return os.path.join(player_dir, f"{i}.jpeg")

# Parcourir chaque joueur dans le fichier JSON
for player_id, player_info in players_data.items():
    name = player_info.get("name", "Unknown_Player")
    img_url = player_info.get("img")

    if not img_url:
        print(f"⚠️ Pas d'image pour {name} ({player_id})")
        continue  # Passer au joueur suivant

    # Chercher le dossier du joueur avec la fonction améliorée
    player_dir = find_player_directory(name)

    # Si aucun dossier correspondant n'est trouvé, enregistrer le joueur dans la liste
    if player_dir is None:
        joueurs_non_trouves.append(name)
        print(f"🚨 Dossier introuvable pour {name}, ajouté à la liste des joueurs non trouvés.")
        continue

    try:
        # Télécharger l'image
        response = requests.get(img_url, headers=headers, timeout=10)
        response.raise_for_status()  # Vérifier si la requête a réussi

        # Charger et convertir l'image
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")  # Convertir en RGB pour éviter les erreurs

        # Trouver le premier numéro de fichier disponible
        image_path = get_next_image_filename(player_dir)

        # Sauvegarde de l'image
        image.save(image_path, "JPEG", quality=95)

        print(f"✅ Image sauvegardée : {image_path}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur de téléchargement pour {name} ({img_url}) : {e}")
    except Exception as e:
        print(f"⚠️ Erreur lors du traitement de l'image pour {name} : {e}")

# Enregistrer la liste des joueurs non trouvés dans un fichier texte
if joueurs_non_trouves:
    missing_players_file = os.path.join(root_dir, "joueurs_non_trouves.txt")
    with open(missing_players_file, "w", encoding="utf-8") as f:
        for joueur in joueurs_non_trouves:
            f.write(joueur + "\n")
    print(f"📄 Liste des joueurs non trouvés enregistrée dans {missing_players_file}")

print("🎉 Téléchargement terminé !")
