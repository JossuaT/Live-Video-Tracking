# IQVision

Ce projet permet de réaliser le suivi et la reconnaissance de joueurs dans des vidéos à l'aide de YOLO pour la détection, DeepFace pour la reconnaissance et d'autres outils pour l'annotation et l'analyse (suivi, attribution d'équipe, génération de rapport via ChatGPT, etc.).  
Les résultats de suivi (bounding boxes, DeepFace, etc.) sont sauvegardés dans un fichier stub (pickle) afin de permettre leur réutilisation lors de différentes exécutions.

---

## 🚀 Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_DEPOT>
```

### 2. Utiliser Poetry pour gérer l’environnement

Si vous n’avez pas encore Poetry installé, consultez les instructions d’installation de Poetry.
Installez ensuite les dépendances avec :

```bash
poetry install
```

Pour lancer le projet, utilisez :

```bash
poetry run python main.py
```

### 3. Télécharger les poids du modèle

⚠️ Les poids YOLO ne sont pas inclus dans ce dépôt  
Le dossier `models_weight` existe, mais vous devez télécharger les poids YOLO :

```bash
wget -O models_weight/yolo11x.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt
```

Si `wget` n’est pas disponible :

```bash
curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt -o models_weight/yolo11x.pt
```

Vérifiez que le chemin du modèle dans `main.py` est correct :

```python
tracker = Tracker('models_weight/yolo11x.pt')
```

### 4. Ajouter vos vidéos

Le dossier `video` existe déjà, mais il ne contient pas de vidéos.  
Ajoutez vos vidéos au format `.mp4` dans le dossier `video/`.

Dans `main.py`, vérifiez que le chemin de la vidéo est correct :

```python
video_path = "video/video_4.mp4"
```

---

## ⚡ Exécuter le projet

1. Vérifiez dans `main.py` que les chemins suivants sont corrects :
   - Vidéo : `video/video_4.mp4`
   - Poids YOLO : `models_weight/yolo11x.pt`
   - Stub pour le suivi : `stubs/tracks_stubs.pkl`
2. Lancer le projet avec :

```bash
poetry run python main.py
```

La vidéo annotée sera enregistrée dans `output_videos/output_video.avi` et un rapport sera généré dans `Rapport.txt`.

---

## 📝 Fonctionnement détaillé

- **Chargement de la vidéo**  
  Le script lit la vidéo et récupère toutes les frames via la fonction `read_video`.

- **Détection et Tracking**  
  La classe `Tracker` utilise YOLO pour détecter les objets (joueurs et ballon) et ByteTrack pour les suivre.  
  Les bounding boxes, les IDs de suivi et les résultats de reconnaissance DeepFace (nom du joueur et zone du visage) sont cumulés dans un fichier stub (pickle) situé dans `stubs/tracks_stubs.pkl`.  
  Lors d’une nouvelle exécution, le script tente de charger ce stub afin de conserver les joueurs déjà reconnus (leurs noms et IDs).

- **Attribution d’équipes**  
  Le module `teams_assigner` attribue des équipes et des couleurs aux joueurs.

- **Annotation de la vidéo**  
  Le `Tracker` dessine :
  - Une bounding box principale autour de chaque détection.
  - Un rectangle bleu pour tous les visages détectés (si une zone du visage est trouvée).
  - Une flèche rouge uniquement pour les joueurs dont la reconnaissance DeepFace est réussie (lorsque `face_identity` n’est pas `None`).

- **Statistiques et Rapport**  
  Le script calcule plusieurs statistiques :
  - Nombre total de frames traitées.
  - Durée totale de la vidéo.
  - Nombre de joueurs uniques.
  - Mapping des IDs vers les noms des joueurs reconnus.
  - Informations sur la possession du ballon et les passes effectuées.
  
  Ces statistiques sont ensuite envoyées à `RapportGenerator` qui utilise l’API ChatGPT (modèle `gpt-3.5-turbo`) pour générer un rapport détaillé dans le fichier `Rapport.txt`.

- **Sauvegarde et restauration du Stub**  
  Le fichier stub (pickle) cumule les bounding boxes, le suivi des joueurs reconnus et les résultats DeepFace, permettant ainsi de conserver ces informations entre les exécutions.

---

## 💡 Contributions

- Ouvrez une issue pour proposer des améliorations.
- Forkez le projet, apportez vos modifications et soumettez une pull request.

---

## 📩 Support

Pour toute question, ouvrez une issue sur GitHub ou contactez directement l’auteur.