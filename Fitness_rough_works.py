import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import time
import winsound

mp_drawing  = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# User inputs
age = 22
gender = "female"  # "male" or "female"
height = 155.67  # cm
weight = 56.3  # kg
exercise_calories_per_minute = 8
exercise_duration = 10  # minutes
average_heart_rate = 92

# Calculate BMR (Harris-Benedict Equation)
if gender == "male":
    bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
elif gender == "female":
    bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

# Calculate Total Calories Burned
tdee = bmr * 1.55  # Active TDEE multiplier
total_calories_burned = tdee + (exercise_calories_per_minute * exercise_duration)

# Curl counter variables
counter = 0
stage = None 
pTime=0
   
# Function to calculate angle
def calculate_angle(a,b,c):
    a = np.array(a) #First
    b = np.array(b) #Mid
    c = np.array(c) #End

    radians = np.arctan2(c[1]-b[1], c[0]-b[0])-np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle>180.0:
        angle=360-angle
    
    return angle

# Video Feed
cap= cv2.VideoCapture(0)

#time
#starting_time=time.time()
#elapsed_time=int(time.time()-starting_time)
cTime = time.time()
fps = 1/(cTime-pTime)
pTime = cTime

# Setup mediapipe instance
with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence = 0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)
        
        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract Landmarks
        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates
            shoulder1=[landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            hip1=[landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
            wrist1=[landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            ankle1=[landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

            shoulder2=[landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            hip2=[landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
            wrist2=[landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
            ankle2=[landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]


            # Calculate angle
            angle1 = calculate_angle(hip1, shoulder1, wrist1)
            angle2 = calculate_angle(hip2, shoulder2, wrist2)
            angle3 = calculate_angle(shoulder1, hip1, ankle1)
            angle4 = calculate_angle(shoulder2, hip2, ankle2)


            # Visualize angle
            cv2.putText(image, str(int(angle1)),
                            tuple(np.multiply(shoulder1, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            cv2.putText(image, str(int(angle2)),
                            tuple(np.multiply(shoulder2, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            cv2.putText(image, str(int(angle3)),
                            tuple(np.multiply(hip1, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )

            cv2.putText(image, str(int(angle4)),
                            tuple(np.multiply(hip2, [640, 480]).astype(int)),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA
                        )
            
             # Display Calories Burned
            cv2.putText(image, f'Calories Burned: {total_calories_burned:.2f}', (10, 120),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            # Curl counter logic
            if angle1 < 30 and angle2 < 30 and angle3 > 170 and angle4 > 170 :
                stage = 'down'
            if angle1 > 160 and angle2 > 160 and angle3 < 160 and angle4 < 160 and stage == 'down':
                stage = 'up'
                counter+=1

        except:
            pass


        # Render curl counter
        # Setup status box
        cv2.rectangle(image, (0, 0), (270, 73), (245, 117, 16), -1)

        # REP Data
        cv2.putText(image, 'REPS', (15, 12),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, str(counter), (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)

        # Stage Data
        cv2.putText(image, 'STAGE', (90, 12),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (85, 60),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
        #For calorie
        cv2.putText(image, f'FPS: {int(fps)}', (10, 150),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)


        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                )


        cv2.putText(image, str(int(fps)), (0, 180),
                    cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
        #Time printing
        #cv2.putText(image,"{} seconds".format(elapsed_time),(0,180),cv2.FONT_HERSHEY_COMPLEX,3,(225,225,225),2,cv2.LINE_AA)

        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()