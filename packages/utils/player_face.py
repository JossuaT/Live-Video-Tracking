from packages.utils import get_center_xyxy

def is_player_face(player_bbox, face_bbox):
    """
    Retourne TRUE si le centre de la bbox du visage est contenu dans le tier supérieur de la bbox du joueur
    """
    px_min, py_min, px_max, py_max = player_bbox
    fx_min, fy_min, fx_max, fy_max = face_bbox
    # Recherche du premier tier
    py_tier = (py_min + py_max) // 3
    # Recherche du milieu du visage
    _, fy_center = get_center_xyxy(face_bbox)
    if fy_center <= py_tier:
        return True
    else:
        return False
