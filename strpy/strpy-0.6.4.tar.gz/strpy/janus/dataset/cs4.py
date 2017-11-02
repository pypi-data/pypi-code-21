import os
import strpy.janus.environ
from strpy.bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv
from strpy.bobo.image import ImageDetection
from strpy.bobo.video import VideoDetection
from strpy.janus.template import GalleryTemplate
from strpy.bobo.geometry import BoundingBox
from itertools import product, groupby
from collections import OrderedDict


def uniq_cs4_id(im):
    return '%s_%s' % (im.attributes['SIGHTING_ID'], os.path.basename(im.filename()).split('.')[0])

class CS4(object):
    def __init__(self, datadir=None):
        self.datadir = os.path.join(strpy.janus.environ.data(), 'Janus_CS4', 'CS4') if datadir is None else os.path.join(datadir, 'Janus_CS4', 'CS4')
        if not os.path.isdir(self.datadir):
            raise ValueError('Download Janus CS4 dataset manually to "%s" ' % self.datadir)

    def __repr__(self):
        return str('<janus.dataset.cs4: %s>' % self.datadir)

    def _parse_csv(self, csvfile):
        """ [generic cs4 metadata csv]"""
        fields = 'TEMPLATE_ID,SUBJECT_ID,FILENAME,SIGHTING_ID,FACE_X,FACE_Y,FACE_WIDTH,FACE_HEIGHT,FRAME_NUM,FACIAL_HAIR,AGE,INDOOR_OUTDOOR,SKINTONE,GENDER,YAW,ROLL,OCC1,OCC2,OCC3,OCC4,OCC5,OCC6,OCC7,OCC8,OCC9,OCC10,OCC11,OCC12,OCC13,OCC14,OCC15,OCC16,OCC17,OCC18'
        schema = fields.split(',')

        csv = readcsv(csvfile)
        imdet = [ImageDetection(filename=os.path.join(self.datadir, x[2]), category='%04d' % int(x[1]),
                             xmin=float(x[4]) if len(x[4]) > 0 else float('nan'),
                             ymin=float(x[5]) if len(x[5]) > 0 else float('nan'),
                             xmax=float(x[4])+float(x[6]) if ((len(x[4])>0) and (len(x[6])>0)) else float('nan'),
                             ymax=float(x[5])+float(x[7]) if ((len(x[5])>0) and (len(x[7])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema,x)}) for x in csv[1:]]
        return imdet

    def _cs4_11_covariate_probe_reference(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'cs4_11_covariate_probe_reference.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]


    def _cs4_11_S1_S2_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocols', 'cs4_11_G1_G2_matches.csv'))

    def _cs4_11_covariate_matches(self):
        return readcsv(os.path.join(self.datadir, 'protocols', 'cs4_11_covariate_matches.csv'))

    def _cs4_1N_gallery_S1(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'cs4_1N_gallery_G1.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs4_1N_gallery_S2(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'cs4_1N_gallery_G2.csv'))
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs4_1N_probe_mixed(self):
        imdet = self._parse_csv(os.path.join(self.datadir, 'protocols', 'cs4_1N_probe_mixed.csv'))
        immedia = [list(x) for (k,x) in groupby(imdet, key=lambda im: ('%s_%s' % (im.attributes['TEMPLATE_ID'], im.attributes['SIGHTING_ID'])))]  # list of media
        imviddet = [VideoDetection(frames=x) if len(x)>1 else x[0] for x in immedia]  # media to video
        imtmpl = [list(x) for (k,x) in groupby(imviddet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # video and image to template
        return [GalleryTemplate(media=t) for t in imtmpl]

    def _cs4_face_detection(self):
        return self._parse_csv_5(os.path.join(self.datadir, 'protocols', 'cs4_face_detection.csv'))

    def cs4_11(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._cs4_1N_gallery_S1() + self._cs4_1N_gallery_S2() + self._cs4_1N_probe_mixed()
        id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._cs4_11_S1_S2_matches()
        return (id_pairs, id_to_index, tmpl)


    def cs4_11_covariate(self):
        """Returns (tuples of template IDs for verification, dictionary mapping template IDs to index into template list, template list)"""
        tmpl = self._cs4_11_covariate_probe_reference()
        dict_id_to_index = {str(t.templateid()):k for (k,t) in enumerate(tmpl)}
        id_pairs = self._cs4_11_covariate_matches()
        return (id_pairs, dict_id_to_index, tmpl)

    def cs4_1N_probe_mixed_gallery_S1(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs4_1N_probe_mixed(), self._cs4_1N_gallery_S1())

    def cs4_1N_probe_mixed_gallery_S2(self):
        """Returns (probe templates, gallery templates)"""
        return (self._cs4_1N_probe_mixed(), self._cs4_1N_gallery_S2())

    def cs4_detection(self):
        return self._cs4_face_detection()

    def all_sightings(self,P=None):
        if (P==None):
            P = [self._cs4_11_covariate_probe_reference(), self._cs4_1N_gallery_S2() + self._cs4_1N_gallery_S1(),
                 self._cs4_1N_probe_mixed()]
        D = {}
        for (k,p) in enumerate(P):  # every protocol
            for t in p:  # every template in every protocol
                for v in t:  # every video or image
                    for im in v:  # every frame or image
                        key = uniq_cs4_id(im)
                        if key not in D:
                            D[key] = im
                        elif D[key].boundingbox().overlap(im.boundingbox()) < 0.99:
                            print D[key], ' versus ', im

                        # So far, after the latest update, there are no duplicates according to
                        # this hashing function in uniq_cs4_id = (fileID_sightingID).
                        # Uncomment the lines above to calculate the
                        # bb overlap to see if a labeling error/ duplicate exists.
                        # cs4 should have 68919 sids according to uniq_cs4_id

                        # The hash function fpath_bboxRepr is way slow, albeit it should guarantee uniqueness.
                        # However, due to some bbox labeling errors
                        # (different subject id, different sighting id, same filename, same bbox)
                        # 250ish sightings are not included
                        # under this hash cs4 has 68666 sightings
                        # key = im.filename() + str(im.boundingbox()) labeling errors
                        # if key not in D.keys():
                        #     D[key] = im  # not seen this one yet
        return D.values()

    def cs4_clustering_protocol7(self):
        csv = ['cs4_clustering_32_hint_100.csv', 'cs4_clustering_64_hint_100.csv', 'cs4_clustering_128_hint_1000.csv', 'cs4_clustering_256_hint_1000.csv', 'cs4_clustering_512_hint_1000.csv', 'cs4_clustering_1024_hint_10000.csv', 'cs4_clustering_1870_hint_10000.csv']
        return [self._parse_csv_12(os.path.join(self.datadir, 'clustering_protocols', 'test7_clustering', c)) for c in csv]


# FIXME: CS4
# def check_for_missing_files(cs4=None):
#     """Sanity check on CS4"""
#
#     cs4 = cs4 if cs4 is not None else CS4('/proj/janus3/data')
#     badfiles = []
#
#     (P,G) = cs4.cs4_1N()
#     T = P[0] + P[1] + P[2] + G[0] + G[1]
#     imset = [im for t in T for im in t]  # templates or videos to list of sightings
#     badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
#     print len(badfiles)
#
#     (T) = cs4.cs4_detection()
#     imset = [im for t in T for im in t]  # templates to list of sightings
#     badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
#     print len(badfiles)
#
#     viddet = cs4._parse_csv_16_video(os.path.join(cs4.datadir, 'protocol', 'cs4_1N_probe_video.csv'))
#     badfiles = badfiles + [os.path.join(cs4.datadir, v.attributes['VIDEO']) for v in viddet if not os.path.exists(os.path.join(cs4.datadir, v.attributes['VIDEO']))]
#     print len(badfiles)
#
#     (P,D,T) = cs4.cs4_11_legacy()
#     imset = [im for t in T for im in t] # templates to list of sightings
#     badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
#     print len(badfiles)
#
#     (P,D,T) = cs4.cs4_11()
#     imset = [im for t in T for im in t]  # templates to list of sightings
#     badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
#     print len(badfiles)
#
#     (P,D,T) = cs4.cs4_11_covariate()
#     imset = [im for t in T for im in t]   # templates to list of sightings
#     badfiles = badfiles + [im.filename() for im in imset if not im.isvalid()]
#     print len(badfiles)
#
#     # All but five files are in CS2
#     return(list(set(badfiles)))
