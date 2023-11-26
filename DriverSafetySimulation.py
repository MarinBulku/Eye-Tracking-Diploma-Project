import ctypes
import time
import cv2
from Objects_Methods.gaze_tacking import GazeTracking

gaze = GazeTracking()
webcam = cv2.VideoCapture(0)
video = cv2.VideoCapture("C:\\Users\\User\\Downloads\\DrivingSimulation.mp4")

# Initialize variables for gaze tracking and attention timer
attention_timer_start = None
attention_duration = 0
attention_message = ""
attention_message_displayed = False

blink_counter = 0;
many_blinks_time = False
safety_pulloff_counter = 0

while True:
    # We get a new frame from the webcam and the video
    ret, vid_frame = video.read()
    if not ret:
        break

    _, original_frame = webcam.read()
    frame = cv2.flip(original_frame, 1)
    # We send this frame to GazeTracking to analyze it
    gaze.refresh(frame)
    text = ""
    tiredness_text = ""

    # Check tiredness and other things that may impact the vision
    if gaze.is_blinking():
        blink_counter += 1

    if blink_counter > 5:
        tiredness_text = "You seem tired, or may have something in your eyes!"
        many_blinks_time = time.time()

    # Check if the gaze is not in the center
    if not gaze.is_center():
        if attention_timer_start is None:
            attention_timer_start = time.time()
        else:
            # Calculate the time gaze is away from center
            elapsed_time = time.time() - attention_timer_start
            if elapsed_time >= 5:
                # Display "Attention on the road" message
                cv2.putText(vid_frame, "Attention on the road", (10, 30), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 0, 255), 1)
                attention_message_displayed = True
                tiredness_text = "You seem tired, or may have something in your eyes!"
                blink_counter += 1
                safety_pulloff_counter += 1

        if gaze.is_center():
            attention_timer = None
            if attention_message_displayed:
                attention_message_displayed = False

    if vid_frame is not None:
        if many_blinks_time is not None and (time.time() - many_blinks_time < 5):
            cv2.putText(vid_frame, tiredness_text, (frame.shape[1] - 500, frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)

        elif many_blinks_time is not None and (time.time() - many_blinks_time > 5):
            many_blinks_time = None
            blink_counter = 0

    if safety_pulloff_counter > 50:
        ctypes.windll.user32.MessageBoxW(0, "Please pull, out now! You are not capable of driving", "ALERT", 0)
        # Display tiredness and blinking text in the bottom right corner with a smaller font size
        cv2.putText(vid_frame, tiredness_text, (vid_frame.shape[1] - 350, vid_frame.shape[0] - 10), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)


    cv2.imshow("Driving Safety simulation", vid_frame)
    if cv2.waitKey(1) == 27:
        break

webcam.release()
video.release()
cv2.destroyAllWindows()
