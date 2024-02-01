# posture_measurement
This project was created as a HI-fi prototype for the HCI course that took place during Module 6 - Intelligent Interaction Design from University of Twente, programme: Technical Computer Science.

## Functionality
The purpose of this project is to measure a person's posture using Python, Tensorflow, Mediapipe and OpenCv. The project can be run using a Raspberry Pi, as I used TensorflowLite which is suitable for this type of hardware. For best measurements, a webcam should be located on either the left or right side of the person, on a tripod. An external speaker is needed too. 

![Screenshot 2024-02-01 at 13 57 58](https://github.com/ralucamaria-gavrila/posture_measurement/assets/57534552/6c9a5942-eb3b-428f-95e7-ee33d6aeee33)

The way this works is by identifying the 33 keypoints using Tensorflow and Mediapipe. See below a picture with all keypoints identified by Tensorflow. 

<img width="392" alt="mediapipe_key_points" src="https://github.com/ralucamaria-gavrila/posture_measurement/assets/57534552/94e723f5-62d5-42a6-8c2c-d670130ceabf">

Out of these keypoints, I used the ear, shoulder and hip and calculated the angles between these points, as they are defined using **x**, **y** coordinates. When the angle is between a threshold that shows that the person sits slouched, a message is played such that the person should improve their posture. In case the person has a correct posture for a certain amount of time, a positive message is played, congratulating the person. The program has also audio messages for setting up the camera, in case the camera is positioned too high or too low and the person is not perfectly visible. 

## Other tools needed
### For macOS
To transfer the files from the computer to the Raspberry Pi, use the ```scp```command (e.g. ```scp -r \path\from\computer name.local:path\to\folder\in\Pi```)
As the Raspberry Pi is not connected to any display, and OpenCV needs to display the output, what worked well for me is using a server running on my computer to display the image recorded by the webcam. Thus, I used XQuartz for macOS, which can be installed using homebrew, with the command ```brew install --cask xquartz``` or by downloading the package from their [website] (https://www.xquartz.org/). After the successful installation, to use the Pi with the server running, use the command ```ssh -X username@name.local```. 

To install the necessary libraries for Python, you can use ```pip install <libraryname>```. This is needed for tensorflow, mediapipe, cv2 and numpy. 
To connect the speaker to the Pi, use this [website] (https://www.baeldung.com/linux/bluetooth-via-terminal) as a tutorial.

## Run the code
To run the code, use the command ```python3 posture_script.py```. Make sure that you have the camera plugged in and the speaker connected to the Pi. Then choose what types of messages you would like to hear and on what side the measurements are done, and that's it!
