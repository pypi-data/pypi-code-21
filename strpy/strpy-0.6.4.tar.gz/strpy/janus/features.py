import os
import ctypes 
import strpy.bobo.app
import numpy as np
import strpy.janus.encoding

from strpy.bobo.util import imread, quietprint
from strpy.bobo.geometry import BoundingBox
from strpy.bobo.image import Image
import math
import sklearn.preprocessing


dsift = None  # load once

def opponentsift(im, dx=4, dy=4, binSizeX=3, binSizeY=3, weakGeometry=False, rootsift=False, do_fast=False, floatDescriptor=True, contrastThreshold=0, weakAspectRatio=False, scale=1.0):
    """vlfeat-0.9.18 dense sift across opponent color image"""
    """Reference: VAN DE SANDE ET AL.: EVALUATING COLOR DESCRIPTORS FOR OBJECT AND SCENE RECOGNITION, PAMI 2010"""
    
    # TESTING: preprocessing
    imc = im.clone();  #.float(1.0/255.0)

    # Require color image 
    if not imc.iscolor() or imc.getattribute('colorspace') != 'bgr':
        raise ValueError('BGR color image required')

    # Extract dense sift across 3 opponent color channels and concatenate
    img = imc.load()
    imga = (img[:,:,2] - img[:,:,1]) / np.sqrt(2)  # (R-G)/sqrt(2)
    imgb = (img[:,:,2] + img[:,:,1] - 2.0*img[:,:,0]) / np.sqrt(6)  # (R+G-2B)/sqrt(6)
    imgc = (img[:,:,2] + img[:,:,1] + img[:,:,0]) / np.sqrt(3)  # (R+G+B)/sqrt(3)
    
    da = densesift(Image().array(imga), dx, dy, binSizeX, binSizeY, weakGeometry=False, rootsift=rootsift, do_fast=do_fast, floatDescriptor=floatDescriptor, scale=scale)
    db = densesift(Image().array(imgb), dx, dy, binSizeX, binSizeY, weakGeometry=False, rootsift=rootsift, do_fast=do_fast, floatDescriptor=floatDescriptor, scale=scale)
    dc = densesift(Image().array(imgc), dx, dy, binSizeX, binSizeY, weakGeometry=True, rootsift=rootsift, do_fast=do_fast, floatDescriptor=floatDescriptor, scale=scale)
    d = np.hstack( (da, db, dc) )

    # Normalization
    #if rootsift:
    #    fr = d[:, -2:]
    #    d_rootsift = np.sqrt(d[:, 0:-2])
    #    d_rootsift = d_rootsift / (np.sqrt(np.sum(np.power(d_rootsift, 2.0), axis=1)).reshape((d_rootsift.shape[0],1)) + 1E-16) # row normalized
    #    d = np.hstack( (d_rootsift, fr) )

    # Weak geometry
    if weakGeometry == False:
        d = d[:, 0:-2]
    elif weakAspectRatio:
        d = np.hstack( (d, (float(imc.height()) / float(imc.width())) * np.ones( (d.shape[0], 1), dtype=np.float32)) )  # FIXME: scale

    # Remove all zero descriptors
    if contrastThreshold > 0:
        d = d[np.argwhere(np.sum(d, axis=1) > contrastThreshold), :]

    return d
    

def densesift(im, dx=4, dy=4, binSizeX=3, binSizeY=3, boundingbox=None, frames=False, weakGeometry=False, rootsift=False, weakGeometryWeight=1.0, resizeHeight=None, resizeWidth=None, scale=1.0, f_reduction=None, floatDescriptor=True, do_fast=False, do_weak_scale=False, weakAspectRatio=False, do_weak_scales=False):
    """vlfeat-0.9.18 dense sift computation"""

    if dsift is None:
        dsift = strpy.bobo.app.loadlibrary('densesift-0.9.18')
    
    # Require image to be preprocessed into canonical form (grayscale, float32)
    imc = im.clone().preprocess()  # TESTING
    #imc = im.clone().float()  # require only floating point to avoid crash, assumed preprocessed as needed by user, clone for rescale idemponence
            
    # Resize?
    if resizeHeight is not None or resizeWidth is not None:
        imc = imc.resize(rows=resizeHeight, cols=resizeWidth)
    if scale != 1.0:
        imc = imc.rescale(scale)
        
    # Bounding box?  (FIXME: scaled?)
    if boundingbox is None:
        boundingbox = BoundingBox(xmin=0, ymin=0, xmax=imc.width()-1, ymax=imc.height()-1)
    
    # Allocate memory for numFrames SIFT descriptors, library will copy into this numpy array buffer
    numFrames = ctypes.c_int(0)
    descrSize = ctypes.c_int(0)
    dsift.lib.numel_dsift(ctypes.c_int(imc.height()),
                          ctypes.c_int(imc.width()),
                          ctypes.c_int(dx),
                          ctypes.c_int(dy),                        
                          ctypes.c_int(binSizeX),
                          ctypes.c_int(binSizeY),
                          ctypes.c_int(int(boundingbox.xmin)),
                          ctypes.c_int(int(boundingbox.ymin)),
                          ctypes.c_int(int(boundingbox.xmax)),
                          ctypes.c_int(int(boundingbox.ymax)),
                          ctypes.byref(numFrames),
                          ctypes.byref(descrSize))
    numFrames = numFrames.value
    descrSize = descrSize.value
    assert descrSize==128
    d = np.zeros( (numFrames,descrSize), dtype=np.float32)
    fr = np.zeros( (numFrames,2), dtype=np.float32)

    # Dense SIFT!
    dsift.lib.dsift(imc.load().ctypes.data_as(ctypes.POINTER(ctypes.c_float)), 
                    ctypes.c_int(imc.height()),
                    ctypes.c_int(imc.width()),
                    d.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                    fr.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
                    ctypes.c_int(dx),
                    ctypes.c_int(dy),
                    ctypes.c_int(binSizeX),
                    ctypes.c_int(binSizeY),
                    ctypes.c_int(int(boundingbox.xmin)),
                    ctypes.c_int(int(boundingbox.ymin)),
                    ctypes.c_int(int(boundingbox.xmax)),
                    ctypes.c_int(int(boundingbox.ymax)),
                    ctypes.c_int(int(do_fast)))

    # Floating point?
    if not floatDescriptor:
        d = np.floor(d)

    # Root SIFT?
    if rootsift:
        d_sqrt = np.sqrt(d)
        d_norm = np.maximum(np.sqrt(np.square(d_sqrt).sum(axis=1)), 1E-16)
        d = d_sqrt / d_norm[:, np.newaxis]  # broadcast

    # Dimensionality Reduction Function? (janus.reduction.pca) 
    if f_reduction is not None:
        d = f_reduction(d)
                
    # Weak Geometry?
    if weakGeometry:
        # numFrames x 128 -> numFrames x (128+2) by appending scale normalized (x,y) position relative to bounding box
        #fr_scaled = (1.0/float(scale))*weakGeometryWeight*fr
        fr_scaled = fr
        if do_weak_scale or do_weak_scales:  # "do_weak_scales" keyword arg for backwards compatibility with pickled model files
            quietprint('[janus.features]: Weak scale feature augmentation', 3)
            # Add third dimension with scale parameter
            s = np.zeros((numFrames, 1), dtype=np.float32)
            s += scale
            d = np.concatenate( (d, ((fr_scaled[:,[0]]-boundingbox.xmin) / (boundingbox.xmax-boundingbox.xmin))-0.5, ((fr_scaled[:,[1]]-boundingbox.ymin) / (boundingbox.ymax-boundingbox.ymin))-0.5, s ) , axis=1)
        else:
            d = np.concatenate( (d, ((fr_scaled[:,[0]]-boundingbox.xmin) / (boundingbox.xmax-boundingbox.xmin))-0.5, ((fr_scaled[:,[1]]-boundingbox.ymin) / (boundingbox.ymax-boundingbox.ymin))-0.5 ) , axis=1)

                
    # Debugging
    quietprint("[janus.features.densesift][dx=%d,dy=%d,weakGeometry=%s,rootsift=%s,frames=%s,scale=%1.2f,ndescs=%d,dim=%d]: image '%s'" %
               (dx, dy, str(weakGeometry), str(rootsift), str(frames), scale, len(d), descrSize, str(im)), verbosity=2)

    # Return frames?
    if frames:
        return (d,fr/float(scale)) # (descriptor, (x,y) positions)
    else:
        return d  # descriptors only

def denseMultiscaleSIFT(im, scales, **kwargs):
    if 'scale' in kwargs: del kwargs['scale']
    D = [densesift(im, scale=s, **kwargs) for s in scales]
    return np.concatenate(D, axis=0)  # ROWS

def denseMultiscaleColorSIFT(im, scales, **kwargs):
    if 'scale' in kwargs: del kwargs['scale']
    D = [opponentsift(im, scale=s, **kwargs) for s in scales]
    return np.concatenate(D, axis=0)  # ROWS
    
def densePCAsift(im, f_pca, f_densesift=None, scales=None, **kwargs):
    """vlfeat-0.9.18 dense sift computation using janus.reduction.pca function"""
    if 'scale' in kwargs: del kwargs['scale']
    if 'f_reduction' in kwargs: del kwargs['f_reduction']                    
    if f_densesift == None:
        f_densesift = densesift
    if scales is None:
        return densesift(im, f_reduction=f_pca, scale=1.0, **kwargs)
    else:
        D = [densesift(im, f_reduction=f_pca, scale=s, **kwargs) for s in scales]
        return np.concatenate(D, axis=0)  # ROWS
    
