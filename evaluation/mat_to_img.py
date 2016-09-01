import argparse
import cv2 
import numpy as np
from scipy.misc import imread
from scipy.io import loadmat
import string
import os
import skimage.io as skio
import sys 

parser = argparse.ArgumentParser(
    description="Convert mat file to set of labelled images.")
parser.add_argument('-f', '--file',
                    help="Path to matrix")
parser.add_argument('-o', '--output',
                    help="Path to write output mat")
parser.add_argument('-b', '--background',
                        help="Intensity of background pixels",
                        default=255)
args = parser.parse_args()

def simplify(x, background_color):
        y = 0 if x == background_color else 255
        return y

def main():
        background_color = int(args.background)

        mat = loadmat(args.file)['GT']
        
        f = np.vectorize(simplify)
        mat = f(mat, background_color)
    
        for x in range(mat.shape[2]):
            skio.imsave(os.path.join(args.output, 'img%d.png' % x), mat[:, :, x])


if __name__ == '__main__':
    main()

