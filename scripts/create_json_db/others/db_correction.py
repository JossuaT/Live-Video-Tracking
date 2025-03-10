"""
Ouvre et corrige les noms des joueurs dans la base de données JSON top14_players_database.json".
"""

import json
import ftfy  # Pour corriger les erreurs d'encodage

# Charger le fichier JSON
json_path = "data/top14_players_database.json"
with open(json_path, "r", encoding="utf-8") as f:
    players_data = json.load(f)

# Correction des noms mal encodés
for player_id, player_info in players_data.items():
    if "name" in player_info:
        original_name = player_info["name"]
        corrected_name = ftfy.fix_text(original_name)  # Correction automatique
        if corrected_name != original_name:
            print(f"✅ Correction : '{original_name}' → '{corrected_name}'")
        player_info["name"] = corrected_name  # Mise à jour du JSON

# Sauvegarder le JSON corrigé
corrected_json_path = "data/top14_players_database_corrected.json"
with open(corrected_json_path, "w", encoding="utf-8") as f:
    json.dump(players_data, f, indent=4, ensure_ascii=False)

print(f"🎉 Fichier corrigé enregistré sous : {corrected_json_path}")
