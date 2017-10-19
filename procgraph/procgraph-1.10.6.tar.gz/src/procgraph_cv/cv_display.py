from . import cv, np
from .conversions import numpy_to_cv
from procgraph import Block
import warnings

class Display(Block):
    Block.alias('cv_display')

    
    Block.config('name', default=None)
    Block.config('position', default=None)
    
    Block.input('rgb')
    
    nimages = 0 
    
    def init(self):
        name = self.config.name
        if name is None:
            name = 'display%d' % Display.nimages
        self.name = name
            
        Display.nimages += 1
        
        cv.NamedWindow(self.name, 1)
    
        if self.config.position is not None:
            x, y = self.config.position
        else:
            cols = 4
            w, h = 320, 320
            u = Display.nimages % cols
            v = int(np.floor(Display.nimages / cols))
            x = u * w
            y = v * h
        
        cv.MoveWindow(self.name, x, y)
        
    def update(self):
        rgb = self.input.rgb
        img = numpy_to_cv(rgb)
        cv.ShowImage(self.name, img)
    
    def finish(self):    
        warnings.warn('to fix')
        cv.DestroyAllWindows()
    
        
