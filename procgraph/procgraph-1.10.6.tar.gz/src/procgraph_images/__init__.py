''' 
    Blocks for basic operations on images.

    This package contains blocks that perform basic operations
    on images. The library has no software dependency. 
    
    For more complex operations see also :ref:`module:procgraph_cv` and 
    :ref:`module:procgraph_pil`
    
    **Example**
    
    Convert a RGB image to grayscale, and back to a RGB image:::
    
    
        |input| -> |rgb2gray| -> |gray2rgb| -> |output| 

'''
from procgraph import import_magic, import_successful


procgraph_info = {
    'requires': ['numpy'],
}


np = import_magic(__name__, 'numpy')


from .filters import *
from .compose import *
from .imggrid import * 
from .images_from_dir import *
from .posterize import *

from .border import *
from .pad import *
from .blend import *
from .copied_from_reprep import *

from .reshape_smart import *
from .solid_imp import *
from .crop import *

from .alpha import *

from .reshape_rect import * 

