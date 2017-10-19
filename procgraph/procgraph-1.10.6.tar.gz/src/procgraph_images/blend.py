from . import np

from procgraph import Block


# TODO: move somewhere else?
def to_rgb(rgb):
    ''' Remove the alpha layer if present. '''
    if rgb.shape[2] == 3:
        return rgb

    return rgb[:, :, 0:3]


# TODO: move somewhere else?
def to_rgba(rgb):
    ''' Adds a opaque alpha if not present. '''
    if rgb.shape[2] == 4:
        rgba = rgb.copy()
        return rgba

    rgba = np.ndarray((rgb.shape[0], rgb.shape[1], 4), dtype='uint8')
    rgba[:, :, 0] = rgb[:, :, 0]
    rgba[:, :, 1] = rgb[:, :, 1]
    rgba[:, :, 2] = rgb[:, :, 2]
    rgba[:, :, 3] = 255

    return rgba


def blend(a, b):
    ''' Blends two RGB or RGBA images. '''
    if (a.shape[0] != b.shape[0]) or  (a.shape[1] != b.shape[1]):
        raise ValueError('Incompatible shapes: %s and %s.' %
                          (a.shape, b.shape))

    # Add alpha component if missing
    a = to_rgba(a)
    b = to_rgba(b)

    #alpha_a = a[:, :, 3].astype('float32')
    alpha_b = b[:, :, 3].astype('float32')

    #weight_a = alpha_a / (alpha_a + alpha_b)
    weight_b = alpha_b / 255.0
    weight_a = -weight_b + 1

    result = np.ndarray(shape=(a.shape[0], a.shape[1], 4), dtype='uint8')

    for i in [0, 1, 2]:
        result[:, :, i] = a[:, :, i] * weight_a + b[:, :, i] * weight_b

    result[:, :, 3] = 255

    return result.astype('uint8')


class Blend(Block):
    '''
        Blend two or more images.
        
        RGB images are interpreted as having full alpha (opaque). 
        All images must have the same width and height.
        
    '''
    Block.alias('blend')

    Block.input_is_variable('images to blend', min=2)

    Block.output('rgb', 'The output is a RGB image (no alpha)')

    def update(self):
        # TODO: check images
        result = None
        for signal in self.get_input_signals_names():
            image = self.get_input(signal)
            if result is None:
                result = image
                continue

            result = blend(result, image)

        self.output.rgb = to_rgb(result)



