#!pip install mediapipe opencv-python

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
#from  moviepy.editor import *
mp_drawing = mp.solutions.drawing_utils
mp_pose=mp.solutions.pose
import winsound #Import beep sound
import time

#VIDEO FEED 
cap = cv2.VideoCapture(0)

#Curl counter variable
count=0
stage=None
#Threshold limits
in_position = False
adjustment_count=0
shoulder_angle_threshold=40
elbow_angle_threshold=120
#gif=VideoFileClip("C:\\Users\\DELL\\OneDrive\\Desktop\\Bicep.webp")


##Stup media instance
with mp_pose.Pose(min_detection_confidence=0.5,min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        #gives current feed of the webcam
        #ret shows the variables and frame stores the feed in the cam
        ret,frame=cap.read()

        #Recolor image to RGB
        image=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        #MAke detection
        results = pose.process(image)

        #Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image,cv2.COLOR_RGB2BGR)

        #Calcuating angles
        def calculate_angle(a,b,c):
            a=np.array(a)
            b=np.array(b)
            c=np.array(c)

            radians= np.arctan2(c[1]-b[1],c[0]-b[0])-np.arctan2(a[1]-b[1],a[0]-b[0])
            angle=np.abs(radians*180.0/np.pi)
            
            if angle>180:
                angle = 360-angle

            return angle

        #Extract landmarks(using try bcoz if we the vidoe feed is blur we cannot detect joins and we don't want the complete function to pause bcoz of error.If it detects,itll display)
        try:
            landmarks = results.pose_landmarks.landmark
            #To grab the x,y axis of the three points ie(Left shoulder,left elbow,left wrist to substitute in above a,b,c)
            shoulder =[landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow =[landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
            wrist =[landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            #Calculate angle
            angle=calculate_angle(shoulder,elbow,wrist)

            #Figures out the alignment with respect to the webcam area
            #a=tuple(np.multiply(elbow,[640,480]).astype(int))
            #print(a)
            #Visualize

            #Cv2.Text is used to draw text on image
            #str(angle) converts the angle value to a string
            #tuple(np.multiply(elbow,[640,480]).astype(int)) determines the position of the text of the image
            #np.multiply(elbow),[640,480] multiplies (x,y) of elbow with webcam screen[640,480],This scales the elbow coordinates based on resolution.
            if not in_position and angle<=shoulder_angle_threshold:
                in_position=True
            if in_position:
                cv2.putText(image,str(angle),
                            tuple(np.multiply(elbow,[640,480]).astype(int)),
                            cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2,cv2.LINE_AA)
            ##print(landmarks)
            


            #Curl counter
            #Here is the Main prt of code for bicep press!if angle=160 ie.the hand is stretched,and if angle=30 the curl is bent and so a count is added
            if angle>85:
                stage="down"
                #Checking for the correct form
                if angle>120:
                    cv2.putText(image,'Adjust Form',(300,100),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),2,cv2.LINE_AA)
                    #Draw red circle on the image
                    cv2.putText(image,'X',(250,400),cv2.FONT_HERSHEY_SIMPLEX,15,(0,0,255),5,cv2.LINE_AA)
                    #play beep sound
                    winsound.Beep(1000,500)
                    adjustment_count+=1

            elif angle<40 and stage=="down":
                stage="up"
                if in_position:
                    count +=1
                    print(count)
                    if count==1:
                        winsound.Beep(1000,500)
                        in_position=False

        except:
            pass

        #Render curl counter
        #Setup status box
        cv2.rectangle(image,(0,0),(225,73),(245,117,16),-1)

        #Rep data
        cv2.putText(image,'REPS',(15,12),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(image,str(count),
                    (10,60),cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),2,cv2.LINE_AA)
        
        #Stage data
        cv2.putText(image,'STAGES',(65,12),
                    cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),1,cv2.LINE_AA)
        cv2.putText(image,stage,
                    (90,60),cv2.FONT_HERSHEY_SIMPLEX,2,(255,255,255),2,cv2.LINE_AA)
        

        #Time printing
        #cv2.putText(image,"{} seconds".format(elapsed_time),(0,180),cv2.FONT_HERSHEY_COMPLEX,3,(225,225,225),2,cv2.LINE_AA)
        
        #cv2.putText(image, str(int(t)), (0, 180),
         #           cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 255), 2, cv2.LINE_AA)
        
        #Displaying sample exercise video
        ##guide_np=np.array(gif)
        ##image[0:guide_np.shape[0],0:guide_np.shape[1]]=guide_np
        

        #rendering detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks,mp_pose.POSE_CONNECTIONS,
                                  mp_drawing.DrawingSpec(color=(245,117,66),thickness=2,circle_radius=2),
                                  mp_drawing.DrawingSpec(color=(245,66,230),thickness=2,circle_radius=2))
        
        #Extracting the specific landmarks
        ##len(landmarks)
        ##for lndmrk in mp_pose.PoseLandmark:
            ##print(lndmrk)

        #This gives x,y,z axis and visibliy rate
        ##print(landmarks[mp_pose.PoseLandmark.NOSE.value])

        #This gives the 'join' number ie.which part of the join among 32 joins
        ##print(mp_pose.PoseLandmark.NOSE.value)
        

        #Extracting the value 
        ##print(results)
        ##print(mp_pose.POSE_CONNECTIONS)
        
        cv2.imshow('Mediapipe Feed',image)

#To exit the loop
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

#Printing in terminal
print(f"Reps:{count}\n")
print(f"Stages : {stage}\n")
print(f"Adjustments : {adjustment_count}\n")