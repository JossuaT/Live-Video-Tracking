## 🚀 Installation

### 1. **Cloner le dépôt**
```bash
git clone <URL_DU_DEPOT>
cd <NOM_DU_DEPOT>
```

### 2. **Créer un environnement virtuel (optionnel mais recommandé)**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Mac/Linux
venv\\Scripts\\activate    # Sur Windows
```

### 3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

---

## 📥 Télécharger les poids du modèle

⚠️ **Les poids YOLO ne sont pas inclus dans ce dépôt**, mais le dossier `models_weight` existe déjà.

Téléchargez les poids YOLO :
```bash
wget -O models_weight/yolo11x.pt https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt
```

👉 **Si `wget` n'est pas disponible** :
```bash
curl -L https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x.pt -o models_weight/yolo11x.pt
```

Dans `main.py`, assurez-vous que le chemin du modèle est correct :
```python
tracker = Tracker('models_weight/yolo11x.pt')
```

---

## 🎬 Ajouter vos vidéos

⚠️ **Le dossier `video` existe déjà**, mais il ne contient pas de vidéos.

Ajoutez vos vidéos au format `.mp4` dans `video/`.

Dans `main.py`, assurez-vous que le chemin de la vidéo est correct :
```python
video_path = "video/video.mp4"
```

---

## ⚡ Exécuter le projet

1. **Vérifiez les chemins dans `main.py`** :
```python
video_path = "video/video.mp4"  # Chemin de la vidéo
tracker = Tracker('models_weight/yolo11x.pt')  # Chemin vers les poids YOLO
```

2. **Lancer l'exécution** :
```bash
python main.py
```

📂 Le résultat sera enregistré dans `output_videos/output_video.avi`.

---

## 🏃 Fonctionnement détaillé du code (`main.py`)

1. **Chargement de la vidéo** :
```python
video_frames = read_video(video_path)
```

2. **Initialisation du tracker** :
```python
tracker = Tracker('models_weight/yolo11x.pt')
bounding_boxes = tracker.get_bounding_boxes(
    video_frames, read_from_stub=True, stub_path='stubs/tracks_stubs.pkl'
)
```

3. **Attribution des équipes** :
```python
team_assigner = TeamAssigner()
team_assigner.assign_team_color(bounding_boxes[0])

for frame_idx, frame_players in enumerate(bounding_boxes):
    for player in frame_players:
        team = team_assigner.get_player_team(player["color"])
        player["team"] = team
        player["team_color"] = team_assigner.team_color[team]
```

4. **Annotation de la vidéo** :
```python
output_frames = tracker.draw_annotations(video_frames, bounding_boxes)
```

5. **Sauvegarde de la vidéo annotée** :
```python
save_video(output_frames, "output_videos/output_video.avi", video_path)
```

---

## 🧪 Structure complète du projet

```
.
├── README.md
├── README_Detect.md
├── data
│   ├── image.jpg
│   ├── players_dataset
│   │   ├── AntoineDupont
│   │   │   └── 9.jpg
│   │   ├── JackWillis
│   │   │   └── 7.jpg
│   │   ├── ds_model_arcface_detector_opencv_aligned_normalization_base_expand_0.pkl
│   │   ├── ds_model_deepface_detector_opencv_aligned_normalization_base_expand_0.pkl
│   │   ├── ds_model_facenet512_detector_opencv_aligned_normalization_base_expand_0.pkl
│   │   ├── ds_model_facenet_detector_opencv_aligned_normalization_base_expand_0.pkl
│   │   └── ds_model_vggface_detector_opencv_aligned_normalization_base_expand_0.pkl
│   └── top14_players_database.json
├── main.py
├── models
│   ├── face_recognition_model
│   │   ├── face_detector.py
│   │   ├── face_recognition.py
│   │   └── flux_video.py
│   └── face_recognition_model.yml
├── models_weight/
├── output_videos/
├── packages
│   ├── __init__.py
│   └── video.py
├── requirements.txt
├── scripts
│   └── web_scraping
│       └── players_database_maker.py
├── stubs/
├── teams_assigner
│   ├── __init__.py
│   ├── team_assigner.py
├── tests
│   ├── test-DeepFace.ipynb
│   ├── test-HTTPserver.py
│   ├── test-app.py
│   └── test-pop-up.py
├── trackers
│   ├── __init__.py
│   └── tracker.py
├── utils
│   ├── __init__.py
│   ├── bbox_utils.py
│   ├── colors_utils.py
│   └── video_utils.py
└── video/
```

---

## 💡 Contributions

- Créez une issue pour suggérer des améliorations.
- Forkez le projet, apportez vos modifications et proposez une pull request.

---

## 📩 Support

Pour toute question, ouvrez une issue ou contactez directement Nathan Sornet.

