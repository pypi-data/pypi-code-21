from . import pylab
from StringIO import StringIO
import numpy as np


__all__ = ['pylab2rgb']



def pylab2rgb(transparent=False, tight=False):
    ''' Saves and returns the pixels in the current pylab figure. 
    
        Returns a RGB uint8 array. Uses PIL to do the job.
        
        If transparent is true, returns a RGBA image instead of RGB. 
    '''
    imgdata = StringIO()

    if tight:
        pylab.savefig(imgdata, format='png',
                      bbox_inches='tight', pad_inches=0)
    else:
        pylab.savefig(imgdata, format='png')

    from procgraph_pil import Image

    imgdata.seek(0)
    im = Image.open(imgdata)
    if not transparent:
        im = im.convert("RGB")
    rgb = np.asarray(im)

    if transparent:
        rgba = rgb.copy()
        white = np.logical_and(rgb[:, :, 0] == 255,
                                  rgb[:, :, 1] == 255,
                                  rgb[:, :, 2] == 255)
        alpha = rgba[:, :, 3]
        alpha[white] = 0
        # alpha[numpy.logical_not(white)] = 110 
        rgba[:, :, 3] = alpha
        return rgba

    return rgb
