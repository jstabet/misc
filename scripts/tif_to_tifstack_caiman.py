import caiman as cm
import glob

for i in range (20): 
    cm.load(glob.glob(f'/home/nel/Desktop/Smart Micro/ShannonEntropy_2Dimgs/data_1/Position {i}/*.tif')).save(f'/home/nel/Desktop/yolo_pipeline/watch folder/stack{i}.tif')
