# from packages import video

# def main() -> None:
#     video.display_live_video()

# if __name__ == "__main__":
#     main()

from utils import read_video, save_video
from trackers import Tracker
from teams_assigner import TeamAssigner

def main():
    # 📹 1. Charger la vidéo
    video_path = "video/video.mp4"
    video_frames = read_video(video_path)

    # 🎯 2. Initialiser le tracker (détection + couleurs des joueurs)
    tracker = Tracker('models_weight/yolo11x.pt')
    bounding_boxes = tracker.get_bounding_boxes(
        video_frames, read_from_stub=True, stub_path='stubs/tracks_stubs.pkl'
    )

    # ✅ Initialiser le système d'assignation avec 3 clusters
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(bounding_boxes[0])

    # 🏃 **Attribution équipe/arbitre frame par frame**
    for frame_idx, frame_players in enumerate(bounding_boxes):
        for player in frame_players:
            team = team_assigner.get_player_team(player["color"])
            player["team"] = team
            player["team_color"] = team_assigner.team_color[team]

    # 🎥 5. Annoter la vidéo avec couleurs + ID + taux de confiance
    output_frames = tracker.draw_annotations(video_frames, bounding_boxes)

    # 💾 6. Sauvegarder la vidéo annotée
    save_video(output_frames, "output_videos/output_video.avi", video_path)
    print("🎉 Vidéo annotée avec attribution des équipes sauvegardée avec succès.")

if __name__ == '__main__':
    main()