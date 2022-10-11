import os
from shutil import copy
from tqdm import tqdm
import pandas as pd

fairface_dataset_path = '/data/dataset/fairface-img-margin025-trainval'
output_path = "/data/dataset/vrn/examples"
if not os.path.isdir(output_path):
	os.makedirs(output_path, exist_ok=True)
csv_path = '/data/dataset/vrn/fairface-head-pose.csv'
df = pd.read_csv(csv_path)
c = 0
x = 0
for i, row in tqdm(df.iterrows(), total=df.shape[0]):
    if abs(row["yaw"]) <= 8 and abs(row["pitch"])<= 8 and abs(row["roll"]) <= 8:
        copy(f"{fairface_dataset_path}/{row['phase']}/{row['img_path']}", f"{output_path}/{c}.jpg")
        x += 1
    c += 1
print(x)