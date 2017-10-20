import os
import subprocess
import tempfile
from csv import DictReader
import cv2
import numpy as np
from strpy.bobo.geometry import BoundingBox
from strpy.bobo.camera import Webcam
from strpy.bobo.scene import SceneDetection
from strpy.bobo.image import Image
from strpy.bobo.image import ImageDetection
from strpy.bobo.util import quietprint, remkdir, Stopwatch, isnumpy
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Circle

# FIXME: DLIB should be optional
#import dlib
#from dlib import shape_predictor, rectangle

import strpy.janus.environ

def viola_jones(img, numDetections=None):
    """Rects = [[x,y,width,height],...] format"""
    model = os.path.join(janus.environ.models(), 'haarcascades','haarcascade_frontalface_default.xml')
    if not os.path.isfile(model):
        raise ValueError('Viola-jones model file "%s" not found' % model)
    detector = cv2.CascadeClassifier(model)
    rects = detector.detectMultiScale(img, 1.2, 2, minSize=(75,75))  # from FVFITW paper
    if numDetections is None:
        return rects  # HACK for demo_violajones
    else:
        if len(rects) > 0:
            bbox = [BoundingBox(xmin=r[0], ymin=r[1], xmax=r[0]+r[2], ymax=r[1]+r[3]) for r in rects]
            bbox = sorted(bbox, key=(lambda bb: bb.area()), reverse=True)  # biggest to smallest
            if numDetections == 1:
                return bbox[0]
            else:
                return bbox[0:np.minimum(numDetections, len(bbox))]
        else:
            return None

def getDlibWebcamFaceDetections(do_landmarks=True, category='Webcam', subjectid=None, framerate=True, numDetections=1, resize=0.5):
    """Performs face detection on a series of images captured with a webcam"""
    images = []
    landmarks = []
    detector = DlibFaceDetector()

    for img in Webcam(framerate=framerate, resize=resize, grey=True):
        im = ImageDetection(category=category)
        im.data = img
        bboxes, landmarks = detector(im, do_landmarks=do_landmarks)
        if len(bboxes) > 0:
            bbox = bboxes[0]
            lm  = landmarks[0]
            if bboxes[0].invalid():
                continue

            im.setattribute('TEMPLATE_ID', category)
            im.setattribute('SIGHTING_ID', 0)
            im.setattribute('SUBJECT_ID', subjectid if subjectid is not None else category)
            im.setattribute('FACE_X', str(bbox.xmin))
            im.setattribute('FACE_Y', str(bbox.ymin))
            im.setattribute('FACE_WIDTH',  str(bbox.xmax - bbox.xmin))
            im.setattribute('FACE_HEIGHT', str(bbox.ymax - bbox.ymin))

            if lm is not None:
                # Ensure landmarks are included inside detection box
                bbox.xmin = min(bbox.xmin, min(lm[:,0]))
                bbox.ymin = min(bbox.ymin, min(lm[:,1]))
                bbox.xmax = max(bbox.xmax, max(lm[:,0]))
                bbox.ymax = max(bbox.ymax, max(lm[:,1]))
                # Calculate remaining Janus landmark alignment locations
                im.setattribute('RIGHT_EYE_X', str(np.mean(lm[42:48,0])))
                im.setattribute('RIGHT_EYE_Y', str(np.mean(lm[42:48,1])))
                im.setattribute('LEFT_EYE_X',  str(np.mean(lm[36:42,0])))
                im.setattribute('LEFT_EYE_Y',  str(np.mean(lm[36:42,1])))
                im.setattribute('NOSE_BASE_X',  str(np.mean(lm[36:42,0]))) # Approx center of landmark
                im.setattribute('NOSE_BASE_Y',  str(np.max(lm[30:35,1])))  # Approx bottom of landmark

            im = im.boundingbox(bbox=bbox)

            im.data = img
            images.append(im)
            landmarks.append(lm)
        if len(images) == numDetections:
            return images, landmarks

        
class DlibFaceDetector(object):
    """Peforms dlib face detection and landmark alignments on an image and provides a method to show landmarks"""
    def __init__(self):
        model = os.path.join(janus.environ.models(), 'dlib', 'combined_face_detector.svm')
        self.detector = DlibObjectDetector(model)
        model = os.path.join(janus.environ.models(), 'dlib', 'sp-aflw-depth6-cascade20_nu0.1-frac1.00-splits60.dat')
        #model = os.path.join(janus.environ.models(), 'dlib', 'shape_predictor_68_face_landmarks.dat')
        self.aligner = DlibShapePredictor(model)

    def detect(self, im, category='Face', num_detections=None):
        """Run face detection on image object, return scenedetection object"""
        return self.detector.detect(im, category=category)

    def align(self, imdet, aflw_order=True):
        """Run object detection on image buffer, return scenedetection object"""
        return self.aligner(imdet.crop(), aflw_order=aflw_order)[0]
                        
    def show_landmarks(self, im, landmarks, frmt='b-', imshowargs={}):
        """Plots dlib landmark alignments on a bobo.image.Image or subclass"""

        lm = landmarks

        f_line =  (lambda lm,b,e: LineCollection([[lm[k] for k in (b, e)]]))
        f_lines = (lambda lm,b,e: LineCollection([[(x,y) for (x,y) in lm[b:e]]]))

        im.show(**imshowargs)
        if lm is not None:
            plt.pause(1E-4)
            plt.hold(True)

            ax = plt.gca()

            ax.add_collection(f_lines(lm, 0, 17)) # Jawline
            ax.add_collection(f_lines(lm, 17, 22)) # Left eyebrow
            ax.add_collection(f_lines(lm, 22, 27)) # Right eyebrow
            ax.add_collection(f_lines(lm, 27, 31)) # Nose bridge
            ax.add_collection(f_lines(lm, 30, 36)) # Nose base
            ax.add_collection(f_line(lm, 30, 35)) # Nose base close
            ax.add_collection(f_lines(lm, 36, 42)) # Left eye
            ax.add_collection(f_line(lm, 36, 41)) # Left eye close
            ax.add_collection(f_lines(lm, 42, 48)) # Right eye
            ax.add_collection(f_line(lm, 42, 47)) # Right eye close
            ax.add_collection(f_lines(lm, 48, 60)) # Lip outline
            ax.add_collection(f_line(lm, 48, 59)) # Lip outline close
            ax.add_collection(f_lines(lm, 60, 68)) # Lip inline
            ax.add_collection(f_line(lm, 60, 67)) # Lip inline close

            plt.draw()


class DlibObjectDetector(object):
    def __init__(self, model=None, upsample_num_times=0):
        model = model if model is not None else os.path.join(janus.environ.models(), 'dlib', 'combined_face_detector.svm')
        self.detector = dlib.fhog_object_detector(model)
        self.upsample_num_times = int(upsample_num_times)
        quietprint('[janus.detection]: Initialized dlib object detector model %s, upsample=%d' % (model, self.upsample_num_times), 2)

    def __call__(self, im, nonmax_threshold=None, adjust_threshold=0.0):
        imset = []
        data = im.clone().rgb().data
        
        if adjust_threshold != 0.0:
            rects, scores, ind = self.detector.run(data, self.upsample_num_times, adjust_threshold=adjust_threshold)  # newer python API
        else:
            rects, scores, ind = self.detector.run(data, self.upsample_num_times)  # older python API support
        detections = zip(rects, scores, ind)

        sorted_detections = sorted(detections, key=lambda x: x[1], reverse=True)
        sorted_results = [(BoundingBox(xmin=d[0].left(), ymin=d[0].top(), xmax=d[0].right(), ymax=d[0].bottom()), d[1], d[2]) for d in sorted_detections]

        final_results = []
        for (bbox, score, _) in sorted_results:
            if nonmax_threshold is not None:
               is_overlap = [bb.overlap(bbox) > nonmax_threshold for bb in final_results]
               if any(is_overlap):
                   continue
            bbox.score = score
            final_results.append(bbox)
        return final_results

    def detect(self, img, nonmax_threshold=None, adjust_threshold=0.0, category='Face'):
        """Run object detection on image buffer or image object, return scenedetection object"""
        im = Image().array(img) if isnumpy(img) else img  # image object or numpy array
        bboxes = self.__call__(im, nonmax_threshold, adjust_threshold)
        return SceneDetection(filename=im.filename(), url=im.url()).objects([ImageDetection(filename=im.filename(), url=im.url(), bbox=bb, category=category).array(im.load()) for bb in bboxes]).array(im.load()).map(lambda x: x.setfilename(im.filename()).array(im.load()))    
    
class DlibShapePredictor(object):
    """Peforms dlib face detection and landmark alignments on an image and provides a method to show landmarks"""
    def __init__(self, model=None):
        model = model if model is not None else os.path.join(janus.environ.models(), 'dlib', 'sp-aflw-depth6-cascade20_nu0.1-frac1.00-splits60.dat')
        self.predictor = shape_predictor(model)

    def __call__(self, im, bboxes=None, aflw_order=True):
        """Performs dlib landmark alignment on a bobo.image.Image or subclass"""
        data = im.clone().rgb().data

        bboxes = bboxes if bboxes is not None else [im.boundingbox()]
        rects = [rectangle(left=int(b.xmin), top=int(b.ymin), right=int(b.xmax), bottom=int(b.ymax)) for b in bboxes]
        landmarks = []

        for (k, rect) in enumerate(rects):
            predictions = self.predictor(data, rect)
            landmarks.append(np.array([ (p.x,p.y) for p in predictions.parts() ], dtype=np.float32))
                # [plt.text(l[0], l[1], str(k)) for k, l in enumerate(lm)]

        if aflw_order and len(landmarks) > 0 and len(landmarks[0]) == 21:
            # Default Dlib landmark order (right/left is subject's perspective)
            # RightbrowRight=0, Rightbrowmiddle=1, Lefteyemiddle=2, Lefteyeoutside=3
            # Rightear/jaw=4, Noseright=5, Nosemiddle=6, Noseleft=7, Leftear/jaw=8,
            # Mouthright=9, Mouthmiddle=10, Mouthleft=11, Rightbrowinside=12, Chincenter=13,
            # Leftbrowinside=14, Leftbrowmiddle=15, Leftbrowoutside=16, Righteyeoutside=17,
            # Righteyemiddle=18, Righteyeinside=19, Lefteyeinside=20,
            idxs = [16, 15, 14, 12, 1, 0, 3, 2, 20, 19, 18, 17, 8, 7, 6, 5, 4, 11, 10, 9, 13]
            # Rearrange to Janus viset.aflw schema order
            # LeftBrowLeftCorner, LeftBrowCenter, LeftBrowRightCorner,
            # RightBrowLeftCorner, RightBrowCenter, RightBrowRightCorner, 
            # LeftEyeLeftCorner, LeftEyeCenter, LeftEyeRightCorner, 
            # RightEyeLeftCorner, RightEyeCenter, RightEyeRightCorner,
            # LeftEar, NoseLeft, NoseCenter, NoseRight, RightEar,
            # MouthLeftCorner, MouthCenter, MouthRightCorner, ChinCenter
            landmarks = [lm[idxs,:] for lm in landmarks]

        return landmarks

    def show_landmarks(self, im, landmarks, frmt='b-', imshowargs={}):
        """Plots dlib landmark alignments on a bobo.image.Image or subclass"""

        lm = landmarks

        imshowargs['flip'] = False
        im.show(**imshowargs)    
        if lm is not None:
            #plt.pause(1E-4)
            plt.hold(True)

            ax = plt.gca()

            if  lm.shape[0] == 68:
                f_line =  (lambda lm,b,e: LineCollection([[lm[k] for k in (b, e)]]))
                f_lines = (lambda lm,b,e: LineCollection([[(x,y) for (x,y) in lm[b:e]]]))
                ax.add_collection(f_lines(lm, 0, 17)) # Jawline
                ax.add_collection(f_lines(lm, 17, 22)) # Left brow
                ax.add_collection(f_lines(lm, 22, 27)) # Right brow
                ax.add_collection(f_lines(lm, 27, 31)) # Nose bridge
                ax.add_collection(f_lines(lm, 30, 36)) # Nose base
                ax.add_collection(f_line(lm, 30, 35)) # Nose base close
                ax.add_collection(f_lines(lm, 36, 42)) # Left eye
                ax.add_collection(f_line(lm, 36, 41)) # Left eye close
                ax.add_collection(f_lines(lm, 42, 48)) # Right eye
                ax.add_collection(f_line(lm, 42, 47)) # Right eye close
                ax.add_collection(f_lines(lm, 48, 60)) # Lip outline
                ax.add_collection(f_line(lm, 48, 59)) # Lip outline close
                ax.add_collection(f_lines(lm, 60, 68)) # Lip inline
                ax.add_collection(f_line(lm, 60, 67)) # Lip inline close
            elif lm.shape[0] == 21:
                radius = 2.0
                patches = [Circle(l, radius) for l in lm]
                p = PatchCollection(patches)
                ax.add_collection(p)
                # [plt.text(l[0], l[1], str(k)) for k, l in enumerate(lm)]
            else:
                raise ValueError, 'Unsupported numer of landmarks: %d' % lm.shape[0]

            plt.draw()


class HeadhunterDetector(object):
    def __init__(self, model=None):
        models = janus.environ.models()
        self._model = model if model is not None else os.path.join(models, 'headhunter', 'face_detection', 'headhunter_baseline.proto.bin')

    def __call__(self, im):
        rundir = tempfile.mkdtemp()
        quietprint('[janus.detection.headhunter]: Writing to %s'%rundir, 2)

        imdir = os.path.join(rundir, 'img')
        remkdir(imdir)

        conf = self._getConfig(rundir, imdir)
        conffile = os.path.join(rundir, 'headhunter.config.ini')
        self._writeConfig(conf, filename=conffile)

        imfile = os.path.join(imdir, os.path.split(im.filename())[1])
        im.saveas(imfile)

        res = self._headhunterDetect(rundir, conffile)

        detsfile = os.path.join(rundir, 'detections.csv')

        bboxes = self._getDetections(detsfile)
        imset = [im.clone().boundingbox(bbox=bb) for bb in bboxes]
        return imset


    def _getConfig(self, rundir, imdir):
        return [ ('None', {
                    'save_detections': 'true ',
                    'process_folder': imdir, # directory with input images
                    'additional_border': '200', # border added the input images, in pixels
                    'recordings_path': rundir, # outputdir
                    }, ),
                ('objects_detector', {
                    'method': 'gpu_channels',

                    'model': self._model,
                    # lower threshold increases recall
                    'score_threshold': '0', # default threshold
                    #score_threshold = 0.05 # nice for visualization

                    # strides smaller than 1 ensures that will use 1 pixel at all scales
                    'x_stride': '0.00001 ',
                    'y_stride': '0.00001 ',

                    'non_maximal_suppression_method': 'greedy',
                    'minimal_overlap_threshold': '0.3',

                    # min_scale = 0.15
                    # max_scale = 18
                    'min_scale': '0.325',
                    'max_scale': '6',

                    # Scales linearly increase processing time
                    # num_scales = 55
                    'num_scales': '80',
                    # num_scales = 100

                    # ratio is defined as width/height
                    'min_ratio': '1',
                    'max_ratio': '1',
                    'num_ratios': '1 ',
                    },
                    ),
                ('preprocess', {
                    'unbayer': 'false',
                    'undistort': 'false',
                    'rectify': 'true',
                    'smooth': 'false',
                    '#residual': 'true',
                    'residual': 'false',
                    'specular': 'false',
                    },
                    ),
                ]

    def _writeConfig(self, conflist, filename):
        with open(filename, 'w') as cf:
            for sk,sv in conflist:
                if sk != 'None':
                    cf.write('[%s]\n'%sk)
                for k,v in sv.iteritems():
                    cf.write('%s = %s\n'%(k,v))

    def _headhunterDetect(self, rundir, conffile):
        # Platform should have placed objects_detect on the path
        command = ['objects_detection', '--gui.disable', 'true', '-c', conffile]
        print 'command: %r' % ' '.join(command)
        try:
            cmd_output = subprocess.check_output(command, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError, e:
            print('Warning: ' + command[0] + ' returned ' + str(e.returncode))
            print(e.output)
            print(' '.join(command))
            return
        return cmd_output

    def _getDetections(self, csvfile):
        schema = ['FILE', 'FACE_X', 'FACE_Y', 'WIDTH', 'HEIGHT', 'SCORE']
        bboxes = []
        with open(csvfile, 'r') as f:
            next(f) # skip header
            reader = DictReader(f, fieldnames=schema)
            for row in reader:
                xmin = float(row['FACE_X'])
                ymin = float(row['FACE_Y'])
                xmax = xmin + float(row['WIDTH'])
                ymax = xmin + float(row['HEIGHT'])
                score = float(row['SCORE'])
                bbox = BoundingBox(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax, score=score)
                bboxes.append(bbox)
        return bboxes

def assign_detections(bb_det, bb_true, percent_overlap=0.5):
    """Assigns object detections to truth using Intesection Area / Union Area overlap metric"""
    bb_det.sort(key=lambda bb: bb.score, reverse=True)  # sort inplace, descending by score
    is_assigned = [False]*len(bb_true)
    y_true = []
    y_pred = []
    matches = []
    nonmatches = []
    for bk, bb in enumerate(bb_det):
        overlap = [bb.overlap(x) for x in bb_true]
        assert len(overlap) == len(bb_true)
        is_overlapped_label = [(x >= percent_overlap) and (bb.label == gt.label) for (x,gt) in zip(overlap, bb_true)]
        max_overlap = [k for (k,v) in enumerate(overlap) if (v == max(overlap) and is_overlapped_label[k])]
        if any(is_overlapped_label):
            if not is_assigned[max_overlap[0]]:
                idx = max_overlap[0]
                y_true.append(1.0)
                y_pred.append(bb.score) # true detection
                is_assigned[idx] = True
                matches.append((bb_true[idx], bb))
            else:
                nonmatches.append(bb)
                #y.append( (0.0, -np.inf) )  # non-maximum suppression
                pass  # ignore multiple detection
        else:
            nonmatches.append(bb)
            y_true.append(0.0)
            y_pred.append(bb.score) # true detection

    return (y_true, y_pred, bb_det, matches, nonmatches)
