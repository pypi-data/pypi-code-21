#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午5:23
# @Author  : Hou Rong
# @Site    : 
# @File    : Image.py
# @Software: PyCharm
import six
from scipy import misc


def is_complete_scale_ok(image_name, min_sum_pixels=200000, min_scale=0.9, max_scale=2.5):
    """
    Check the completeness and whether the scale of the Image is ok
    Using Library scipy.misc
    :param image_name: '1.jpg', not'dir/1.jpg'
    :param min_sum_pixels: the min sum of the pixels of image
    :param min_scale: the min scale of image
    :param max_scale: the max scale of image
    :return:
    flag:
        If the scale of the image is ok, return flag 0;
        If the image can't be opened(is broken), return flag 1;
        If the image is incomplete, return flag 2;
        If the sum of the pixels is less than the min, return flag 3;
        If the scale of the image is less than min_scale, return flag 4;
        If the scale of the image is greater than max_scale, return flag 5;
    height: the height of the image. If broken or incomplete, -1;
    width: the width of the image. If broken or incomplete, -1;
    """

    flag = 0

    try:
        img = misc.imread(image_name)
    except IOError:
        print('open image file ' + image_name + ' fails')
        flag = 1
        return flag, -1, -1

    # incompleteness
    if img.shape == () or img.size == 1:
        flag = 2
        return flag, -1, -1

    if len(img.shape) == 3:
        height, width, channels = img.shape
    else:
        height, width = img.shape

    # sum of pixels
    sum_pixels = height * width
    if sum_pixels < min_sum_pixels:
        flag = 3

    # scale
    scale = float(width) / float(height)
    if scale < min_scale:
        if width < 500:
            flag = 4
    if scale > max_scale:
        flag = 5

    return flag, height, width
