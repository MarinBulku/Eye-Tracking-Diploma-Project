import cv2
import dlib
import numpy as np
from scipy.spatial import distance as dist

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
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480

# Function to calculate eye aspect ratio (EAR)
def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Load the face landmarks predictor

# Initialize webcam
cap = cv2.VideoCapture(0)

# Create a window to display eye movements, tiredness level, and gaze position
cv2.namedWindow("Eye Tracking")

# Initialize variables for eye movement analysis and tiredness detection
blink_counter = 0
tiredness_counter = 0

def shape_to_np(shape, dtype="int"):
    # Initialize an array of shape (68, 2) to store the (x, y)-coordinates
    coords = np.zeros((shape.num_parts, 2), dtype=dtype)

    # Loop over the facial landmarks and convert them to a 2-tuple of (x, y)-coordinates
    for i in range(shape.num_parts):
        coords[i] = (shape.part(i).x, shape.part(i).y)

    # Return the array of (x, y)-coordinates
    return coords

while True:
    # Read a frame from the webcam
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = detector(gray)

    for face in faces:
        # Detect the facial landmarks for the face
        shape = predictor(gray, face)
        landmarks = shape_to_np(shape)

        # Extract the eye region from the facial landmarks
        left_eye = landmarks[left_eye_indices[0]:left_eye_indices[-1] + 1]
        right_eye = landmarks[right_eye_indices[0]:right_eye_indices[-1] + 1]

        # Calculate the eye aspect ratio (EAR) for each eye
        left_ear = eye_aspect_ratio(left_eye)
        right_ear = eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # Perform eye movement analysis and tiredness detection
        if avg_ear < EAR_THRESHOLD:
            blink_counter += 1
        else:
            if blink_counter >= 3:
                # Blink detected
                print("Blink detected")

            blink_counter = 0

        if avg_ear < EAR_THRESHOLD:
            tiredness_counter += 1
        else:
            tiredness_counter = 0

        if tiredness_counter > TIREDNESS_THRESHOLD:
            # Person appears tired
            print("Person appears tired")

        # Calculate the center of the eyes
        left_eye_center = np.mean(left_eye, axis=0).astype(int)
        right_eye_center = np.mean(right_eye, axis=0).astype(int)

        # Determine the direction of eye movement
        if left_eye_center[0] < right_eye_center[0]:
            eye_movement_text = "Looking Left"
        elif left_eye_center[0] > right_eye_center[0]:
            eye_movement_text = "Looking Right"
        else:
            eye_movement_text = "Looking Straight"

        # Display the eye movement direction as text
        cv2.putText(frame, eye_movement_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Calculate the position of eye gaze on the screen
        gaze_x = int(left_eye_center[0] + right_eye_center[0]) // 2
        gaze_y = int(left_eye_center[1] + right_eye_center[1]) // 2

        # Normalize the gaze position to match the screen dimensions
        normalized_gaze_x = int(gaze_x / frame.shape[1] * SCREEN_WIDTH)
        normalized_gaze_y = int(gaze_y / frame.shape[0] * SCREEN_HEIGHT)

        # Display the position of eye gaze as a circle on the screen
        cv2.circle(frame, (gaze_x, gaze_y), 4, (0, 255, 0), -1)

        # Display the normalized gaze position as text
        gaze_position_text = f"Gaze Position: ({normalized_gaze_x}, {normalized_gaze_y})"
        cv2.putText(frame, gaze_position_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Display the eye movements and tiredness level as text
        eye_movement_text = f"Eye Movements: {eye_movement_text}"
        tiredness_text = f"Appears like tired for: {tiredness_counter} ms"

        # Display the eye movements and tiredness level as text in the window
        cv2.putText(frame, eye_movement_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, tiredness_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Display the frame in the window
    cv2.imshow("Eye Tracking", frame)

    # Break the loop if the 'q' key is pressed
    key = cv2.waitKey(1)
    if key == 27:  # Check if the "Esc" key is pressed
        print("Exiting...")
        break

# Release the webcam and close the window
cap.release()
cv2.destroyAllWindows()