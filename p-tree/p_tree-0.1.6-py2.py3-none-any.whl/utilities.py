# coding: utf-8

from __future__ import division, unicode_literals, print_function  # for compatibility with Python 2 and 3
import os
# import math
# import cv2
# import shutil

import numpy as np
# import pandas as pd
#
# import matplotlib.mlab as mlab
# import matplotlib as mpl
# import matplotlib.pyplot as plt

# from scipy import ndimage
from scipy import ndimage as ndi

# from skimage.morphology import watershed
# from skimage import data, io, filters, color, morphology, util, feature
# from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
# from skimage.draw import circle_perimeter
# from skimage.util import img_as_ubyte
# from skimage.filters import sobel
from PIL import Image
import pims
# import trackpy as tp
import zipfile


"""
Explain WTF your doing
"""

__author__ = 'George Pamfilis'


def cut_in_quads(f_name):
    img_orig = Image.open(f_name)
    h = img_orig.size[0]
    w = img_orig.size[1]

    quadrant_crops = [(0, 0, int(w / 2), int(h / 2)),
                      (int(w / 2), 0, w, int(h / 2)),
                      (0, int(h / 2), int(w / 2), h),
                      (int(w / 2), int(h / 2), w, h)]

    for j in range(len(quadrant_crops)):
        quadrant = img_orig.crop(quadrant_crops[j])
        quadrant.save('../Q' + str(j) + '.png')
    return None


def cut_in_half(f_name, orientation='vertical'):
    # crops = []
    img_orig = Image.open(f_name)
    # size = img_orig.size
    h = img_orig.size[0]
    w = img_orig.size[1]

    if orientation == 'vertical':
        vertical_crops = [(0, 0, int(w / 2), h), (int(w / 2), 0, w, h)]
        for j, v in enumerate(vertical_crops):
            half = img_orig.crop(v)
            half.save('../HV' + str(j) + '.png')

    elif orientation == 'horizontal':
        vertical_crops = [(0, 0, w, int(h / 2)), (0, int(h / 2), w, h)]
        for j, v in enumerate(vertical_crops):
            half = img_orig.crop(v)
            half.save('../HH' + str(j) + '.png')

    return None


def rotate_images(base_image, angle=45, n=4):
    img = Image.open(base_image)
    for i in range(n):
        img2 = img.rotate(angle * i)
        img2.save('../seed_images/seed_' + str(i) + '.png')
    return None


def filter_out_colonies(f_name):
    full_frame = pims.ImageSequence(f_name, as_grey=True)[0]

    frames = [full_frame]

    # quadrants
    for i in range(4):
        # print('Quad Frame: ',i)
        frame = pims.ImageSequence('../Q' + str(i) + '.png', as_grey=True)[0]
        frames.append(frame)

    # HV
    for i in range(2):
        # print('HV Frame: ',i)
        frame = pims.ImageSequence('../HV' + str(i) + '.png', as_grey=True)[0]
        frames.append(frame)

    # HH
    for i in range(2):
        # print('HH Frame: ',i)
        frame = pims.ImageSequence('../HH' + str(i) + '.png', as_grey=True)[0]
        frames.append(frame)

    to = []
    for c in range(9):
        #         print('Counting: ', c)
        edges = canny(frames[c] / 255., sigma=1)
        fill_coins = ndi.binary_fill_holes(edges)
        label_objects, nb_labels = ndi.label(fill_coins)
        sizes = np.bincount(label_objects.ravel())
        mask_sizes = sizes > 40
        mask_sizes[0] = 0
        coins_cleaned = mask_sizes[label_objects]
        to.append(coins_cleaned)
    return np.array(to)


def erase_directory_contents(folder='../temp'):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)
    return None


def extract_zip(path_to_zip_file, directory_to_extract_to):
    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(directory_to_extract_to)
    zip_ref.close()
    return None


if __name__ == '__main__':
    pass
