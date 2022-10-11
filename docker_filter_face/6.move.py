import os,shutil
from tqdm import tqdm

path = '/data/dataset/fairface-3d/tmp/step4/'
obj_path = '/data/dataset/fairface-3d/tmp/step0/obj'
save_path = '/data/dataset/fairface-3d'

if not os.path.isdir(os.path.join(save_path, 'images')):
    os.mkdir(os.path.join(save_path, 'images'))
if not os.path.isdir(os.path.join(save_path, 'obj')):
    os.mkdir(os.path.join(save_path, 'obj'))
for i in os.listdir(path):
    shutil.move(os.path.join(path,i),os.path.join(save_path,'images',i))
    shutil.move(os.path.join(obj_path,"{}.obj".format(i)), os.path.join(save_path,'obj',"{}.obj".format(i)))
            