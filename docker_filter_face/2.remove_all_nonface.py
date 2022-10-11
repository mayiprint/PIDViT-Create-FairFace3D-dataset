import os,shutil
from tqdm import tqdm
import os,csv
import cv2
import numpy as np
import tensorflow as tf

original_path = '/data/dataset/fairface-3d/tmp/step1/'
save_path = '/data/dataset/fairface-3d/tmp/step2/'

def landmarks(img,thresholds = [0.6, 0.7, 0.8]):
    bbox, scores, lam = mtcnn_fun(img, 80, 0.7, thresholds)
    bbox, scores, lam = bbox.numpy(), scores.numpy(), lam.numpy()
    l = []
    if len(scores) < 1:
        return None
    pts = lam[np.argmax(scores)]
    for i in range(5):
        l.append([pts[i+5], pts[i]])
    
    return l

def affineMatrix(lmks, scale=2.5):
    lmks = np.array(lmks, dtype=np.float32)
    left_eye = lmks[0]
    right_eye = lmks[1]
    nose = lmks[2]
    eye_width = right_eye - left_eye
    angle = np.arctan2(eye_width[1], eye_width[0])
    center = [ left_eye[0] +  (right_eye[0]-left_eye[0])/2,nose[1]]
    #center = [(np.sum(lmks[:,0]) - lmks[2][0]) /4,(np.sum(lmks[:,1]) - lmks[2][1]) /4]
    eye_width = lmks - center
    alpha = np.cos(angle)
    beta = np.sin(angle)
    w = max(np.sqrt(np.sum(eye_width**2,axis=1))) * scale
    m = [[alpha, beta, -alpha * center[0] - beta * center[1] + w * 0.5],
         [-beta, alpha, beta * center[0] - alpha * center[1] + w * 0.5]]
    return np.array(m), (int(w), int(w))

def mtcnn_fun(img, min_size, factor, thresholds):
    #with tf.device('/cpu:0'):
    prob, landmarks, box = tf.compat.v1.import_graph_def(graph_def,
        input_map={
            'input:0': img,
            'min_size:0': min_size,
            'thresholds:0': thresholds,
            'factor:0': factor
        },
        return_elements=[
            'prob:0',
            'landmarks:0',
            'box:0']
        , name='')
    return box, prob, landmarks
with open('./mtcnn_1.12.pb', 'rb') as f:
    graph_def = tf.compat.v1.GraphDef.FromString(f.read())
    
mtcnn_fun = tf.compat.v1.wrap_function(mtcnn_fun, [
    tf.TensorSpec(shape=[None, None, 3], dtype=tf.float32),
    tf.TensorSpec(shape=[], dtype=tf.float32),
    tf.TensorSpec(shape=[], dtype=tf.float32),
    tf.TensorSpec(shape=[3], dtype=tf.float32)
])
c = 0
x = 0
if not os.path.isdir(save_path):
    os.mkdir(save_path)
for i in tqdm(os.listdir(original_path)):
    if os.path.isdir(os.path.join(original_path,i)):
        for j in os.listdir(os.path.join(original_path,i)):
            img = cv2.imread(os.path.join(original_path,i,j))
            lam = landmarks(img)
            if lam is None:
                print("exclude", j)
                continue
            lam = np.array(lam)
            mat, size = affineMatrix(lam, scale=2.35)
            if not len(np.where(np.array(cv2.warpAffine(img, mat, size).shape[:2]) > 145)[0]):
                print("exclude-min", j)
                continue
            if not os.path.isdir(os.path.join(save_path,i)):
                os.mkdir(os.path.join(save_path,i))
            print("save", j)
            shutil.copy(os.path.join(original_path,i,j), os.path.join(save_path,i,j))