#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>
# @date: Fri 17 Jun 2016 10:41:36 CEST

import numpy
import os
import bob.core
logger = bob.core.log.setup("bob.ip.dlib")
bob.core.log.set_verbosity_level(logger, 3)
import dlib
from .utils import bounding_box_2_rectangle, bob_to_dlib_image_convertion
from .FaceDetector import FaceDetector


class DlibLandmarkExtraction(object):
    """

    """

    def __init__(self, model=None):
        """
        """

        default_model = os.path.join(DlibLandmarkExtraction.get_dlib_model_path(), "shape_predictor_68_face_landmarks.dat")
        if model is None:
            self.model = default_model
            if not os.path.exists(self.model):
                DlibLandmarkExtraction.download_dlib_model()
        else:
            self.model = model
            if not os.path.exists(self.model):
                raise ValueError("Model not found: {0}".format(self.model))

        self.face_detector = FaceDetector()
        self.predictor = dlib.shape_predictor(self.model)

    def __call__(self, image, bb=None, xy_output=False):

        # Detecting the face if the bounding box is not passed
        if bb is None:
            bb = bounding_box_2_rectangle(self.face_detector.detect_single_face(image)[0])

            if bb is None:
                return None
        else:
            bb = bounding_box_2_rectangle(bb)

        if bb is None:
            raise ValueError("Face not found in the image.")

        points = self.predictor(bob_to_dlib_image_convertion(image), bb)
        if xy_output:
            return list(map(lambda p: (p.x, p.y), points.parts()))
        else:
            return list(map(lambda p: (p.y, p.x), points.parts()))

    @staticmethod
    def get_dlib_model_path():
        import pkg_resources
        return pkg_resources.resource_filename(__name__, 'data')

    @staticmethod
    def download_dlib_model():
        """
        Download and extract the dlib model face detection model from
        """
        import sys
        import os
        import bz2
        logger.info("Downloading the shape_predictor_68_face_landmarks.dat Face model from  database from "
                    "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 ...")

        tmp_file = os.path.join(DlibLandmarkExtraction.get_dlib_model_path(), "shape_predictor_68_face_landmarks.dat.bz2")
        url = 'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2'
        #url = 'http://beatubulatest.lab.idiap.ch/software/bob/packages/vgg_face_caffe.tar.gz'

        if sys.version_info[0] < 3:
            # python2 technique for downloading a file
            from urllib2 import urlopen
            with open(tmp_file, 'wb') as out_file:
                response = urlopen(url)
                out_file.write(response.read())

        else:
            # python3 technique for downloading a file
            from urllib.request import urlopen
            from shutil import copyfileobj
            with urlopen(url) as response:
                with open(tmp_file, 'wb') as out_file:
                    copyfileobj(response, out_file)
        # Unzip
        logger.info("Unziping in {0}".format(DlibLandmarkExtraction.get_dlib_model_path()))
        #t = tarfile.open(fileobj=open(tmp_file), mode='r:gz')
        t = bz2.BZ2File(tmp_file)
        open(os.path.join(DlibLandmarkExtraction.get_dlib_model_path(),'shape_predictor_68_face_landmarks.dat'), 'wb').write(t.read())
        t.close()
