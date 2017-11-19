""" Class Image
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.image import pil_to_array
import PIL as pil

from .find_embryo import find_embryo
from .extract_pattern import extract_pattern

zigzag_index = [ 0,  1,  5,  6, 14, 15, 27, 28,
                 2,  4,  7, 13, 16, 26, 29, 42,
                 3,  8, 12, 17, 25, 30, 41, 43,
                 9, 11, 18, 24, 31, 40, 44, 53,
                10, 19, 23, 32, 39, 45, 52, 54,
                20, 22, 33, 38, 46, 51, 55, 60,
                21, 34, 37, 47, 50, 56, 59, 61,
                35, 36, 48, 49, 57, 58, 62, 63]

ijg_q0 = np.array([[16, 11, 10, 16, 24,  40,  51,  61]
                 , [12, 12, 14, 19, 26,  58,  60,  55]
                 , [14, 13, 16, 24, 40,  57,  69,  56]
                 , [14, 17, 22, 29, 51,  87,  80,  62]
                 , [18, 22, 37, 56, 68,  109, 103, 77]
                 , [24, 35, 55, 64, 81,  104, 113, 92]
                 , [49, 64, 78, 87, 103, 121, 120, 101]
                 , [72, 92, 95, 98, 112, 100, 103, 99]
                 ])
                 
ijg_q1 = np.array([[17, 18, 24, 47, 99, 99, 99, 99]
                 , [18, 21, 26, 66, 99, 99, 99, 99]
                 , [24, 26, 56, 99, 99, 99, 99, 99]
                 , [47, 66, 99, 99, 99, 99, 99, 99]
                 , [99, 99, 99, 99, 99, 99, 99, 99]
                 , [99, 99, 99, 99, 99, 99, 99, 99]
                 , [99, 99, 99, 99, 99, 99, 99, 99]
                 , [99, 99, 99, 99, 99, 99, 99, 99]
                 ])
                 
                 

class Image(object):
    """
    Class Image wrapper class for algorithms to locate an embryo in the 
    image and extract expression pattern.
    """
    
    def __init__(self, name, add_noise=True, verbose=False):
        """ Class Image constructor
            
            
            Parameters
            ----------
            name: str
                Path to the image file
                
            add_noise: Bool, optional, default: True
                Add noise to smooth histograms of highly compressed jpegs
                and palette based images.
            
            verbose: Bool/str, optional, default: False
                Verbosity level:
                - False: silent run
                - True: report textual information
                - Path prefix: report textual information and report graphical
                    information in verbose+<suffix>.jpg files
        """
        self.verbose=verbose
        self.name = name
        self.jpeg_quality = 100
        self.palette_use = 1.
        self.add_noise = add_noise
        with open(name, "rb") as fh:
            image = pil.Image.open(fh)
            
            if image.format == 'JPEG':
                q0 = np.array(image.quantization[0])[zigzag_index].reshape(8, 8)
                if 1 in image.quantization:
                    q1 = np.array(image.quantization[1])[zigzag_index].reshape(8, 8)
                else:
                    q1 = q0.copy()
                    
                S = np.vstack([(100 * q0[:3, :3] - 50)/ijg_q0[:3, :3], (100 * q1[:3, :3] - 50)/ijg_q1[:3, :3]]).max()
                self.jpeg_quality = ((200 - S)/2 if S < 100 else 5000/S)

            if image.mode == 'P':
                csc = np.cumsum(np.array(sorted(image.getcolors(), key=lambda x:x[0]))[:, 0])
                self.palette_use = csc[csc > csc.max()/20.].shape[0]/float(len(csc))
            
            img = pil_to_array(image)
            

        if np.max(img) <= 1:
            img = np.uint8(img*255)
        self.valid = True
        if len(img.shape) < 3 or img.shape[2] < 3:
            self.valid = False
            return
        self.img = img[:, :, :3]
        
    def find_embryo(self, max_comp=2, num_layers=2, layer_size=200, smooth=True):
        """ 
            Locate an embryo in the image
            
            Parameters
            ----------
                
            max_comp: integer, optional, default: 2
                The maximum number components to segment the image into. 
                
            layer_size: integer, optional, default: 200
                The upper limit on the largest dimension of the larges layer 
                of Gaussian pyramid to use in segmentation
            
            num_layers: integer, optional, default: 2
                Number of Gaussian pyramid layers toooo use in segemntation
                
            smooth: Bool, optional, default: True
                Defines whether to smooth the embryo contour.
                    
        """
        if not self.valid:
            return self
            
        img_ = self.img.copy()
        
        if self.add_noise:
            noise = np.random.randn(np.prod(img_.shape)).reshape(img_.shape)
            nn, mx = noise.min(), img_.max()

            if self.jpeg_quality < 75: 
                noise_level = np.sqrt(img_.max() - img_.min())/4
                if self.verbose:
                    print "High jpeg compression: quality =", self.jpeg_quality 
            
                img_ = img_ + noise_level*(noise - nn)*75./self.jpeg_quality
                img_ *= mx/img_.max()
                img_ = np.uint8(img_)
                
            if self.palette_use < .75: 
                noise_level = 1./self.palette_use 
                if self.verbose:
                    print "Low palette use: poportion =", self.palette_use 

                img_ = img_ + noise_level*(noise - nn)
                img_ *= mx/img_.max()
                img_ = np.uint8(img_)

            
        ret = find_embryo(img_, max_comp=max_comp, num_layers=num_layers
                        , layer_size=layer_size, smooth=smooth, verbose=self.verbose)
                        
        if ret is None:
            self.valid = False
        else:
            self.mask, self.touches, self.rect, self.scaling = ret
            
        return self
        
    def extract_pattern (self, stain_colour=[98, 63, 127], stain_p=.5, pigment_colour=[150, 140, 54], pigment_p=.05):
        """ 
            Extract spatial distribution of the stain and pigment in the image
            
            Parameters
            ----------
            
            stain_colour: list[3], optional, default: [98, 63, 127]
                Expected colour of the stain [RGB]
                
            stain_p: float, optional, default: .5
                Confidence level in expected colour of the stain
                
            pigment_colour: list[3], optional, default: [150, 140, 54]
                Expected colour of the pigment [RGB]
                
            pigment_p: float, optional, default: .05
                Confidence level in expected colour of the pigment
        """
        
        if not self.valid:
            return self
        
        img_ = self.img.copy()
        
        if self.add_noise:
            noise = np.random.randn(np.prod(img_.shape)).reshape(img_.shape)
            nn, mx = noise.min(), img_.max()
            
            if self.jpeg_quality < 75: 
                noise_level = np.sqrt(img_.max() - img_.min())/4
            
                img_ = img_ + .5*noise_level*(noise - nn)
                img_ *= mx/img_.max()
                img_ = np.uint8(img_)
    
            
        self.pattern, self.pigment, c_est = extract_pattern(img_, self.mask
            , expected=[(stain_colour, stain_p), (pigment_colour, pigment_p)], ksize=max(3, self.scaling), verbose=self.verbose)
        self.stain_colour = c_est[0]
        self.pigment_colour = c_est[1]
        self.background_colour = c_est[2]
        
        return self
        
