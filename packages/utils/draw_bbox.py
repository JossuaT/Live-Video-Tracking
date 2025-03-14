import cv2

def draw_annoted_bbox_on_frame (frame, bbox, color, label, confidence):
    x_min, y_min, x_max, y_max = bbox
    cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color, 2)
    cv2.putText(frame, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    confidence_text = f"{confidence:.1f}%"
    (conf_w, conf_h), _ = cv2.getTextSize(confidence_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
    cv2.rectangle(frame, (x_max - conf_w, y_min - conf_h - 5), (x_max, y_min), color, -1)
    cv2.putText(frame, confidence_text, (x_max - conf_w, y_min - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    return frame

def draw_arrow_on_frame (frame, bbox, color=(0, 0, 255), thickness=5, tipLength=0.5):
    x_min, y_min, x_max, y_max = bbox
    arrow_tail = ((x_min + x_max) // 2, max(0, y_min - 40))
    arrow_tip = ((x_min + x_max) // 2, y_min)
    cv2.arrowedLine(frame, arrow_tail, arrow_tip, color, thickness, tipLength=tipLength)
    return frame