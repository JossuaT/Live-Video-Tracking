from inference_sdk import InferenceHTTPClient
import cv2


CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key="VuCR4Lpa5j69hNBAm4SU"
)

def draw_bbox_from_api_results(image_path, res, color=(255, 255, 255), thickness=2):
    # Prendre la bbox la plus confiante
    result = sorted(res['predictions'], key=lambda x: x['confidence'], reverse=True)[0]

    x, y, w, h = result['x'], result['y'], result['width'], result['height']
    # Convertir les coordonnées (l'API retourne le centre, OpenCV veut le coin haut gauche)
    x1 = int(x - (w / 2))
    y1 = int(y - (h / 2))
    x2 = int(x + (w / 2))
    y2 = int(y + (h / 2))

    # Charger l'image
    img = cv2.imread(image_path)

    # Dessiner la bounding box
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)

    # Afficher l'image pour vérifier
    cv2.imshow("Image avec BBox", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return img  # Retourne l'image modifiée

path = "data/image3.png"
results = CLIENT.infer(path, model_id="scrum-earbn/1")

print(f"Results: {results}")

draw_bbox_from_api_results(path, results)


