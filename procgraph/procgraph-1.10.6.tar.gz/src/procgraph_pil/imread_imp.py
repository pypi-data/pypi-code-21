import numpy as np
from procgraph import Block, Generator, simple_block


__all__ = ['StaticImage', 'imread']

class StaticImage(Generator):
    Block.alias('static_image')
    Block.config('file', 'Static image to read')
    Block.output('rgb', 'Image rgb')
    
    def init(self):
        self.done = False

    def next_data_status(self):
        # print('Status')
        if self.done:
            # print ('Return False, none')
            return (False, None)
        else:
            # print ('Return True, none')
            return (True, 0)  # XXX: not sure
    
    def update(self):
        # print('update')
        self.set_output('rgb', imread(self.config.file), 0)
        self.done = True
    

@simple_block
def imread(filename):
    ''' 
        Reads an image from a file into a numpy array. This can have
        different dtypes according to whether it's RGB, grayscale, RGBA, etc.
        
        :param filename: Image filename.
        :type filename: string
        
        :return: image: The image as a numpy array.
        :rtype: image
    '''
    from . import Image
    try:
        im = Image.open(filename)
    except Exception as e:
        msg = 'Could not open filename "%s": %s' % (filename, e)
        raise ValueError(msg)

    data = np.array(im)

    return data


@simple_block
def imread_rgb(filename):
    '''
        Reads an image from a file using PIL and converts to an RGB array.
        
        :param filename: Filename
        :type filename: str
        
        :return: A numpy array.
        :rtype: ``array[HxWx3](uint8)``
         
    '''
    from . import Image
    try:
        im = Image.open(filename)
    except Exception as e:
        msg = 'Could not open filename "%s": %s' % (filename, e)
        raise ValueError(msg)

    im = im.convert('RGB')
    data = np.array(im)
    # print filename, data.shape, data.dtype

    assert data.ndim == 3
    assert data.dtype == np.uint8

    return data

