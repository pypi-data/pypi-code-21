import warnings

from numpy.ma.testutils import assert_equal



__all__ = ['PlotGeneric']


class PlotGeneric(object):
    ''' 
        Produces images using matplotlib. Good for custom animation.
    '''
    def __init__(self, width, height, transparent, tight, keep=False):
        self.width = width
        self.height = height
        self.transparent = transparent
        self.tight = tight
        self.keep = keep

        self.figure = None
        self.warned = False        

    def init_figure(self):
        # TODO: remove from here
        from . import pylab
        
        pylab.rc('xtick', labelsize=8)
        pylab.rc('ytick', labelsize=8)

        ''' Creates figure object and axes '''
        self.figure = pylab.figure(frameon=False,
                                   figsize=(self.width / 100.0,
                                            self.height / 100.0))
        self.axes = pylab.axes()
        self.figure.add_axes(self.axes)

        pylab.draw_if_interactive = lambda: None

        pylab.figure(self.figure.number)

    def get_rgb(self, function):
        """ function(pylab) """
        if self.figure is None:
            self.init_figure()
            
        from . import pylab, pylab2rgb
        
        pylab.figure(self.figure.number)

        function(pylab)
        
        # http://matplotlib.sourceforge.net/users/tight_layout_guide.html
        try:
            pylab.tight_layout()
        except Exception as e:
            msg = ('Could not call tight_layout(); available only on '
                   'Matplotlib >=1.1 (%s)' % e)
            if not self.warned:
                warnings.warn(msg)
                self.warned = True

        # There is a bug that makes the image smaller than desired
        # if tight is True 
        pixel_data = pylab2rgb(transparent=self.transparent, tight=self.tight)

        from procgraph_images import image_pad # need here otherwise circular
    
        # So we check and compensate
        shape = pixel_data.shape[0:2]
        shape_expected = (self.height, self.width)
        if shape != shape_expected:
            msg = ('pylab2rgb() returned size %s instead of %s.' % 
                (shape, shape_expected))
            msg += ' I will pad the image with white.'
            warnings.warn(msg)
            pixel_data = image_pad(pixel_data, shape_expected,
                                   bgcolor=[1, 1, 1])
            assert_equal(pixel_data.shape[0:2], shape_expected)

        if not self.keep:
            pylab.close(self.figure.number)
            self.figure = None
        else:
            pass
#             pylab.cla()
#             pylab.clf()
            
        return pixel_data


