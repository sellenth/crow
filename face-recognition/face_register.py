import tkinter as tk
import threading
import numpy as np
import cv2
from tkinter import filedialog
from keras.models import load_model
from face_recog import *

def register_face():

    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        user_in = input("This device does not have a camera. Do you want to submit an image file instead?(y/n): ")
        while user_in.lower() != "y" and user_in.lower() != "n":
            user_in = input("This device does not have a camera. Do you want to submit an image file instead?(y/n): ")
        if user_in == "n":
            print("Error: could not get user's face, exiting...")
            return None
    else:
        face = None
        while cap.isOpened():
            input("Look directly into the camera and press any button to take a picture...")
            ret,frame = cap.read()
            if ret == True:
                face = get_face_frame(frame)
                if face is not None:
                    face = format_face_frame(face,frame)
                    break
                else:
                    user_in = None
                    while user_in.lower() != "y" and user_in.lower() != "n":
                        user_in = input("No faces detected, try again? (y/n): ")
                    if user_in == "n":
                        print("Error: could not get user's face, exiting...")
                        return None
            else:
                user_in = None
                while user_in.lower() != "y" and user_in.lower() != "n":
                    user_in = input("No faces detected, try again? (y/n): ")
                if user_in == "n":
                    print("Error: could not get user's face, exiting...")
                    return None
        print("Found user's face, saving... (may take up to 1 minute)")
        model = load_model("./facenet_keras.h5")
        embed = get_embeddings(np.array([face]),model)
        cap.release()
        cv2.destroyAllWindows()
        print("Successfully saved! exiting...")
        return embed[0]


    root = tk.Tk()
    root.wm_attributes('-topmost',1)
    root.withdraw()

    face = None
    while True:
        file_path = filedialog.askopenfilename()
        if file_path == "": break
        face = get_face(file_path)
        if face is not None: break
        else: print("No face found, please try again.")
    if face is None:
        print("Error: could not get user's face, exiting...")
        return None
    else:
        print("Found user's face, saving... (may take up to 1 minute)")
        model = load_model("./facenet_keras.h5")
        embed = get_embeddings(np.array([face]),model)
        print("Successfully saved! exiting...")
        return embed[0]

