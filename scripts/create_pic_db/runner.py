"""
Ce script exécute tous les scripts de traitement des images dans l'ordre.
Il ajoute des images dans le dossier data/players_pictures.

/!\ Peux créer des doublons si le dossier data/players_pictures n'est pas vide !
"""

import sys
import subprocess

# Liste des scripts à exécuter DANS L'ORDRE
scripts = [
    # "scripts/create_pic_db/web_scraping/collect_players_pic.py",
    "scripts/create_pic_db/others/download_pictures.py",
    "scripts/create_pic_db/others/rm_empty_pic.py",
    "scripts/create_pic_db/others/dl_pictures2.py"
]

all_success = True

for script in scripts:
    print(f"🚀 Exécution de : {script}...")
    python_executable = sys.executable  # Récupère l'interpréteur actuel (celui du venv)
    result = subprocess.run([python_executable, script], capture_output=True, text=True, encoding="utf-8")

    # Affichage de la sortie du script exécuté
    print(result.stdout)
    
    # Vérification des erreurs
    if result.returncode != 0:
        print(f"❌ Erreur lors de l'exécution de {script} !")
        print(result.stderr)
        all_success = False
        break

if all_success:
    print("✅  Tous les scripts ont été exécutés avec succès !")
else:
    print("⚠️  Le processus a été interrompu à cause d'une erreur.")
