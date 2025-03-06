#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 10:57:51 2021

@author: nel
"""

import matplotlib

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

import os,glob
from skimage import io
import matplotlib.pyplot as plt

for path in glob.glob('/home/nel/Desktop/smart micro images/*.tiff'):

    im = io.imread(path)
    
    plt.imshow(im, cmap='gray')
    plt.title(os.path.basename(path[:-5]))
    plt.axis('off')
    
    plt.savefig(os.path.basename(path[:-4])+'pdf', dpi=300, transparent=True)