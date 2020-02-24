import os
import os.path
import cv2
import numpy as np
from mtcnn import MTCNN
from numpy import savez_compressed
from numpy import load
from numpy import expand_dims
from keras.models import load_model
from sklearn.svm import SVC 
from sklearn.preprocessing import LabelEncoder

#REQUIRED PIP INSTALLS:
# opencv, numpy, mtcnn, keras, sklearn, tensorflow
# requires python 3.6
# requires numpy version 1.16.2, do pip install numpy==1.16.2

#returns a cropped image of the face located in the file

def get_face(file):
    IMAGE_SIZE = (160,160)
    detector = MTCNN()
    img = cv2.cvtColor(cv2.imread(file),cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(img)
    if len(faces) < 1:
        raise ValueError('No faces detected')
    x,y,width,height = faces[0]["box"]
    cropped = cv2.resize(img[y:y+height,x:x+width],IMAGE_SIZE)
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

#train an SVM to predict images

def train_SVM():
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train = dataset['arr_0'], dataset['arr_1']
    labels_modified = []
    embeds_modified = []
    for i in range(len(embeds_train)):
        for j in range(len(embeds_train[i])):
            embeds_modified.append(embeds_train[i][j])
            labels_modified.append(labels_train[i])
    labels_modified = np.array(labels_modified)
    embeds_modified = np.array(embeds_modified)
    encoder = LabelEncoder().fit(labels_modified)
    labels_modified = encoder.transform(labels_modified)
    SVM = SVC(kernel='linear',probability=True).fit(embeds_modified,labels_modified)
    return encoder,SVM

#predict a single image using the SVM from train_SVM()
#file is path to image to predict
#model is loaded from facenet_keras.h5

def predict_face(encoder,svm,file,model):
    face = get_face(file)
    embed = get_embeddings(np.array([face]),model)
    pred_class = svm.predict(embed)
    pred_prob = svm.predict_proba(embed)
    prediction = encoder.inverse_transform(pred_class)
    probability = pred_prob[0,pred_class[0]]*100
    return prediction,probability

#gets the embedding with the shortest euclidian distance to the input image file

def lowest_euclidian_distance(file,model):
    face = get_face(file)
    embed = get_embeddings(np.array([face]),model)
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    lowest = 10
    classification = None
    image = None
    for i in range(len(embeds_train)):
        for j in range(len(embeds_train[i])):
            dist = get_euclidean_distance(embeds_train[i][j],embed[0])
            if dist < lowest:
                lowest = dist
                classification = labels_train[i]
                image = images_train[i][j]
    if lowest == 10:
        print("ERROR in finding image")
        return
    return lowest,classification,image

#same as above, but uses a greedy algorithm with greedy choice being:
#skip at distance > 1
#return at distance < 0.6

def lowest_euclidian_distance_greedy(file,model):
    face = get_face(file)
    embed = get_embeddings(np.array([face]),model)
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    lowest = 10
    classification = None
    image = None
    for i in range(len(embeds_train)):
        for j in range(len(embeds_train[i])):
            dist = get_euclidean_distance(embeds_train[i][j],embed[0])
            if dist >= 1:
                break
            if dist <= 0.60:
                lowest = dist
                classification = labels_train[i]
                image = images_train[i][j]
                return lowest,classification,image
            if dist < lowest:
                lowest = dist
                classification = labels_train[i]
                image = images_train[i][j]
    if lowest == 10:
        print("ERROR in finding image")
        return
    return lowest,classification,image


#add a new face embedding to the dataset
#directory is the directory of all faces
#name is the name the image will be saved under
#file is a path to the image file

def add_to_dataset(directory,model,file,name):
    dataset = load('face_embeds_dataset.npz')
    labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    face = get_face(file)
    embed = get_embeddings(np.array([face]),model)
    embeds_tmp = list(embeds_train)
    labels_tmp = list(labels_train)
    images_tmp = list(images_train)
    if(name in labels_tmp):
        idx = labels_tmp.index(name)
        images_id = list(images_tmp[idx])
        embeds_train[idx] = np.append(embeds_train[idx],embed,axis=0)
        images_id.append(cv2.imread(file))
        images_train[idx] = np.array(images_id)
    else:
        labels_tmp.append(name)
        images_tmp.append(np.array([cv2.imread(file)]))
        embeds_tmp.append(np.array(embed))
        embeds_train = np.array(embeds_tmp)
        labels_train = np.array(labels_tmp)
        images_train = np.array(images_tmp)

    filepath = directory+name

    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    num = len([name for name in os.listdir(filepath) if os.path.isfile(os.path.join(filepath, name))])
    cv2.imwrite(filepath+"/"+str(num)+".jpg",cv2.imread(file))
    print("finished adding entry: " + name + ". saving...")
    savez_compressed('face_embeds_dataset.npz',labels_train,embeds_train,images_train)
    
#create a brand new dataset from the specified directory
#replaces the current dataset if force is set to true
#does not create a new dataset if one is already found

def create_dataset(directory,model,force=False):
    if os.path.isfile("./face_embeds_dataset.npz") and not force:
        print("dataset already found")
        return
    embeds_train = []
    labels_train = []
    images_train = []
    train_dir = directory + "train/"
    for name in os.listdir(train_dir):
        cropped_faces = []
        uncropped_faces = []
        for img in os.listdir(train_dir+name):
            uncropped_faces.append(cv2.imread(train_dir+name+'/'+img))
            face = get_face(train_dir+name+'/'+img)
            cropped_faces.append(face)
        cropped_faces = np.array(cropped_faces)
        embeds_ = get_embeddings(cropped_faces,model)
        embeds_train.append(embeds_)
        uncropped_faces = np.array(uncropped_faces)
        images_train.append(uncropped_faces)
        labels_train.append(name)
    labels_train = np.array(labels_train)
    embeds_train = np.array(embeds_train)
    images_train = np.array(images_train)

    print("dataset done, saving...")
    savez_compressed('face_embeds_dataset.npz',labels_train,embeds_train,images_train)


def main():
    model = load_model("./facenet_keras.h5")
    create_dataset("./data/",model)
    enc,svm = train_SVM()
    pred,prob = predict_face(enc,svm,"./data/val/ben_afflek/33.jpg",model)
    print(pred[0])
    print(prob)
    print('------------')
    dist,classification,image = lowest_euclidian_distance("./data/val/steve_jobs/22.jpg",model)
    print(classification)
    print(dist)
    print('------------')
    dist,classification,image = lowest_euclidian_distance_greedy("./data/val/steve_jobs/22.jpg",model)
    print(classification)
    print(dist)

if __name__ == "__main__":
    main()



###############################

## EXTRA DEBUG CODE ##

###############################

    # dataset = load('face_embeds_dataset.npz')
    # labels_train,embeds_train, images_train = dataset['arr_0'], dataset['arr_1'], dataset['arr_2']
    # labels_tmp = list(labels_train)
    # embeds_tmp = list(embeds_train)
    # images_tmp = list(images_train)
    # labels_tmp.pop()
    # embeds_tmp.pop()
    # images_tmp.pop()
    # labels_train = np.array(labels_tmp)
    # embeds_train = np.array(embeds_tmp)
    # images_train = np.array(images_tmp)
    # for i in labels_train:
    #     print(i)
    # print("----")
    # for i in embeds_train:
    #     print(i.shape)
    # print("----")
    # for i in images_train:
    #     print(i.shape)
    # savez_compressed('face_embeds_dataset.npz',labels_train,embeds_train,images_train)  