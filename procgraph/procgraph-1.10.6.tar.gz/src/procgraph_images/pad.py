
from .border import image_border


__all__ = ['image_pad']


def image_pad(pixel_data, expected_shape, bgcolor=[1, 1, 1]):
    """ Pads horizontally and vertically an image so that it is of the 
        given shape. """
    shape = pixel_data.shape[0:2]
    if (shape[0] > expected_shape[0]) or (shape[1] > expected_shape[1]):
        msg = ('Image is bigger (%s) than the expected shape (%s) ' %
               (shape, expected_shape))
        raise ValueError(msg)

    extra_hor = expected_shape[1] - shape[1]
    left = int(extra_hor / 2)
    right = extra_hor - left

    extra_ver = expected_shape[0] - shape[0]
    top = int(extra_ver / 2)
    bottom = extra_ver - top

    new_image = image_border(rgb=pixel_data, color=bgcolor,
                 left=left, right=right, top=top, bottom=bottom)

    # assert_equal(new_image.shape[0:2], expected_shape)

    return new_image


