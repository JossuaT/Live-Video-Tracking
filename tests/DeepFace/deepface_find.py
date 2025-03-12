#!/usr/bin/env python
from deepface import DeepFace

def main():
    # Recherche de correspondances pour l'image spécifiée dans le dataset
    results = DeepFace.find(
        img_path='./data/image5.png',
        db_path='./data/players_dataset',
        model_name='ArcFace'
    )
    
    # Affiche les résultats complets
    print("Résultats complets :", results)
    
    # Affiche les identités trouvées (si présentes)
    if results and isinstance(results, list) and 'identity' in results[0]:
        print("Identités trouvées :")
        for identity in results[0]['identity']:
            print(identity)
        # Affiche de nouveau la liste des identités
        print("Liste des identités :", results[0]['identity'])
    else:
        print("Aucune identité trouvée.")

if __name__ == '__main__':
    main()