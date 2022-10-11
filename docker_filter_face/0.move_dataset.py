import os
import shutil
from tqdm import tqdm
# 取得所有檔案與子目錄名稱
face_path = '/data/dataset/fairface-3d/tmp/image'
obj_path = '/data/dataset/fairface-3d/tmp/obj'
save_path = '/data/dataset/fairface-3d/tmp/step0'
if not os.path.isdir(os.path.join(save_path,'obj')):
    os.makedirs(os.path.join(save_path,'obj'))
if not os.path.isdir(os.path.join(save_path,'image')):
    os.makedirs(os.path.join(save_path,'image'))
for i in tqdm(os.listdir(face_path)):
    if "_75_45.jpg" not in i: continue
    i = i.replace('_75_45.jpg', '')
    if not os.path.isfile(os.path.join(obj_path, "{}.obj".format(i))): continue
    if not os.path.isdir(os.path.join(save_path,'image',i)):
        os.makedirs(os.path.join(save_path,'image',i))
    shutil.move(os.path.join(obj_path,"{}.obj".format(i)), os.path.join(save_path,'obj',"{}.obj".format(i)))
    for yaw in [-75,-60,-45,-30,-15,0,15,30,45,60,75]:
        for pitch in [-45,-30,-15,0,15,30,45]:
            shutil.move(
                os.path.join(face_path,"{}_{}_{}.jpg".format(i, yaw, pitch)),
                os.path.join(save_path, 'image', i, "{}_{}_{}.jpg".format(i, yaw, pitch)),
            )