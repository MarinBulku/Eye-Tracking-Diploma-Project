import time
import cv2
from Objects_Methods.gaze_tacking import GazeTracking

# Gaze initial coordinates
left_gaze_x, left_gaze_y = -1, -1
right_gaze_x, right_gaze_y = -1, -1

blink_counter = 0
many_blinks_time = None

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)

while True:
    _, original_frame = webcam.read()
    frame = cv2.flip(original_frame, 1)
    gaze.refresh(frame)

    frame = gaze.annotated_frame()
    text = ""
    tiredness_text = ""
    blinking_text = ""

    if gaze.is_blinking():
        blinking_text = "Blink Detected"
        blink_counter += 1

    if blink_counter > 5:
        tiredness_text = "You seem tired, or may have something in your eyes!"
        many_blinks_time = time.time()

    if gaze.is_right():
        text = "Looking right"
    elif gaze.is_left():
        text = "Looking left"
    elif gaze.is_center():
        text = "Looking center"

    if gaze.horizontal_ratio() is not None and gaze.vertical_ratio() is not None:
        horizontal_ratio = gaze.horizontal_ratio()
        vertical_ratio = gaze.vertical_ratio()

        horizontal_offset = int(horizontal_ratio * frame.shape[1])
        vertical_offset = int(vertical_ratio * frame.shape[0])

        gaze_x = int(horizontal_offset)
        gaze_y = int(vertical_offset)

        cv2.circle(frame, (gaze_x, gaze_y), 10, (0, 255, 0), -1)


    cv2.putText(frame, f"Left pupil: {gaze.pupil_left_coords()}", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                (74, 5, 171),1)
    cv2.putText(frame, f"Right pupil: {gaze.pupil_right_coords()}", (10, 60), cv2.FONT_HERSHEY_DUPLEX, 0.6,
                (74, 5, 171), 1)
    cv2.putText(frame, f"Gaze: {text}", (10, 90), cv2.FONT_HERSHEY_DUPLEX, 0.6, (74, 5, 171), 1)
    cv2.putText(frame, blinking_text, (frame.shape[1] - 350, frame.shape[0] - 50), cv2.FONT_HERSHEY_DUPLEX, 0.5,
                (0, 0, 255), 1)

    if many_blinks_time is not None and (time.time() - many_blinks_time < 50):
        cv2.putText(frame, tiredness_text, (frame.shape[1] - 475, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX,0.5,(0, 0, 255), 1)
    elif many_blinks_time is not None and (time.time() - many_blinks_time > 50):
        many_blinks_time = None
        blink_counter = 0

    cv2.imshow("Eye Tracking Application", frame)

    if cv2.waitKey(1) == 27:
        break

webcam.release()
cv2.destroyAllWindows()