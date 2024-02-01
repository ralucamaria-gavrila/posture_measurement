######### Imports #########
import tensorflow as tf
import numpy as np
import cv2
import mediapipe as mp
import math
import time
import random
import subprocess
import os

######### Declare necessary time variables ######### 

time_interval = 20
last_warning_time = None
last_positive_time = None
last_hip_time = None
last_ear_time = None
hip_visible = None
ear_visible = None

######### Define methods used in the process ######### 

def sound(stype):
    if stype == "negative":
        process = subprocess.Popen(["cvlc", random.choice(negative_messages)])
        print("negative")
        time.sleep(6)
        process.kill()
    elif stype == "positive": 
        process = subprocess.Popen(["cvlc", random.choice(positive_messages)])
        print("positive")
        time.sleep(6)
        process.kill()
    elif stype == "hipwarning":
        process = subprocess.Popen(["cvlc", hip_warning])
        time.sleep(5)
        process.kill()
    elif stype == "earwarning": 
        process = subprocess.Popen(["cvlc", ear_warning])
        time.sleep(5)
        process.kill()


def findAngle(x1, y1, x2, y2):
    # Make a vector from the 2 points given
    dx = x2 - x1
    dy = y2 - y1
    
    # Calculate the angle between the two vectors in radians
    angle_rad = math.atan2(dy, dx)
    
    # Angle converted to degrees
    angle_deg = math.degrees(angle_rad)
    
    return angle_deg


######### Import vocal messages #########

negative_messages_path = 'negative_audio'
positive_messages_path = 'positive_audio'
warnings_path = 'warnings'

negative_files = os.listdir(negative_messages_path)
positive_files = os.listdir(positive_messages_path)
warning_files = os.listdir(warnings_path)

negative_messages = []
positive_messages = []

for file_name in negative_files:
    file_path = os.path.join(negative_messages_path, file_name)
    with open(file_path, 'rb') as file:
        data = file.read()
        negative_messages.append(data)

for file_name in positive_files:
    file_path = os.path.join(positive_messages_path, file_name)
    with open(file_path, 'rb') as file:
        data = file.read()
        positive_messages.append(data)

for file_name in warning_files:
    file_path = os.path.join(negative_messages_path, file_name)
    with open(file_path, 'rb') as file:
        data = file.read()
        if 'ear' in file_path:
            ear_warning = data
        else:
            hip_warning = data

######### Declare the mediapipe utilities

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

message_type = input("Choose what type of messages you would like to hear: positive, negative or both: ")

side_input = input("Choose on what side of your body you will do the measurements: ")

interpreter = tf.lite.Interpreter(model_path='./3.tflite') 

interpreter.allocate_tensors()

cap = cv2.VideoCapture(0)
with mp_pose.Pose(min_detection_confidence = 0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolour image as through OpenCV we get it in color of BGR(blue, green, red) 
        # and in order to interpret it, we need it in RGB
        # Images are represented as NumPy arrays; if the image is greyscaled, the array is 2D; 
        # In case the image is coloured, the array is 3D, the third dimension represents the color channel in BGR. 
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # By making this condition false, the image cannot be changed (the pixels cannot be modified)
        image.flags.writeable = False 

        # Make detection
        results = pose.process(image)

        image.flags.writeable = True

        # Rechange colors as we want to show the image with OpenCV that only works with BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Extract landmarks
        try:
            landmarks = results.pose_landmarks.landmark
            # Draw landmarks on the image
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color = (245, 117, 66), thickness = 2, circle_radius = 2),
                                    mp_drawing.DrawingSpec(color = (245, 66, 230), thickness = 2, circle_radius = 2))
            
            cv2.imshow('HCI Project', image)

            if (side_input.lower() == 'right'):

                # Extract necessary landmarks, in our case, we do measurements using the ear, shoulder and hip
                right_shoulder_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                x_right_shoulder = right_shoulder_landmark.x
                y_right_shoulder = right_shoulder_landmark.y

                right_ear_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR]
                x_right_ear = right_ear_landmark.x
                y_right_ear = right_ear_landmark.y 

                right_hip_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
                x_right_hip = right_hip_landmark.x
                y_right_hip = right_hip_landmark.y

                if right_shoulder_landmark.visibility > 0.90 and right_hip_landmark.visibility < 0.90 and right_ear_landmark.visibility > 0.90:
                    hip_visible = False
                    if hip_visible == False: 
                        current_time = time.time()
                        if last_hip_time is None:
                            sound("hipwarning")
                            last_hip_time = current_time
                        elif current_time - last_hip_time >= time_interval:
                            sound("hipwarning")
                            last_hip_time = current_time
                else:
                    hip_visible = True
                
                if right_shoulder_landmark.visibility > 0.90 and right_hip_landmark.visibility > 0.90 and right_ear_landmark.visibility < 0.90:
                    current_time = time.time()
                    if last_ear_time is None:
                        sound("earwarning")
                        last_hip_time = current_time
                    elif current_time - last_ear_time >= time_interval:
                        sound("earwarning")
                        last_ear_time = current_time
                    
                if right_shoulder_landmark.visibility > 0.90 and right_hip_landmark.visibility > 0.90 and right_ear_landmark.visibility > 0.90:
                    # Calculate the angle between the two points
                    ear_shoulder_angle = findAngle(x_right_ear, y_right_ear, x_right_shoulder, y_right_shoulder)
                    shoulder_hip_angle = findAngle(x_right_shoulder, y_right_shoulder, x_right_hip, y_right_hip)

                    if ear_shoulder_angle > 110 and shoulder_hip_angle > 100:
                        print("negative")
                                # start tracking the time sitting slouched
                        if message_type == "negative" or message_type == "both": 
                            current_time = time.time()
                            if last_warning_time is None:
                                sound("negative")
                                last_warning_time = current_time
                            elif current_time - last_warning_time >= time_interval:
                                sound("negative")
                                last_warning_time = current_time
                    else:
                        if message_type == "both" or message_type == "positive": 
                            improved_posture_start_time = None 
                            current_time = time.time()
                            if last_positive_time is None:
                                sound("positive")
                                last_positive_time = current_time
                            elif current_time - last_positive_time >= time_interval:
                                sound("positive")
                                last_positive_time = current_time
                            
            elif side_input.lower() == 'left':
                left_shoulder_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                x_left_shoulder = left_shoulder_landmark.x
                y_left_shoulder = left_shoulder_landmark.y

                left_ear_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR]
                x_left_ear = left_ear_landmark.x
                y_left_ear = left_ear_landmark.y 

                left_hip_landmark = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
                x_left_hip = left_hip_landmark.x
                y_left_hip = left_hip_landmark.y

                if (left_shoulder_landmark.visibility > 0.90 and left_hip_landmark.visibility < 0.90 and left_ear_landmark.visibility > 0.90):
                    improved_hip_start_time = None 
                    current_time = time.time()
                    if last_hip_time is None:
                        sound("hipwarning")
                        last_hip_time = current_time
                    elif current_time - last_hip_time >= time_interval:
                        sound("hipwarning")
                        last_hip_time = current_time
                
                elif (left_shoulder_landmark.visibility > 0.90 and left_hip_landmark.visibility > 0.90 and left_ear_landmark.visibility < 0.90):
                    current_time = time.time()
                    if last_ear_time is None:
                        sound("earwarning")
                        last_hip_time = current_time
                    elif current_time - last_ear_time >= time_interval:
                        sound("earwarning")                        
                        last_ear_time = current_time

                if (left_shoulder_landmark.visibility > 0.90 and left_hip_landmark.visibility > 0.90 and left_ear_landmark.visibility > 0.90):
                    # Calculate the angle between the two points
                    ear_shoulder_angle = findAngle(x_left_ear, y_left_ear, x_left_shoulder, y_left_shoulder)
                    shoulder_hip_angle = findAngle(x_left_shoulder, y_left_shoulder, x_left_hip, y_left_hip)
                
                    if ear_shoulder_angle < 110 and shoulder_hip_angle < 100:
                        # start tracking the time sitting slouched
                        if message_type == "negative" or message_type == "both": 
                            current_time = time.time()
                            if last_warning_time is None:
                                sound("negative")
                                last_warning_time = current_time
                            elif current_time - last_warning_time >= time_interval:
                                sound("negative")
                                last_warning_time = current_time
                    else:
                        if message_type == "both" or message_type == "positive": 
                            current_time = time.time()
                            if last_positive_time is None:
                                sound("positive")
                                last_positive_time = current_time
                            elif current_time - last_positive_time >= time_interval:
                                sound("positive")
                                last_positive_time = current_time        
        except:
            pass
        
        if cv2.waitKey(10) & 0xFF== 27:
            break

cap.release()
cv2.destroyAllWindows()

