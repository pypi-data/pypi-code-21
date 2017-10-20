import os
from bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv
import janus.environ
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
from bobo.geometry import BoundingBox
from itertools import product, groupby
from collections import OrderedDict
from glob import glob


def uniq_strface_id(im):
    filename_parts = im.filename().split('/')
    base_folder = filename_parts[-2]
    ids = base_folder.split('_')
    assert(ids[1] == im.category())
    capture_id = ids[-1]
    return '%s_%s_%s' % (im.category(), capture_id, os.path.basename(im.filename()).split('.')[0])


class STRface(object):
    def __init__(self, datadir=None):
        self.datadir = os.path.join(janus.environ.data(), 'strface') if datadir is None else os.path.join(datadir, 'strface')
    def _parse_csvs(self,csvfile,header=True):
        csv = readcsv(csvfile)
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT','RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_X','NOSE_Y','FRAME_NUM','EYES_VISIBLE','NOSE_MOUTH_VISIBLE','FOREHEAD_VISIBLE','FACIAL_HAIR','AGE','INDOOR_OUTDOOR','SKINTONE','GENDER','YAW','CS2']
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category = x[1],
                                xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                                ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                                xmax = float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                                ymax = float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                                attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]
        return imdet

    def all_templates(self):
        f_parse = self._parse_csvs;
        imdet = []
        for csvfile in sorted(glob(os.path.join(self.datadir,'meta','*.csv'))):
            imdet += f_parse(csvfile)
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['SIGHTING_ID'], im.attributes['TEMPLATE_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def all_sightings(self):
        D = {}
        templates = self.all_templates()
        for t in templates:
            for v in t:
                for im in v:
                    key = uniq_strface_id(im)
                    if key not in D:
                        D[key] = im
                    elif D[key].boundingbox().overlap(im.boundingbox()) < 0.99:
                        print D[key], ' versus ', im
        return D.values()
