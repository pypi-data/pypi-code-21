# -*- coding: utf-8 -*-

# Copyright (C) 2016 Andreu Casas
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details: 
# https://www.gnu.org/licenses/gpl-3.0.en.html

"""
This python module provides a set of functions implement computer vision
techniques for the study of politics

Please cite as:
<add-cambridge-elements-ref-in-here>    

"""

import numpy as np
import matplotlib.pyplot as plt

def imshow(inp, title=None):
    """
    Description: This function takes a grid of images and shows them, making 
    image visualization easy.
    
    Parameters:
        `inp`:      type <torch.FloatTensor> object
        `title`:    type <list> of strings indicating the labels of the `inp` 
                        images
    
    Output:
        shows the images and their labels (if provided)
    """
    inp = inp.numpy().transpose((1, 2, 0))
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    inp = std * inp + mean
    inp = np.clip(inp, 0, 1)
    plt.imshow(inp)
    if title is not None:
        plt.title(title)
    plt.pause(0.001)