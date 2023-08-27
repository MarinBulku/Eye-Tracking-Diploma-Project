import cv2

# Load the cascade for detecting eyes
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# Start the video capture
cap = cv2.VideoCapture(0)

while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect the eyes in the grayscale image
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Draw rectangles around the eyes
    for (x, y, w, h) in eyes:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Show the video feed with the rectangles drawn around the eyes
    cv2.imshow('Eye tracking', frame)

    # Check for a key press to exit the program
    if cv2.waitKey(1) == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()
