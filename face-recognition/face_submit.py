import cv2
import tkinter as tk
from tkinter import filedialog
from face_recog import *
from keras.models import load_model

def submit_face_tmp():
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
        return face
        

def get_face_from_camera(cap):

    c = -1
    face = None
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            cv2.imshow('frame',frame)
            if c == 20 or c == -1:
                face = get_face_frame(frame)
                if face is not None:
                    face = format_face_frame(face,frame)
                    break
                c = 0
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            c+=1
            
        else:
            break

    # Release everything if job is finished
    cap.release()
    cv2.destroyAllWindows()
    return face

def submit_face():
    cap = cv2.VideoCapture(0)
    if cap is None or not cap.isOpened():
        face = submit_face_tmp()
        if face is None:
            print("Error: could not get user's face, exiting...")
            return None
        else:
            print("Found user's face, saving... (may take up to 1 minute)")
            model = load_model("./facenet_keras.h5")
            embed = get_embeddings(np.array([face]),model)
            print("Successfully saved! exiting...")
            return embed[0]
        # print("This node does not have a camera, exiting...")
        # return None
    input("Look directly at the camera. (Press any key to continue)")
    print("Searching for face... (press Q to quit")
    face = get_face_from_camera(cap)
    if face is None:
        print("Error: could not get user's face, exiting...")
        return None
    print("Found user's face, submitting... (may take up to 1 minute)")
    model = load_model("./facenet_keras.h5")
    embed = get_embeddings(np.array([face]),model)
    print("Successfully submitted! exiting...")
    return embed[0]

    