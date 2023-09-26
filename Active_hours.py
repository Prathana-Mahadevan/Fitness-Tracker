import cv2

# Open the webcam
cap = cv2.VideoCapture(0)  # Use 0 for the default webcam, 1 for the second, and so on

# Initialize variables
prev_frame = None
active_time = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # Convert frame to grayscale for motion detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if prev_frame is None:
        prev_frame = gray
        continue

    frame_diff = cv2.absdiff(prev_frame, gray)
    thresh = cv2.threshold(frame_diff, 30, 255, cv2.THRESH_BINARY)[1]

    # Count active frames
    active_pixels = cv2.countNonZero(thresh)
    if active_pixels > 1000:  # Adjust this threshold as needed
        active_time += 1

    prev_frame = gray

    # Display active seconds on the video frame
    cv2.putText(frame, f"Active Seconds: {active_time}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame with motion detected
    cv2.imshow("Motion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
