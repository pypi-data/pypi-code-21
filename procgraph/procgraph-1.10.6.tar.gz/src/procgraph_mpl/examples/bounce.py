import numpy as np
from procgraph import Block
from procgraph_mpl.plot_generic import PlotGeneric


__all__ = [
    'Bounce',
]

class Bounce(Block):
    
    Block.alias('bounce')

    Block.config('width', 'Image dimension', default=320)
    Block.config('height', 'Image dimension', default=240)
    Block.config('transparent', 'If true, outputs a RGBA image instead of RGB.',
                 default=False)
    Block.config('tight', 'Uses "tight" option for creating png (Matplotlib>=1.1).',
                 default=False)
    
    Block.input('tick')
    Block.output('rgb')
    
    
    def init(self):
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.height,
                                        transparent=self.config.transparent,
                                        tight=self.config.tight)

    def update(self):
        self.output.rgb = self.plot_generic.get_rgb(self.plot)
        
        
    def plot(self, pylab):
        t = self.get_input_timestamp(0)
        t0 = t
        t1 = t + 2
        x = np.linspace(t0, t1, 1000)
        y = np.cos(x)
        pylab.plot(x, y)
        pylab.axis((t0, t1, -1.2, +1.2))
        
