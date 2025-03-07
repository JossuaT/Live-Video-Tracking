from PIL import Image
import requests
from io import BytesIO
import os

def is_empty_image(image_path):
    size_bytes = os.path.getsize(image_path)
    if size_bytes < 10000:
        return True
    return False

def remove_picture(image_path):
    try:
        os.remove(image_path)
        print(f"🗑️ Image supprimée : {image_path}")
    except OSError as e:
        print(f"❌ Erreur lors de la suppression de l'image : {e}")
    

# Chemin du dossier contenant les images
base_folder = "data/players_pictures"

# Vérifier si le dossier existe
if not os.path.exists(base_folder):
    print("Le dossier n'existe pas !")
else:
    # Boucler sur chaque dossier d'équipe
    for equipe in os.listdir(base_folder):
        equipe_path = os.path.join(base_folder, equipe)

        # Vérifier si c'est bien un dossier
        if os.path.isdir(equipe_path):
            print(f"📂 Équipe : {equipe}")


            # Boucler sur chaque dossier d'équipe
            for player in os.listdir(equipe_path):
                player_path = os.path.join(equipe_path, player)

                # Boucler sur chaque fichier image dans le dossier de l'équipe
                for fichier in os.listdir(player_path):
                    if fichier.endswith(".jpeg"):  # Filtrer uniquement les images .jpeg
                        image_path = os.path.join(player_path, fichier)
                        if is_empty_image(image_path):
                            remove_picture(image_path)
