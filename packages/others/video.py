import cv2 as cv2

def display_live_video() -> None:
    facecam = cv2.VideoCapture(0)
    frame_width = int(facecam.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(facecam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = facecam.read()
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) == 27:
            break
    facecam.release()
    cv2.destroyAllWindows()