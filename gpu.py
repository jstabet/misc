import torch
print(f'Pytorch GPU is availbale: {torch.cuda.is_available()}', end='\n\n')

import tensorflow as tf
print(f'\nTensorflow GPU is available: {tf.config.list_physical_devices('GPU')}')
