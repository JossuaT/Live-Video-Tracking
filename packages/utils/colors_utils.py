from sklearn.cluster import KMeans
import numpy as np
import cv2

def extract_dominant_color(cropped_image, k=3):
    """
    🎨 Extraire la couleur dominante du maillot d'un joueur en :
    - Convertissant en HSV
    - Focalisant sur la zone centrale du haut du maillot
    - Appliquant KMeans avec 3 clusters
    :param cropped_image: Image recadrée (numpy array).
    :param k: Nombre de clusters (par défaut 3).
    :return: Tuple (B, G, R) représentant la couleur dominante.
    """
    # ✅ Conversion en HSV (meilleure séparation couleur/luminosité)
    img_hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    height, width, _ = img_hsv.shape
    if height < 10 or width < 10:
        return (0, 255, 0)  # Valeur par défaut

    # 🎯 **Cibler le haut central du maillot uniquement**
    start_h = int(0.15 * height)
    end_h = int(0.4 * height)
    start_w = int(0.35 * width)
    end_w = int(0.65 * width)
    top_half = img_hsv[start_h:end_h, start_w:end_w]

    # ✅ Mise en forme pour KMeans
    img_2d = top_half.reshape(-1, 3)
    img_2d = np.float32(img_2d)

    # 🎨 Appliquer KMeans avec 3 clusters
    kmeans = KMeans(n_clusters=k, random_state=0).fit(img_2d)
    cluster_centers = kmeans.cluster_centers_

    # ✅ Éliminer les couleurs proches du vert (terrain) et du beige (peau)
    filtered_centers = [
        center for center in cluster_centers
        if not (35 <= center[0] <= 85) and center[1] > 50  # Exclure verts + faible saturation
    ]

    if len(filtered_centers) == 0:
        filtered_centers = cluster_centers  # Si tout filtré, reprendre tous

    # 🎯 Prendre la couleur avec la plus forte saturation (probable couleur du maillot)
    dominant_color_hsv = max(filtered_centers, key=lambda c: c[1])

    # ✅ Revenir à BGR
    dominant_color_bgr = cv2.cvtColor(
        np.uint8([[dominant_color_hsv]]), cv2.COLOR_HSV2BGR
    )[0][0]

    return tuple(map(int, dominant_color_bgr))