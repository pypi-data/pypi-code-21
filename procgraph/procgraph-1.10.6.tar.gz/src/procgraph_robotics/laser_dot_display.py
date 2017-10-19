from numpy import array, linspace, sin, cos
from procgraph import Block, BadInput
import math


__all__ = ['LaserDotDisplay']


class LaserDotDisplay(Block):
    ''' Produces a plot of a range-finder scan variation (derivative). 
    
    It is a variation of :ref:`block:laser_display`; look there for 
    the documentation.
     
    '''

    Block.alias('laser_dot_display')

    Block.config('width', 'Width of the resulting image.', default=320)
    Block.config('height', 'Height of the resulting image.', default=320)

    Block.config('groups', 'How to group and draw the readings. '
                            ' (see :ref:`block:laser_display`) ')
    Block.config('title', 'By default it displays the signal name.'
                        ' Set the empty string to disable.', default=None)
    Block.config('transparent', 'Gives transparent RGBA rather than RGB.',
                  default=False)
    Block.config('R0', 'Radius of the readings circle.', default=1)
    Block.config('amp', 'Amplitude of the readings crown.', default=0.5)

    Block.input('readings_dot', 'Array of float representing array readings.')

    Block.output('image', 'A fancy visualization of the laser derivative')

    def update(self):
        y = array(self.input.readings_dot)
        from procgraph_mpl import pylab2rgb, pylab

        if max(abs(y)) > 1:
            raise BadInput('I expect an input normalized in the [-1,1] range;'
                           'min,max: %s,%s ' % (min(y), max(y)),
                           self, 'readings_dot')

        f = pylab.figure(frameon=False,
                        figsize=(self.config.width / 100.0,
                                 self.config.height / 100.0))

        R0 = self.config.R0
        amp = self.config.amp

        theta = linspace(0, 2 * math.pi, 300)
        pylab.plot(R0 * cos(theta), R0 * sin(theta), 'k--')

        for group in self.config.groups:
            indices = group['indices']
            indices = range(indices[0], indices[-1] + 1)
            theta_spec = group['theta']
            origin = group.get('origin', [0, 0, 0])
            color = group.get('color', 'b.')

            N = len(indices)

            theta = linspace(theta_spec[0], theta_spec[-1], N)

            group_y = y[indices]

            r = R0 + amp * group_y

            px = cos(theta + origin[2]) * r
            py = sin(theta + origin[2]) * r

            pylab.plot(-py, px, color)

        M = R0 + amp * 1.2
        pylab.axis([-M, M, -M, M])

        # turn off ticks labels, they don't have meaning
        pylab.setp(f.axes[0].get_xticklabels(), visible=False)
        pylab.setp(f.axes[0].get_yticklabels(), visible=False)

        if self.config.title is not None:
            if self.config.title != "":
                pylab.title(self.config.title, fontsize=10)
        else:
            # We don't have a title ---
            t = self.get_input_signals_names()[0]
            pylab.title(t, fontsize=10)

        self.output.image = pylab2rgb(transparent=self.config.transparent)

        pylab.close(f.number)


