import cv2
import mediapipe as mp
import time

# Initialize Mediapipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize webcam
cap = cv2.VideoCapture(0)

# Calculate the end time for the countdown (3 minutes from now)
end_time = time.time() + 3 * 60
 
while time.time() < end_time:
    ret, image = cap.read()
    
    # Your pose detection and drawing code here...
    
    # Calculate the remaining time in seconds
    remaining_time = max(0, int(end_time - time.time()))
    
    # Convert remaining time to hh:mm:ss format
    hours = remaining_time // 3600
    minutes = (remaining_time % 3600) // 60
    seconds = remaining_time % 60
    countdown_text = f"{hours:02}:{minutes:02}:{seconds:02}"
    
    # Display countdown text
    cv2.putText(image, countdown_text, (0, 180),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
    
    # Display the image
    cv2.imshow('Mediapipe Feed', image)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()