import cv2
import mediapipe as mp
import numpy as np
import winsound
import time

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

cap = cv2.VideoCapture(0)

# Pull-up and pull-down counter variables
pull_up_count = 0
pull_down_count = 0
pull_up_stage = None
pull_down_stage = None
active_time=0

# Threshold limits for pull-up and pull-down detection
pull_up_threshold = 160  # Adjust this value as needed
pull_down_threshold = 40  # Adjust this value as needed

# MET values for pull-ups and pull-downs (example values)
met_pull_ups = 4.0
met_pull_downs = 3.5

# Person's weight in kilograms (example weight)
person_weight_kg = 70.0

# Variables for calorie calculation
calories_burned_pull_ups = 0.0
calories_burned_pull_downs = 0.0

# Variables for tracking active time
exercise_active = False
start_time = None
end_time = None

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        def calculate_angle(a,b,c):
            a=np.array(a)
            b=np.array(b)
            c=np.array(c)

            radians= np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
            angle=np.abs(radians*180.0/np.pi)
            
            if angle>180:
                angle = 360-angle

            return angle

        try:
            landmarks = results.pose_landmarks.landmark
            shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            angle = calculate_angle(shoulder, elbow, wrist)

            if angle > pull_up_threshold:
                pull_up_stage = "down"
                if not exercise_active:
                    start_time = time.time()
                    exercise_active = True
            elif angle < pull_down_threshold and pull_up_stage == "down":
                pull_up_stage = "up"
                pull_up_count += 1
                winsound.Beep(1000, 500)

            if angle < pull_down_threshold:
                pull_down_stage = "up"
                if exercise_active:
                    end_time = time.time()
                    exercise_active = False

            if end_time is not None:
                active_time = end_time - start_time
            else:
                active_time = time.time() - start_time

            # Calculate calories burned for pull-ups and pull-downs
            calories_burned_pull_ups = met_pull_ups * active_time * person_weight_kg
            calories_burned_pull_downs = met_pull_downs * active_time * person_weight_kg

        except:
            pass

        # Display pull-up and pull-down counts
        cv2.putText(image, f'Pull-ups: {pull_up_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f'Pull-downs: {pull_down_count}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

        # Display active time
        cv2.putText(image, f'Active Time: {active_time:.2f} seconds', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

        # Display calories burned
        cv2.putText(image, f'Calories Burned (Pull-ups): {calories_burned_pull_ups:.2f} kcal', (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(image, f'Calories Burned (Pull-downs): {calories_burned_pull_downs:.2f} kcal', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow('Mediapipe Feed', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

print(f"Pull-ups: {pull_up_count}\n")
print(f"Pull-downs: {pull_down_count}\n")
print(f"Active Time: {active_time:.2f} seconds\n")
print(f"Calories Burned (Pull-ups): {calories_burned_pull_ups:.2f} kcal\n")
print(f"Calories Burned (Pull-downs): {calories_burned_pull_downs:.2f} kcal\n")

