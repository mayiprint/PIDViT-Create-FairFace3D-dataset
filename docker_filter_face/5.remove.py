import os,shutil
from tqdm import tqdm
import numpy as np

path = '/data/dataset/fairface-3d/tmp/step4/'
model = 0
if model == 0:
    for i in os.listdir(path):
        for yaw in [60,75]:
            b = False
            for pitch in [0,15,-15,30,-30,45,-45]:
                if os.path.isfile(os.path.join(path, i, "{}_{}_{}.jpg".format(i,yaw,pitch))):
                    if b:
                        os.remove(os.path.join(path, i, "{}_{}_{}.jpg".format(i,yaw,pitch)))
                        print(os.path.join(path, i, "{}_{}_{}.jpg".format(i,yaw,pitch)))
                    b = True
                elif os.path.isfile(os.path.join(path, i, "{}_{}_{}.jpg".format(i,-yaw,pitch))):
                    if b:
                        os.remove(os.path.join(path, i, "{}_{}_{}.jpg".format(i,-yaw,pitch)))
                        print(os.path.join(path, i, "{}_{}_{}.jpg".format(i,-yaw,pitch)))
                    b = True
else:
    import cv2
    import tensorflow as tf
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
    def getScores(img,thresholds = [0.6, 0.7, 0.8]):
        bbox, scores, lam = mtcnn_fun(img, 80, 0.7, thresholds)
        bbox, scores, lam = bbox.numpy(), scores.numpy(), lam.numpy()

        return scores[np.argmax(scores)]

    for i in os.listdir(path):
        for yaw in [60,75]:
            l = os.listdir(os.path.join(path,i))
            l = [s for s in l if "_{}_".format(yaw) in s] + [s for s in l if "_{}_".format(-yaw) in s]
            if len(l) == 0: continue
            scores = []
            for f in l:
                img =  cv2.imread(os.path.join(path, i, f))
                score = getScores(img)
                scores.append(score)
            l.remove(l[np.argmax(scores)])
            for f in l:
                os.remove(os.path.join(path, i, f))
                print(os.path.join(path, i, f))
