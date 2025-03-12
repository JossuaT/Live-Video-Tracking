import os
import shutil
from deepface import DeepFace

def filter_players_dataset (remaining_teams, full_db_path="./data/players_datasets", filtered_db_path = "./data/filtered_players_datasets"):
    # Supprimer l'ancien dossier temporaire s'il existe
    if os.path.exists(filtered_db_path):
        shutil.rmtree(filtered_db_path)

    # Créer le dossier temporaire
    os.makedirs(filtered_db_path)

    # Créer des liens symboliques vers les dossiers des équipes sélectionnées
    for team in remaining_teams:
        equipe_original = os.path.join(full_db_path, team)
        equipe_symlink = os.path.join(filtered_db_path, team)
        
        if os.path.exists(equipe_original):
            os.symlink(equipe_original, equipe_symlink)  # Créer un lien symbolique

filtered_db_path = filter_players_dataset(['toulouse', 'paris'])

# Exécuter DeepFace.find() sur la base filtrée
results = DeepFace.find(img_path="image5.png", db_path=filtered_db_path, model_name="VGG-Face")

# Afficher les résultats
print(results)
