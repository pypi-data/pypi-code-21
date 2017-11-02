import cv2
from bobo.image import Image
import janus.detection

def detect_and_crop(im, outdir):
    return im.crop(bbox=janus.detection.viola_jones(im, numDetections=1)).savein(outdir)

def align(im, outdir):
    """Transform input image"""
    pass


