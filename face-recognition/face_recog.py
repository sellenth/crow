import os
import os.path
import numpy as np
from numpy import expand_dims
from keras.models import load_model
from mtcnn import MTCNN
import cv2

def get_face(file):
    IMAGE_SIZE = (160,160)
    detector = MTCNN()
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
    detector = MTCNN()
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

def embed_to_string(embed):
    return ",".join([str(i) for i in list(embed)])

def string_to_embed(string):
    embed = np.array(string.split(","))
    return embed.astype(np.float)
