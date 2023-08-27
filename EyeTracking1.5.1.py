import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist
import time

# Initialize dlib's face detector and facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

# Define the indices of the left and right eyes
left_eye_indices = [36, 37, 38, 39, 40, 41]
right_eye_indices = [42, 43, 44, 45, 46, 47]

# Define the eye aspect ratio (EAR) thresholds for blink detection and tiredness detection
EAR_THRESHOLD = 0.2
TIREDNESS_THRESHOLD = 20

# Define the screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 720, 560

# Function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Function to convert dlib shape to NumPy array
def shape_to_np(shape, dtype="int"):
    coords = np.zeros((shape.num_parts, 2), dtype=dtype)
    for i in range(shape.num_parts):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

# Function to detect pupil
def detect_pupil(eye):
    # Preprocess the eye region
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    preprocessed_eye = clahe.apply(eye)

    # Apply adaptive thresholding to handle varying lighting conditions
    thresholded_eye = cv2.adaptiveThreshold(preprocessed_eye, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresholded_eye, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and find the largest contour (presumably the pupil)
    filtered_contours = [contour for contour in contours if cv2.contourArea(contour) > 50]
    if filtered_contours:
        largest_contour = max(filtered_contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            pupil_x = int(M["m10"] / M["m00"])
            pupil_y = int(M["m01"] / M["m00"])
            return pupil_x, pupil_y
    return None, None

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a window to display eye movements, tiredness level, and gaze position
cv2.namedWindow("Eye Tracking")

# Initialize variables for eye movement analysis and tiredness detection
blink_counter = 0
tiredness_counter = 0
blink_detected_time = None

# Initialise gaze_x and gaze_y
gaze_x, gaze_y = -1, -1

# Main loop
while True:
    ret, frame = cap.read()

    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    for face in faces:
        shape = predictor(gray, face)
        if shape is None:
            continue

        landmarks = shape_to_np(shape)

        left_eye = landmarks[left_eye_indices[0]:left_eye_indices[-1] + 1]
        right_eye = landmarks[right_eye_indices[0]:right_eye_indices[-1] + 1]

        left_pupil_x, left_pupil_y = detect_pupil(gray[left_eye[0][1]:left_eye[-1][1], left_eye[0][0]:left_eye[-1][0]])
        right_pupil_x, right_pupil_y = detect_pupil(gray[right_eye[0][1]:right_eye[-1][1], right_eye[0][0]:right_eye[-1][0]])

        # Initialize normalized_gaze_x and normalized_gaze_y
        normalized_gaze_x, normalized_gaze_y = -1, -1

        # Calculate the position of eye gaze on the screen
        if left_pupil_x is not None and left_pupil_y is not None and right_pupil_x is not None and right_pupil_y is not None:
            gaze_x = (left_pupil_x + right_pupil_x) // 2
            gaze_y = (left_pupil_y + right_pupil_y) // 2
            # Normalize the gaze position to match the screen dimensions
            normalized_gaze_x = int(gaze_x / frame.shape[1] * SCREEN_WIDTH)
            normalized_gaze_y = int(gaze_y / frame.shape[0] * SCREEN_HEIGHT)

            # Display the position of eye gaze as a yellow transparent circle on the screen
            cv2.circle(frame, (normalized_gaze_x, normalized_gaze_y), 10, (0, 255, 255), -1)

            if gaze_x != -1 and gaze_y != -1:
                # Normalize the gaze position to match the screen dimensions
                normalized_gaze_x = int(gaze_x / frame.shape[1] * SCREEN_WIDTH)
                normalized_gaze_y = int(gaze_y / frame.shape[0] * SCREEN_HEIGHT)
                # Display the position of eye gaze as a yellow transparent circle on the screen
                cv2.circle(frame, (normalized_gaze_x, normalized_gaze_y), 10, (0, 255, 255), -1)
                gaze_position_text = f"Gaze Position: ({normalized_gaze_x}, {normalized_gaze_y})"
            else:
                gaze_position_text = "Gaze Position: Not detected"

        else:
            # Handle the case when pupil detection fails
            gaze_position_text = "Pupil not detected"

        # Calculate EAR and blink detection
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        if avg_ear < EAR_THRESHOLD:
            blink_counter += 1
        else:
            if blink_counter >= 3:
                blink_detected_time = time.time()
            blink_counter = 0

        tiredness_counter = tiredness_counter + 1 if avg_ear < EAR_THRESHOLD else 0

        # Display eye movements and tiredness level
        if gaze_x < normalized_gaze_x - 20:
            eye_movement_text = "Looking Left"
        elif gaze_x > normalized_gaze_x + 20:
            eye_movement_text = "Looking Right"
        else:
            eye_movement_text = "Looking Straight"

        tiredness_text = f"Appears like tired for: {tiredness_counter} ms" if tiredness_counter > TIREDNESS_THRESHOLD else "Not tired"

        # Display blink detected text for 2 seconds
        if blink_detected_time is not None and time.time() - blink_detected_time < 2:
            cv2.putText(frame, "Blink Detected!", (frame.shape[1] - 150, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display "Person appears tired" only if the person is tired
        if tiredness_counter > TIREDNESS_THRESHOLD:
            cv2.putText(frame, "Person appears tired", (10, frame.shape[0] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Display the eye movements and tiredness level as text in the window
        cv2.putText(frame, gaze_position_text, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        if gaze_position_text != "Pupil not detected":
            cv2.putText(frame, eye_movement_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.putText(frame, tiredness_text, (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("Eye Tracking", frame)

    key = cv2.waitKey(1)
    if key == 27:  # Check if the "Esc" key is pressed
        break

cap.release()
cv2.destroyAllWindows()