from procgraph import simple_block, COMPULSORY

from .pil_conversions import Image_from_array


__all__ = ['imwrite']

@simple_block
def imwrite(rgb, file=COMPULSORY):  # @ReservedAssignment
    ''' 
        Writes an image to a file.
    ''' 
    im = Image_from_array(rgb)
    im.save(file)
    
