import os,shutil
from tqdm import tqdm
import os,csv
import cv2
import numpy as np
import tensorflow as tf


original_path = '/data/dataset/fairface-3d/tmp/step2/'
save_path = '/data/dataset/fairface-3d/tmp/step3/'

def getScores(img,thresholds = [0.6, 0.7, 0.8]):
    bbox, scores, lam = mtcnn_fun(img, 80, 0.7, thresholds)
    bbox, scores, lam = bbox.numpy(), scores.numpy(), lam.numpy()

    return scores[np.argmax(scores)]

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
    if os.path.isdir(os.path.join(original_path, i)):
        if os.path.isdir(os.path.join(save_path, i)):
            shutil.rmtree(os.path.join(save_path, i))
        shutil.copytree(os.path.join(original_path, i), os.path.join(save_path, i))
        for pitch in [-45,-30,-15,0,15,30,45]:
            for yaw in [15,30,45,60,75]:
                if not os.path.isfile(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,yaw,pitch))) or not os.path.isfile(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,-yaw,pitch))):
                    continue
                a1 =  cv2.imread(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,yaw,pitch)))
                a2 =  cv2.imread(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,-yaw,pitch)))
                scores = [getScores(a1),getScores(a2)]
                if np.argmax(scores):
                    os.remove(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,-yaw,pitch)))
                    print("remove", "{}_{}_{}.jpg".format(i,-yaw,pitch))
                else:
                    os.remove(os.path.join(save_path, i,"{}_{}_{}.jpg".format(i,yaw,pitch)))
                    print("remove", "{}_{}_{}.jpg".format(i,yaw,pitch))
            