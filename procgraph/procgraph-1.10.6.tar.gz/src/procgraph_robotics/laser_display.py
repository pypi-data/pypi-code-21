
from numpy import (array, cos, linspace, logical_not, maximum, minimum, nonzero, 
    sin)
from procgraph import BadInput, Block


__all__ = ['LaserDisplay']

class LaserDisplay(Block):
    ''' Produces a plot of a range-finder scan. 
    
    Example of configuration: ::
    
        display_sick.groups = [{ indices: [0,179], theta: [-1.57,+1.57],
             color: 'r', origin: [0,0,0]}]
    
    '''

    Block.alias('laser_display')

    Block.config('width', 'Width of the resulting image.', default=320)
    Block.config('height', 'Height of the resulting image.', default=320)
    Block.config('max_readings', 'Readings are clipped at this threshold (m).',
                                 default=30)
    Block.config('groups', 'How to group and draw the readings. (see example)')
    Block.config('title', 'By default it displays the signal name.'
                        ' Set the empty string to disable.', default=None)

    Block.config('transparent', 'Gives transparent RGBA rather than RGB.',
                  default=False)
    Block.input('readings', 'The laser readings (array of floats).')

    Block.output('image', 'The laser visualization (rgba).')

    def update(self):

        readings = array(self.input.readings)

        if len(readings.shape) > 1:
            msg = 'Expected flat array, got shape %s' % str(readings.shape)
            raise BadInput(msg, self, 0)

        from procgraph_mpl import pylab, pylab2rgb


        f = pylab.figure(frameon=False,
                        figsize=(self.config.width / 100.0,
                                 self.config.height / 100.0))

        # limit the readings

        bounds = array([0, 0, 0, 0])

        for group in self.config.groups:
            indices = group['indices']
            indices = range(indices[0], indices[-1] + 1)
            theta_spec = group['theta']
            origin = group.get('origin', [0, 0, 0])
            color = group.get('color', 'b.')

            max_readings = group.get('max_readings', self.config.max_readings)
            group_readings = minimum(readings[indices], max_readings)

            N = len(indices)

            theta = linspace(theta_spec[0], theta_spec[-1], N)

            assert len(theta) == len(group_readings)

            x = cos(theta + origin[2]) * group_readings + origin[0]
            y = sin(theta + origin[2]) * group_readings + origin[1]

            valid_flag = group_readings < max_readings
            valid, = nonzero(valid_flag)
            invalid, = nonzero(logical_not(valid_flag))

            pylab.plot(-y[valid], x[valid], color)
            pylab.plot(-y[invalid], x[invalid], 'r.')

            R = max_readings * 1.1
            x_R = R * cos(theta)
            y_R = R * sin(theta)
            group_bounds = array([min(x_R), max(x_R), min(y_R), max(y_R)])
            for i in [1, 3]:
                bounds[i] = maximum(bounds[i], group_bounds[i])
            for i in [0, 2]:
                bounds[i] = minimum(bounds[i], group_bounds[i])

        pylab.axis(bounds)

        if self.config.title is not None:
            if self.config.title != "":
                pylab.title(self.config.title, fontsize=10)
        else:
            # We don't have a title ---
            t = self.get_input_signals_names()[0]
            pylab.title(t, fontsize=10)

        self.output.image = pylab2rgb(transparent=self.config.transparent)
        #tight=True)

        pylab.close(f.number)



