""" Utility module for command line script select_images
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import matplotlib.pyplot as plt

from isimage import Image

from check_cleared import check_cleared
from score_images import score_images

import numpy as np

import os

class ImageGroup(object):
    """ Collection of Image objects """
    
    def __init__ (self, images):
        """ Class initialiser """
        
        self.images = images
        if len(self.images) == 0:
            return
            
    def best (self):
        """ Returns best scored image """
        
        assert( all([hasattr(img, "score") for img in self.images]))
        
        return self.images[np.argmax([img.score for img in self.images])]
            
    def __getitem__ (self, index):
        """ Function doc """
        
        return self.images[index]
        
    def __setitem__(self, index, value):
        """ Function doc """
        
        self.images[index] = value
        
    def __len__(self):
        """ Function doc """
        
        return len(self.images)
        
    def dry (self):
        """ Reduce memory footprint for archiving. """
        
        for img in self.images:
            if hasattr(img, "img"):
                del img.img
            if hasattr(img, "mask"):
                del img.mask
            if hasattr(img, "outline"):
                del img.outline
            if hasattr(img, "pattern"):
                del img.pattern    
            if hasattr(img, "pigment"):
                del img.pigment
                
    def save(self, path, append=[]):
        """ Save image group 
            
            Parameters
            ----------
                
            path: str
                Path to a target folder.
                
            append: list, optional, default: []
                List of strings to add to the file name.

        """
            
        for i, img  in enumerate(sorted(self.images, key=lambda x: -x.score)):
            
            l, r, t, b = img.rect
            name = os.path.split(img.name)[-1].split('.')
            app = append + [str(i), str(l), str(t), str(r-l), str(b-t)]
            name = '.'.join(name[:-1] + ['_'.join(app)] + name[-1:])
            
            assert(hasattr(img, "img"))
            img.saved_name = os.path.join(path, name)
            plt.imsave(img.saved_name, img.img)
            
                
class GeneStage(object):
    """ Collection of classified and scored images corresponding to a 
        certain gene and development stage 
    """
    
    def __init__ (self, gene, stage, names, model=None, compute=None, cluster=False, verbose=False):
        """ 
        Gene stage image collection initialiser.
        
        Parameters
        ----------
            
        gene: str
            Gene name
            
        stage: float
            Development stage
            
        names: list
            List of paths to images.

        model: optional, default: None
            Path to GMM to identify cleared images, if any.

        compute: optional, default: None
            Reference to parallel cluster, if any.

        cluster: Bool, optional, default: False
            Cluster images on expression patterns if True.
        
        verbose: Bool, optional, default: False
            Visualize computation if True.
        
        """
        
        self.names = names
        self.verbose = verbose
        self.path = os.path.split(names[0])[0]
        self.gene = gene
        self.stage = stage
        
        #load and check images             
        images = [Image(name, verbose=verbose) for name in names]
        images = [image for image in images if not hasattr(image, 'valid') or image.valid]
        
        #Identify cleared images
        cleared = check_cleared([img.img for img in images], model)
        
        #score cleared images
        self.cleared = score_images(
            ImageGroup([img for img, c in zip(images, cleared) if c])
            , cluster = cluster
            , max_comp=3
            , compute=compute, verbose=verbose)
            
        #score uncleared images
        self.uncleared = score_images(
            ImageGroup([img for img, c in zip(images, cleared) if not c])
            , cluster = cluster
            , compute=compute, verbose=verbose)

        if verbose:
            print "Cleared"
            for i, img in [(i, img) for i, ig in enumerate(self.cleared) for img in ig]:
                print i, img.name, img.score

            print "Uncleared"
            for i, img in [(i, img)for i, ig in enumerate(self.uncleared) for img in ig]:
                print i, img.name, img.score
        
        
    def save(self, path):
        """ Save images in the collection """
        
        self.selected_path = os.path.join(os.path.join(path, 'selected'), os.path.split(self.path)[-1])
        if not os.path.exists(self.selected_path):
            os.makedirs(self.selected_path)
            
        self.cleared_path = os.path.join(os.path.join(path, 'cleared'), os.path.split(self.path)[-1])
        if not os.path.exists(self.cleared_path):
            os.makedirs(self.cleared_path)
        
        #Save cleared images and the best cleared image in each image group
        for i, ig in enumerate(self.cleared):
            ig.save(self.cleared_path, append=[str(i)])
            ImageGroup([ig.best()]).save(self.selected_path, append=[str(i)])

        self.uncleared_path = os.path.join(os.path.join(path, 'uncleared'), os.path.split(self.path)[-1])
        if not os.path.exists(self.uncleared_path):
            os.makedirs(self.uncleared_path)

        #Save uncleared images and the best uncleared image in each image group
        for i, ig in enumerate(self.uncleared):
            ig.save(self.uncleared_path, append=[str(i)])
            ImageGroup([ig.best()]).save(self.selected_path, append=[str(i)])
        
        
    def dry(self):
        """ Reduce memory footprint for archiving """
        
        for ig in self.cleared:
            ig.dry()
        for ig in self.uncleared:
            ig.dry()
            
        return self
        
    def find_images(self, name):
        """ Image search routine """
        
        ret = [img for cls in self.cleared for img in cls if img.name == name]
        ret += [img for cls in self.uncleared for img in cls if img.name == name]
        
        return ret        

