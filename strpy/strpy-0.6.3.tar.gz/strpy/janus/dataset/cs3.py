import os
import janus.environ
from bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
from bobo.geometry import BoundingBox
from itertools import product, groupby
from collections import OrderedDict


def uniq_cs3_id(im):
    return '%s_%s' % (im.attributes['SIGHTING_ID'], os.path.basename(im.filename()).split('.')[0])


class CS3(object):
    def __init__(self, datadir=None, v2=True):
        self.v2 = v2
        d = 'CS3_2.0' if self.v2 else 'CS3'
        self.datadir = os.path.join(janus.environ.data(), 'Janus_CS3', d) if datadir is None else os.path.join(datadir, 'Janus_CS3', d)
        if not os.path.isdir(self.datadir):
            raise ValueError('Download Janus CS3 dataset manually to "%s" ' % self.datadir)

    def __repr__(self):
        return str('<janus.dataset.cs3: %s>' % self.datadir)

    def _parse_csv_1(self, csvfile, header=True):
        """ v2.0: detection and clustering protocols """
        schema = ['FILENAME']
        csv = readcsv(csvfile)
        return [ImageDetection(filename=os.path.join(self.datadir, x[0]), attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]

    def _parse_csv_12(self, csvfile, header=True):
        """ v2.0: clustering protocols """
        schema = ['TEMPLATE_ID', 'FILENAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_X', 'NOSE_Y']
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[1]), category='%04d' % int(x[0]),
                             xmin=float(x[2]) if len(x[2]) > 0 else float('nan'),
                             ymin=float(x[3]) if len(x[3]) > 0 else float('nan'),
                             xmax = float(x[2])+float(x[4]) if ((len(x[2])>0) and (len(x[4])>0)) else float('nan'),
                             ymax = float(x[3])+float(x[5]) if ((len(x[3])>0) and (len(x[5])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]
        return imdet


    def _parse_csv_15(self, csvfile, header=True):
        """ v2.0: [csv_1N_gallery_S1.csv, csv_1N_gallery_S2.csv, csv_1N_probe_mixed.csv, cs3_1N_probe_img.csv]"""
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT',
                  'RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_X','NOSE_Y','FRAME_NUM']
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax = float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax = float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]
        return imdet

    def _parse_csv_16(self, csvfile, header=True):
        """[csv_1N_gallery_S1.csv, csv_1N_gallery_S2.csv, csv_1N_probe_mixed.csv, cs3_1N_probe_img.csv]"""
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILE','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT','RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_BASE_X','NOSE_BASE_Y','FRAME','CS2_BOOL']
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax = float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax = float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]
        return imdet

    def _parse_csv_15(self, csvfile, header=True):
        """D2.0 update from 7/15/16, [csv_1N_gallery_S1.csv, csv_1N_gallery_S2.csv, csv_1N_probe_mixed.csv, cs3_1N_probe_img.csv]"""
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILE','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT','RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_BASE_X','NOSE_BASE_Y','FRAME']
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax = float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax = float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1 if header else 0:]]
        return imdet

    def _parse_csv_24(self, csvfile):
        """[cs3_11_covariate_reference_metadata.csv, cs3_11_covariate_probe_metadata.csv]"""
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILE','SIGHTING_ID','FRAME','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT','RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y',
                'NOSE_BASE_X','NOSE_BASE_Y','FACE_YAW','FOREHEAD_VISIBLE','EYES_VISIBLE','NOSE_MOUTH_VISIBLE','INDOOR','GENDER','SKIN_TONE','AGE','FACIAL_HAIR']

        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             ymin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                             xmax=float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             ymax=float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet

    def _parse_csv_25(self, csvfile):
        """ v2.0: [cs3_11_covariate_reference_metadata.csv, cs3_11_covariate_probe_metadata.csv]"""
        schema = ['TEMPLATE_ID','SUBJECT_ID','FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT',
                  'RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_x','NOSE_Y','FRAME_NUM',
                  'EYES_VISIBLE','NOSE_MOUTH_VISIBLE','FOREHEAD_VISIBLE','FACIAL_HAIR','AGE','INDOOR_OUTDOOR','SKINTONE','GENDER','YAW','CS2']

        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax=float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax=float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet

    def _parse_csv_5(self, csvfile):
        """csv_face_detection.csv"""
        schema = ['FILE','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT']
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[0]), category='Face',
                             xmin=float(x[1]) if len(x[1]) > 0 else float('nan'),
                             ymin=float(x[2]) if len(x[2]) > 0 else float('nan'),
                             xmax = float(x[1])+float(x[3]) if ((len(x[1])>0) and (len(x[3])>0)) else float('nan'),
                             ymax = float(x[2])+float(x[4]) if ((len(x[2])>0) and (len(x[4])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet



    def _parse_csv_cs2(self, csvfile):
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X',
                  'NOSE_BASE_Y', 'FACE_YAW', 'FOREHEAD_VISIBLE', 'EYES_VISIBLE', 'NOSE_MOUTH_VISIBLE', 'INDOOR', 'GENDER', 'SKIN_TONE', 'AGE', 'FACIAL_HAIR']  # newer schema released on 13MAR15
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                             ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                             xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                             ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet



    def _parse_csv_16_video(self, csvfile):
        """s3_1N_probe_video.csv"""
        schema_v1 = ['TEMPLATE_ID','SUBJECT_ID','FILE','VIDEO','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT',
                     'RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_BASE_X','NOSE_BASE_Y','FRAME']
        schema_v2 = ['TEMPLATE_ID','SUBJECT_ID','FILENAME','VIDEO_FILENAME','SIGHTING_ID','FACE_X','FACE_Y','FACE_WIDTH','FACE_HEIGHT',
                     'RIGHT_EYE_X','RIGHT_EYE_Y','LEFT_EYE_X','LEFT_EYE_Y','NOSE_X','NOSE_Y','FRAME_NUM']
        schema = schema_v2 if self.v2 else schema_v1
        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             ymin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                             xmax = float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             ymax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]

        if self.v2:
            for im in imdet:
                im.attributes['VIDEO'] = im.attributes['VIDEO_FILENAME']

        imframes = [list(x) for (k,x) in groupby(imdet, key=lambda im: '%s_%s' % (im.attributes['VIDEO'], im.attributes['TEMPLATE_ID']))]  # list of sightings for each video
        return [VideoDetection(frames=f) for f in imframes]

    def _cs3_11_covariate_reference_metadata(self):
        f_parse = self._parse_csv_25 if self.v2 else self._parse_csv_24
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_11_covariate_reference_metadata.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_11_covariate_probe_metadata(self):
        f_parse = self._parse_csv_25 if self.v2 else self._parse_csv_24
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_11_covariate_probe_metadata.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_11_covariate_matches(self):
        return [(x[0], x[1]) for x in readcsv(os.path.join(self.datadir, 'protocol', 'cs3_11_covariate_matches.csv'))]

    def _cs3_1N_gallery_S1(self):
        f_parse = self._parse_csv_15 if self.v2 else self._parse_csv_16
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_1N_gallery_S1.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_1N_gallery_S2(self):
        f_parse = self._parse_csv_15 if self.v2 else self._parse_csv_16
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_1N_gallery_S2.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_1N_probe_mixed(self):
        f_parse = self._parse_csv_15 if self.v2 else self._parse_csv_16
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_1N_probe_mixed.csv'))
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['SIGHTING_ID'], im.attributes['TEMPLATE_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_1N_probe_img(self):
        f_parse = self._parse_csv_15 if self.v2 else self._parse_csv_16
        imdet = f_parse(os.path.join(self.datadir, 'protocol', 'cs3_1N_probe_img.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_11_S1_S2_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocol', 'cs3_11_S1_S2_matches.csv'))

    def _legacy_11_reference_metadata(self):
        imdet = self._parse_csv_24(os.path.join(self.datadir, 'protocol', 'legacy_11_reference_metadata.csv'))
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['SIGHTING_ID'], im.attributes['TEMPLATE_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _legacy_11_probe_metadata(self):
        imdet = self._parse_csv_24(os.path.join(self.datadir, 'protocol', 'legacy_11_probe_metadata.csv'))
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['SIGHTING_ID'], im.attributes['TEMPLATE_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _legacy_11_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocol', 'legacy_11_matches.csv'))

    def _cs3_1N_probe_video(self):
        """metadata for first available I-frame only"""
        viddet = self._parse_csv_16_video(os.path.join(self.datadir, 'protocol', 'cs3_1N_probe_video.csv'))
        imtmpl = [list(x) for (k,x) in groupby(viddet, key=lambda v: v.attributes['TEMPLATE_ID'])]  # list of videos for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs3_face_detection(self):
        return self._parse_csv_5(os.path.join(self.datadir, 'protocol', 'cs3_face_detection.csv'))

    def cs3_11(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._cs3_1N_gallery_S1() + self._cs3_1N_gallery_S2() + self._cs3_1N_probe_mixed()
        id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._cs3_11_S1_S2_matches()
        return (id_pairs, id_to_index, tmpl)

    def cs3_11_covariate(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        #tmpl = self._cs3_11_covariate_reference_metadata() + self._cs3_11_covariate_probe_metadata() # FIXME: duplicate data files in CS3
        tmpl = self._cs3_11_covariate_reference_metadata() # probe_metadata and reference_metadata are identical
        dict_id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._cs3_11_covariate_matches()
        return (id_pairs, dict_id_to_index, tmpl)

    def cs3_11_legacy(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._legacy_11_reference_metadata() + self._legacy_11_probe_metadata()
        dict_id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._legacy_11_matches()
        return (id_pairs, dict_id_to_index, tmpl)

    def cs3_1N(self):
        """Returns ([Probe1, Probe2], [Gallery1, Gallery2, Gallery3]), Each probe searched against each gallery separately"""
        probelist = [self._cs3_1N_probe_img(), self._cs3_1N_probe_mixed(),self._cs3_1N_probe_video()]
        gallerylist = [self._cs3_1N_gallery_S1(), self._cs3_1N_gallery_S2()]
        return (probelist, gallerylist)

    def cs3_1N_probe_img_gallery_S1(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_img(), self._cs3_1N_gallery_S1())

    def cs3_1N_probe_img_gallery_S2(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_img(), self._cs3_1N_gallery_S2())

    def cs3_1N_probe_mixed_gallery_S1(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_mixed(), self._cs3_1N_gallery_S1())

    def cs3_1N_probe_mixed_gallery_S2(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_mixed(), self._cs3_1N_gallery_S2())

    def cs3_1N_probe_video_gallery_S1(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_video(), self._cs3_1N_gallery_S1())

    def cs3_1N_probe_video_gallery_S2(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs3_1N_probe_video(), self._cs3_1N_gallery_S2())

    def cs3_detection(self):
        return self._cs3_face_detection()


    def all_sightings(self,P=None):
        if (P==None):
            P = [self._cs3_1N_probe_video(), self._cs3_1N_gallery_S2() + self._cs3_1N_gallery_S1(),
                 self._cs3_1N_probe_mixed(), self._cs3_1N_probe_img()]
                 #self._legacy_11_reference_metadata(), self._legacy_11_probe_metadata(),
                 #self._cs3_11_covariate_reference_metadata(), self._cs3_11_covariate_probe_metadata()]
        D = {}
        for (k, p) in enumerate(P):  # every protocol
            for t in p:  # every template in every protocol
                for v in t:  # every video or image
                    for im in v:  # every frame or image
                        key = uniq_cs3_id(im)
                        if key not in D:
                            D[key] = im
                        # elif D[key].boundingbox().overlap(im.boundingbox()) < 0.99:
                        #     print D[key], ' versus ', im

                        # So far, after the latest update, there are no duplicates according to
                        # this hashing function in uniq_cs3_id = (fileID_sightingID).
                        # Uncomment the lines above to calculate the
                        # bb overlap to see if a labeling error/ duplicate exists.
                        # cs3 should have 68919 sids according to uniq_cs3_id

                        # The hash function fpath_bboxRepr is way slow, albeit it should guarantee uniqueness.
                        # However, due to some bbox labeling errors
                        # (different subject id, different sighting id, same filename, same bbox)
                        # 250ish sightings are not included
                        # under this hash cs3 has 68666 sightings
                        # key = im.filename() + str(im.boundingbox()) labeling errors
                        # if key not in D.keys():
                        #     D[key] = im  # not seen this one yet
        return D.values()

    def cs3_clustering_protocol7(self):
        csv = ['cs3_clustering_32_hint_100.csv', 'cs3_clustering_64_hint_100.csv', 'cs3_clustering_128_hint_1000.csv', 'cs3_clustering_256_hint_1000.csv', 'cs3_clustering_512_hint_1000.csv', 'cs3_clustering_1024_hint_10000.csv', 'cs3_clustering_1870_hint_10000.csv']
        templateid_to_subjectid = {a:b for (a,b,c) in readcsv(os.path.join(self.datadir, 'clustering_protocols', 'test7_clustering', 'cs3_clustering_test7_ground_truth.csv'))}
        L = []
        for c in csv:
            imlist = self._parse_csv_12(os.path.join(self.datadir, 'clustering_protocols', 'test7_clustering', c))
            imlist = [im.category(templateid_to_subjectid[im.category()]) for im in imlist]
            L.append(imlist)
        return L
    def cs3_clustering_protocol8(self):
        return self._parse_csv_1(os.path.join(self.datadir, 'clustering_protocols', 'test8_detection_clustering', 'cs3_detection_clustering_hint_100000.csv'))


def check_for_missing_files(cs3=None):
    """Sanity check on CS3"""

    cs3 = cs3 if cs3 is not None else CS3('/proj/janus3/data')
    badfiles = []

    (P,G) = cs3.cs3_1N()
    T = P[0] + P[1] + P[2] + G[0] + G[1]
    imset = [im for t in T for im in t]  # templates or videos to list of sightings
    badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
    print len(badfiles)

    (T) = cs3.cs3_detection()
    imset = [im for t in T for im in t]  # templates to list of sightings
    badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
    print len(badfiles)

    viddet = cs3._parse_csv_16_video(os.path.join(cs3.datadir, 'protocol', 'cs3_1N_probe_video.csv'))
    badfiles = badfiles + [os.path.join(cs3.datadir, v.attributes['VIDEO']) for v in viddet if not os.path.exists(os.path.join(cs3.datadir, v.attributes['VIDEO']))]
    print len(badfiles)

    (P,D,T) = cs3.cs3_11_legacy()
    imset = [im for t in T for im in t] # templates to list of sightings
    badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
    print len(badfiles)

    (P,D,T) = cs3.cs3_11()
    imset = [im for t in T for im in t]  # templates to list of sightings
    badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
    print len(badfiles)

    (P,D,T) = cs3.cs3_11_covariate()
    imset = [im for t in T for im in t]   # templates to list of sightings
    badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
    print len(badfiles)

    # All but five files are in CS2
    return(list(set(badfiles)))
