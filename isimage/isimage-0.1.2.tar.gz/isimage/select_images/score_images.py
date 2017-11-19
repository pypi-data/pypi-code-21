""" Utility module for command line script select_images
"""
# Author: Ilya Patrushev ilya.patrushev@gmail.com

# License: GPL v2.0

import numpy as np
import cv2

from isimage import cluster_patterns

def score_images(images, max_comp=2, cluster=False, compute=None, verbose=False):
    """ 
        High level image scoring algorithm utilsing isimage module.
        
        Parameters
        ----------
            
        images: 
            Image group to score
            
        max_comp: integer, optional, default: 2
            Max componet parameter for find_embryo routine.

        cluster: Bool, optional, default: False
            Cluster expression patterns if True.

        compute: optional, default: None
            Reference to parallel cluster if any.

        verbose: Bool, optional, default: True
            Visualize computation if True.
        
        Returns
        -------
        
        list
            List of image groups that contain valid and scored images 
    """

    images_t = type(images)
    
    if len(images) == 0:
        return []
        
    if compute is not None:
        clen = len(images)
    
    #locating embryos    
    if compute is None or verbose:
        [img.find_embryo(max_comp=max_comp, layer_size=200) for img in images]
    elif len(images) > 0:
        for grp in range(len(images)/clen + 1):
            if len(images[grp*clen:(grp + 1)*clen]) > 0:
                images[grp*clen:(grp + 1)*clen] = compute.map(lambda (img, mc): img.find_embryo(max_comp=mc, layer_size=200), zip(images[grp*clen:(grp + 1)*clen], [max_comp]*clen)).result

    #removing images where the embryo touches an image edge 
    #except for gene/stages where all images touch an image edge
    images = [img for img in images if img.valid]
    if not all([img.touches for img in images]):
        images = [img for img in images if not img.touches]
    
    #compesating differences in background luminosity 
    lum = []
    labs = []
    for img in images:
        if not img.touches:
            l, r, t, b = img.rect
            img.img = img.img[t:b, l:r]
            img.mask = img.mask[t:b, l:r]

        labs += [cv2.cvtColor(img.img, cv2.COLOR_RGB2LAB)]
        lum += [np.mean(labs[-1][img.mask == 0].reshape(-1, 3)[:, 0])]

    lum_corr = np.mean(lum) - np.array(lum)
    
    for img, lab, lc in zip(images, labs, lum_corr):
        img.img_saved = img.img.copy()
        lab[:, :, 0] = np.minimum(255, np.maximum(0, lab[:, :, 0] + lc))
        img.img = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)
        
    del labs
    
    #extracting patterns
    if compute is None or verbose:
        [img.extract_pattern() for img in images]
    elif len(images) > 0:
        for grp in range(len(images)/clen + 1):
            if len(images[grp*clen:(grp + 1)*clen]) > 0:
                images[grp*clen:(grp + 1)*clen] = compute.map(lambda img: img.extract_pattern(), images[grp*clen:(grp + 1)*clen]).result

    #scoring and restoring image
    for img in images:
        img.score = np.percentile(img.pattern[(img.mask == 1)], 85) if np.any((img.mask == 1)) else 0 # & (img.pattern > 0) & (img.pattern > 0)
        img.img = img.img_saved
        del img.img_saved
        
    #clustering if needed
    if cluster:
        norms = np.array([np.sqrt(np.mean(img.pattern[img.mask == 1]**2)) for img in images])
        norms[norms < 1.e-2] = 1
        labels, D, cluster_centers = cluster_patterns([img.pattern/norm for img, norm in zip(images, norms)], max_clusters=4, compute=compute) #, verbose=True, opt_images=[img.img for img in images])
        
        groups = []
        for label in range(int(max(labels))+1):
            group = images_t([img for l, img in zip(labels, images) if l == label])
            scores = D[cluster_centers[label], labels == label]
            for img, score in zip(group, scores):
                img.score += score
            groups += [group]
        return groups
        
    else:
        return [images_t(images)]
