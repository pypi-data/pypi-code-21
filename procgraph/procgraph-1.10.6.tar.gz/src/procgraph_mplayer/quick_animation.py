from procgraph import Block
from procgraph.core.registrar_other import register_model_spec
from procgraph.scripts.pgmain import pg
import numpy as np



__all__ = ['pg_quick_animation']



class GenericPlot(Block):

    Block.alias('GenericPlot')

    Block.config('plotfunc', 'Must be called with plotfunc(pylab, frame)')
    Block.config('width', 'Image dimension', default=320)
    Block.config('height', 'Image dimension', default=240)
    Block.config('transparent', 'If true, outputs a RGBA image instead of RGB.',
                 default=False)
    Block.config('tight', 'Uses "tight" option for creating png (Matplotlib>=1.1).',
                 default=False)

    Block.input('tick')
    Block.output('rgb')

    def init(self):
        from procgraph_mpl import PlotGeneric
        
        self.plot_generic = PlotGeneric(width=self.config.width,
                                        height=self.config.height,
                                        transparent=self.config.transparent,
                                        tight=self.config.tight)
        self.state.frame = 0

    def update(self):
        frame = self.state.frame

        plotfunc = self.config.plotfunc

        def f(pylab):
            return plotfunc(pylab, frame)

        self.output.rgb = self.plot_generic.get_rgb(f)

        self.state.frame += 1


register_model_spec("""
--- model GenericWrap
''' This is a simple test for :ref:`block:hdfread_many`. '''
config width
config height
config out
config plotfunc
config nframes 
config fps

import procgraph_mpl.examples

|clock interval=1.0 length=$nframes| -> clock
clock -> |GenericPlot plotfunc=$plotfunc width=$width height=$height| -> rgb

rgb -> |enc:mencoder fps=$fps file=$out |
""")

def pg_quick_animation(plotfunc, nframes, width, height, out, fps):
    config = dict(width=width, height=height, out=out,
                  nframes=nframes, plotfunc=plotfunc, fps=fps)

    config['enc.firstpass_bitrate'] = 10 * 1000 * 1000

    pg('GenericWrap', config=config)





if __name__ == '__main__':


    def bounce(pylab, frame):
        t = frame * 0.2
        t0 = t
        t1 = t + 2
        x = np.linspace(t0, t1, 1000)
        y = np.cos(x)
        pylab.plot(x, y)
        pylab.axis((t0, t1, -1.2, +1.2))

    out = 'bounce.mp4'

    pg_quick_animation(bounce, nframes=10, width=320, height=240, out=out, fps=10)



