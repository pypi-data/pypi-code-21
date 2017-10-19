from procgraph.core.registrar_other import simple_block
# import numpy as np
# from . import cv as cv2
# from procgraph_cv.conversions import numpy_to_cv
# from reprep.graphics.zoom import rgb_zoom
from contracts import contract
from procgraph_images.filters import torgb

@simple_block
@contract(gray='array[HxW]')
def simple_detector_demo(gray):
    import cv2

#     print gray[10, :]


    gray = torgb(gray)

#     print gray[10, :, 0]
#     img = numpy_to_cv(rgb)

    # Initiate STAR detector
#     star = cv2.FeatureDetector_create("STAR")  # @UndefinedVariable

    # Initiate BRIEF extractor

#     brief = cv2.DescriptorExtractor_create("BRIEF")  # @UndefinedVariable

    sift = cv2.SIFT()

    # find the keypoints with STAR
#     gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

    kps = sift.detect(gray)  # , None, useProvidedKeypoints=False)

#     print kps
    res = cv2.drawKeypoints(gray, kps)
#     print res[10, :, 0]
#
#     for kp in kps:
#         x = kp.x
#         y = kp.y
#         img[y, x, 0] = 255

#     kp = star.detect(imgg, None)

    # compute the descriptors with BRIEF
#     kp, des = brief.compute(rgb, kp)

#     print kp
#     print brief.getInt('bytes')
#     print des


    return res


# Initiate STAR detector


@simple_block
@contract(rgb='array[HxWx3]', returns='array[HxWx3]')
def detect_and_plot_star(rgb, nfeatures=50):
    import cv2
    detector = cv2.FeatureDetector_create("STAR")

    r = detector.detect(rgb)  # , None, useProvidedKeypoints=False)
    print('Number of STAR kps: %s' % len(r))
    keypoints = r

    res = draw_keypoints(rgb, keypoints)
    return res



@simple_block
@contract(rgb='array[HxWx3]', returns='array[HxWx3]')
def detect_and_plot_dense(rgb, nfeatures=50):
    import cv2
    detector = cv2.FeatureDetector_create("Dense")

    r = detector.detect(rgb)  # , None, useProvidedKeypoints=False)
    print('Number of dense kps: %s' % len(r))
    keypoints = r

    res = draw_keypoints(rgb, keypoints)
    return res


@simple_block
@contract(rgb='array[HxWx3]', returns='array[HxWx3]')
def detect_and_plot_fast(rgb, nfeatures=50):
    import cv2
    detector = cv2.FeatureDetector_create("FAST")

    r = detector.detect(rgb)  # , None, useProvidedKeypoints=False)
    print('Number of FAST kps: %s' % len(r))
    keypoints = r

    res = draw_keypoints(rgb, keypoints)
    return res




def draw_keypoints(rgb, keypoints):
    import cv2
    try:
        raise ValueError()
        res = cv2.drawKeypoints(rgb, keypoints)
    except:
        res = rgb.copy()
        for kp in keypoints:
            x, y = kp.pt
            res[y, x, :] = 255

    return res


@simple_block
@contract(rgb='array[HxWx3]', returns='array[HxWx3]')
def detect_and_plot_orb(rgb, nfeatures=50):
    import cv2
#     gray = torgb(gray)

    detector = cv2.ORB(nfeatures=nfeatures, edgeThreshold=0)  # @UndefinedVariable
    r = detector.detect(rgb)  # , None, useProvidedKeypoints=False)
    print('Number of ORB kps: %s' % len(r))
    keypoints = r

#     print kps
    res = cv2.drawKeypoints(rgb, keypoints)
#     print res[10, :, 0]
#
#     for kp in kps:
#         x = kp.x
#         y = kp.y
#         img[y, x, 0] = 255

#     kp = star.detect(imgg, None)

    # compute the descriptors with BRIEF
#     kp, des = brief.compute(rgb, kp)

#     print kp
#     print brief.getInt('bytes')
#     print des


    return res
