import os
import os.path
import numpy as np
from numpy import savez_compressed
from numpy import load
from numpy import expand_dims
from keras.models import load_model
from mtcnn import MTCNN
import cv2
import face_database as db
import time

detector = MTCNN()

def get_face(file):
    IMAGE_SIZE = (160,160)
    try:
        img = cv2.cvtColor(cv2.imread(file),cv2.COLOR_BGR2RGB)
        faces = detector.detect_faces(img)
        if len(faces) < 1:
            print('No faces detected')
            return None
        x,y,width,height = faces[0]["box"]
        cropped = cv2.resize(img[y:y+height,x:x+width],IMAGE_SIZE)
        return cropped
    except:
        return None



def get_face_frame(frame):
    faces = detector.detect_faces(frame)
    if len(faces) < 1:
        print('No faces detected')
        return None
    return faces

def format_face_frame(faces,frame):
    IMAGE_SIZE = (160,160)
    x,y,width,height = faces[0]["box"]
    cropped = cv2.resize(frame[y:y+height,x:x+width],IMAGE_SIZE)
    return cropped

#standardize pixel values

def prewhiten(x):
    if x.ndim == 4:
        axis = (1, 2, 3)
        size = x[0].size
    elif x.ndim == 3:
        axis = (0, 1, 2)
        size = x.size
    else:
        raise ValueError('Dimension should be 3 or 4')

    mean = np.mean(x, axis=axis, keepdims=True)
    std = np.std(x, axis=axis, keepdims=True)
    std_adj = np.maximum(std, 1.0/np.sqrt(size))
    y = (x - mean) / std_adj
    return y

#normalize embedding vectors

def l2_normalize(x, axis=-1, epsilon=1e-10):
    output = x / np.sqrt(np.maximum(np.sum(np.square(x), axis=axis, keepdims=True), epsilon))
    return output

#returns a list of embeddings from the list of images passed in
#list of images must be of type np.ndarray
#model is loaded from facenet_keras.h5

def get_embeddings(imgs,model):
    imgs = prewhiten(imgs)
    raws = []
    for raw in imgs:
        img = expand_dims(raw,axis=0)
        raws.append(model.predict(img))
    embeds = l2_normalize(np.concatenate(raws))
    return embeds

#return the distance between 2 embeddings

def get_euclidean_distance(emb1,emb2):
   return np.linalg.norm(emb1-emb2)

#gets the embedding with the shortest euclidian distance to the input embedding

def lowest_euclidian_distance(embed,model):
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    lowest = 10
    classification = "None"
    for i in range(len(embeds_train)):
        for j in range(len(embeds_train[i])):
            dist = get_euclidean_distance(embeds_train[i][j],embed)
            if dist < lowest:
                lowest = dist
                classification = labels_train[i]
    if lowest == 10:
        print("ERROR in finding match: could not find match")
    return lowest,classification
    
#return list of embeddings that fall below a certain threshold

def lowest_euclidian_distance_list(embed,model,upper,lower):
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    classification_list = []
    for i in range(len(embeds_train)):
        for j in range(len(embeds_train[i])):
            dist = get_euclidean_distance(embeds_train[i][j],embed)
            if dist >= upper:
                break
            if dist <= lower:
                classification_list.append((labels_train[i],dist)) 
                break   
    return classification_list

def get_face_from_camera():

    cap = cv2.VideoCapture(0)
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

def main():
    model = load_model("./facenet_keras.h5")
    # db_conn = db.init_db()
    # all_embeds = db.getall_from_db(db_conn)
    # print(all_embeds)

    face = get_face_from_camera()
    embeds = get_embeddings(np.array([face]),model)
    cv2.imshow("face",face)
    cv2.waitKey(0)



  
if __name__ == "__main__":
  main()
