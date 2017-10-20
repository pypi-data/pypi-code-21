import numpy
from bob.ip.facedetect import BoundingBox
import dlib


def bob_to_dlib_image_convertion(bob_image, change_color=True):
    """
    Bob stores color images as (C, W, H), where C is channels, W is the width and H is height; AND the order of the
    colors are R,G,B.
    On the other hand, Dlib do (W, H, C) AND the order of the colors are the same as OpenCV (B, G, R)
    """

    if len(bob_image.shape) == 2:
        return bob_image

    dlib_image = numpy.zeros(shape=(bob_image.shape[1], bob_image.shape[2], bob_image.shape[0]), dtype="uint8")
    if change_color:
        dlib_image[:, :, 0] = bob_image[2, :, :]  # B
        dlib_image[:, :, 1] = bob_image[1, :, :]  # G
        dlib_image[:, :, 2] = bob_image[0, :, :]  # R
    else:
        dlib_image[:, :, 0] = bob_image[0, :, :]  # B
        dlib_image[:, :, 1] = bob_image[1, :, :]  # G
        dlib_image[:, :, 2] = bob_image[2, :, :]  # R

    return dlib_image


def dlib_to_bob_image_convertion(dlib_image, change_color=True):
    """
    Bob stores color images as (C, W, H), where C is channels, W is the width and H is height; AND the order of the
    colors are R,G,B.
    On the other hand, Dlib do (W, H, C) AND the order of the colors are the same as OpenCV (B, G, R)
    """

    if len(dlib_image.shape) == 2:
        return dlib_image

    bob_image = numpy.zeros(shape=(dlib_image.shape[2], dlib_image.shape[0], dlib_image.shape[1]), dtype="uint8")
    if change_color:
        bob_image[0, :, :] = dlib_image[:, :, 2] # R
        bob_image[1, :, :] = dlib_image[:, :, 1] # G
        bob_image[2, :, :] = dlib_image[:, :, 0] # B
    else:
        bob_image[0, :, :] = dlib_image[:, :, 0] # R
        bob_image[1, :, :] = dlib_image[:, :, 1] # G
        bob_image[2, :, :] = dlib_image[:, :, 2] # B

    return bob_image


def bounding_box_2_rectangle(bb):
    """
    Converrs a bob.ip.facedetect.BoundingBox to dlib.rectangle
    """

    assert isinstance(bb, BoundingBox)
    return dlib.rectangle(bb.topleft[1], bb.topleft[0],
                          bb.bottomright[1], bb.bottomright[0])




# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
