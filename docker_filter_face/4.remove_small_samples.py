import os,shutil
from tqdm import tqdm
import os,csv
import cv2
import numpy as np
import tensorflow as tf

original_path = '/data/dataset/fairface-3d/tmp/step3/'
save_path = '/data/dataset/fairface-3d/tmp/step4/'

if os.path.isfile(r'exclude.txt'):
    f = open(r'exclude.txt', 'r')
    data = f.read().split('\n')
    while '' in data: data.remove('')
    f.close()
else:
    data = []

if not os.path.isdir(save_path):
    os.mkdir(save_path)
for i in tqdm(os.listdir(original_path)):
    if os.path.isdir(os.path.join(original_path,i)):
        n = len(os.listdir(os.path.join(original_path,i)))
        if n <= 30 or i in data:
            print('remove', i)
            continue
        else:
            print('save', i)
            shutil.copytree(os.path.join(original_path,i), os.path.join(save_path,i))