import numpy as np
import cv2,os
from tqdm import tqdm 
from whenet import WHENet
import csv

output_path = "/data/dataset/vrn"
if not os.path.isdir(output_path):
	os.makedirs(output_path, exist_ok=True)
csv_path = '/data/dataset/vrn/fairface-head-pose.csv'
fairface_dataset_path = '/data/dataset/fairface-img-margin025-trainval'
if __name__ == "__main__":
    model = WHENet('./model/WHENet.h5')
    x = 0
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['', 'phase','img_path', 'yaw', 'pitch', 'roll'])
        for phase in ["train","val"]:
            for root, dirs, files in os.walk(os.path.join(fairface_dataset_path, phase)):
                if(dirs != []): continue
                for i in files:
                    filePath = os.path.join(root,i)
                    img = cv2.imread(filePath)
                    img = cv2.resize(img,(224,224))
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    img_rgb = np.expand_dims(img_rgb, axis=0)
                    yaw, pitch, roll = model.get_angle(img_rgb)
                    if len(yaw) != 1: continue
                    writer.writerow([x,phase, i, yaw[0],pitch[0],roll[0]])
                    x += 1