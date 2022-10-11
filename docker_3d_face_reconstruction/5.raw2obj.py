import numpy as np
import imageio
import mcubes
import argparse
import os
from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

output_obj_path = "/data/dataset/fairface-3d/tmp/obj"
input_raw_path = "/data/dataset/vrn/output"
face_scaled_path = "/data/dataset/vrn/examples/scaled"
if not os.path.isdir(output_obj_path):
	os.makedirs(output_obj_path, exist_ok=True)

for file in tqdm(os.listdir(input_raw_path)):
	name = os.path.splitext(file)[0]
	im = imageio.imread(os.path.join(face_scaled_path, "{}.jpg".format(name)), as_gray=False, pilmode="RGB")
	vol = np.fromfile(os.path.join(input_raw_path, "{}.raw".format(name)), dtype=np.int8)
	vol = vol.reshape((200,192,192))
	vol = vol.astype(float)
	vertices, triangles = mcubes.marching_cubes(vol, 10)
	vertices = vertices[:,(2,1,0)]
	vertices[:,2] *= 0.5 # scale the Z component correctly
	r = im[:,:,0].flatten()
	g = im[:,:,1].flatten()
	b = im[:,:,2].flatten()
	vcx,vcy = np.meshgrid(np.arange(0,192),np.arange(0,192))
	vcx = vcx.flatten()
	vcy = vcy.flatten()
	vc = np.vstack((vcx, vcy, r, g, b)).transpose()
	neigh = NearestNeighbors(n_neighbors=1)
	neigh.fit(vc[:,:2])
	n = neigh.kneighbors(vertices[:,(0,1)], return_distance=False)
	colour = vc[n,2:].reshape((vertices.shape[0],3)).astype(float) / 255
	vc = np.hstack((vertices, colour))
	with open(os.path.join(output_obj_path,"{}.obj".format(name)), 'w') as f:
		for v in range(0,vc.shape[0]):
			f.write('v %0.2f %0.2f %0.2f %0.2f %0.2f %0.2f\n' % (vc[v,0],vc[v,1],vc[v,2],vc[v,3],vc[v,4],vc[v,5]))
		for t in range(0,triangles.shape[0]):
			f.write('f {} {} {}\n'.format(*triangles[t,:]+1))