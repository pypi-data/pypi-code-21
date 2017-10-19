from . import np

from procgraph import Block
from procgraph.block_utils  import assert_rgb_image


class Compose(Block):
    '''
    Compose several images in the same canvas.
    You should probably use :ref:`block:grid` in many situations.
    
    Example configuration: ::
    
        compose.positions = {y: [0,0], ys: [320,20]}
        
    '''

    Block.alias('compose')

    Block.config('width', 'Dimension in pixels.')
    Block.config('height', 'Dimension in pixels.')
    Block.config('positions',
             'A structure giving the position of each signal in the canvas.')

    Block.input_is_variable('Images to compose.')

    Block.output('canvas', 'RGB image')

    def update(self):
        width = self.get_config('width')
        height = self.get_config('height')

        canvas = np.zeros((height, width, 3), dtype='uint8')

        positions = self.get_config('positions')

        if not isinstance(positions, dict):
            raise Exception('I expected a dict, not "%s"' % positions)

        for signal, position in positions.items():
            if not self.is_valid_input_name(signal):
                raise Exception('Unknown input "%s" in %s.' % (signal, self))
            rgb = self.get_input(signal)
            # TODO check
            if rgb is not None:
                assert_rgb_image(rgb, 'input %s to compose block' % signal)

                place_at(canvas, rgb, position[0], position[1])
                #print "Writing image %s" % signal
            else:
                print "Ignoring image %s because not ready.\n" % signal

        self.set_output(0, canvas)



def place_at(canvas, image, xpix, ypix):
    # print canvas.shape, image.shape
    xsize = min(canvas.shape[1] - xpix, image.shape[1])
    ysize = min(canvas.shape[0] - ypix, image.shape[0])
    if len(image.shape) == 2:
        image = image.reshape((image.shape[0], image.shape[1], 1))
    canvas[ypix:(ypix + ysize), xpix:(xpix + xsize), 0:3] = \
        image[0:ysize, 0:xsize, :]


