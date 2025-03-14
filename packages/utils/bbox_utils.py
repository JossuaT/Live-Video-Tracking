def get_center_xyxy(bbox):
    x_min, y_min, x_max, y_max = bbox
    return ((x_min + x_max) // 2, (y_min + y_max) // 2)

def get_center_xywh(bbox):
    x, y, w, h = bbox
    return (x + w // 2, y + h // 2)

def compute_distance(center1, center2):
    return ((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)**0.5
