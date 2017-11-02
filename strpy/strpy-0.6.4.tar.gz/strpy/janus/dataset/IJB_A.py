import os
from janus.dataset.cs2 import CS2
import bobo.app
from bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv, remkdir, writecsv, dirlist, csvlist
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
from bobo.geometry import BoundingBox
from itertools import product
import numpy as np
from collections import OrderedDict


def uniq_ijba_id(im):
    return '%s_%s' % (im.attributes['SIGHTING_ID'], os.path.basename(im.filename()).split('.')[0])

class IJBA_11(CS2):
    def __init__(self, datadir=None, protocoldir=None, sparkContext=None, appname='janus_ijba_11', partitions=None):
        """datadir should contain the 'frame' directory, protocoldir should contain 'split%d' directories"""
        self.datadir = os.path.join(janus.environ.data(), 'IJB-A') if datadir is None else os.path.join(datadir, 'IJB-A')
        self.protocoldir = os.path.join(self.datadir, 'protocol', 'IJB-A', 'IJBA_11') if protocoldir is None else protocoldir
        if not os.path.isdir(os.path.join(self.datadir)):
            raise ValueError('Download Janus IJB-A dataset manually to "%s" ' % self.datadir)
        self.minPartitions = partitions  # spark.default.parallelism if None
        self.f_remapimage = None
        self.appname = appname
        self.sparkContext = sparkContext

    def __repr__(self):
        return str('<janus.dataset.ijb.IJBA_11: data=%s, protocol=%s>' % (self.datadir, self.protocoldir))

    def _initspark(self):
        self.sparkContext = bobo.app.init(self.appname)


    def _cs2_to_ijba11(self, cs2, Y, Yhat):
        """Convert a list of CS2 matrices into a list of IJBA 1:1 verification matrices suitable for janus.metrics.ijba11"""
        """Y = [ M1xN1, M2xN2, ..., MkxNk], Yhat =  [ M1xN1, M2xN2, ..., MkxNk] for M probes and N gallery templates.  Must be in same template id order as output from cs2.as_templates()"""
        #ijb = IJBA_11(datadir='/proj/janus/platform/data/Janus_CS2/CS2', protocoldir='/proj/janus/platform/data/IJB-A/IJB-A_11')
        #cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')

        (Y_ijba, Yhat_ijba) = ([], [])
        for s in range(1,len(Y)+1):
            P = cs2.as_templates('probe', s)  # in csv order
            G = cs2.as_templates('gallery', s)  # in csv order

            Pid = {int(p.templateid()):j for (j,p) in enumerate(P)}  # probe id in csv order
            Gid = {int(g.templateid()):j for (j,g) in enumerate(G)}  # gallery id in csv order

            # Extract IJB-A 1:1 verification pairs only
            y_pairs = [Y[s-1][Pid[j], Gid[i]] for (i,j) in self.verification(s)]
            yhat_pairs = [Yhat[s-1][Pid[j], Gid[i]] for (i,j) in self.verification(s)]
            Y_ijba.append(y_pairs)
            Yhat_ijba.append(yhat_pairs)

        return (Y_ijba, Yhat_ijba)

    def splitfile(self, dataset, split):
        """dataset = ['verify_metadata', 'train']"""
        csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), '%s_%d.csv' % (dataset, split))
        if not os.path.isfile(csvfile):
            raise ValueError('File not found "%s"' % csvfile)
        return csvfile

    def verification(self, split):
        csv = readcsv(os.path.join(self.protocoldir, 'split%d' % int(split), 'verify_comparisons_%d.csv' % int(split)))
        return [(int(p), int(q)) for (p,q) in csv]

    def rdd_all_media(self):
        M = self.rdd_as_media('train',1).map(lambda m: (m.attributes['MEDIA_ID'], m))
        for (d,s) in product(['train','verify_metadata'], range(1,11)):
            M = M.union(self.rdd_as_media(d,s).map(lambda m: (m.attributes['MEDIA_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()

    def rdd_all_sightings(self):
        M = self.rdd('train',1).map(lambda m: (m.attributes['SIGHTING_ID'], m))
        for (d,s) in product(['train','verify_metadata'], range(1,11)):
            M = M.union(self.rdd(d,s).map(lambda m: (m.attributes['SIGHTING_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()


def export_ijba11(Yhat, ijba11, templateSize=10488, outdir='.', offset=0.0):
    """Write out IBJA-11 formatted directories: Yhat = [ vector_similarity_split1, vector_similarity_split2, ...], Pid = [ list_of_templateid_tuples_split1, ... ]"""
    remkdir(outdir)
    #yhatmin = np.min([np.min(np.array(yh).flatten()) for yh in Yhat]) # minimum across all splits to guarantee export non-negative
    yhatmin = offset
    for s in range(0,len(Yhat)):
        csv = [('ENROLL_TEMPLATE_ID', 'VERIF_TEMPLATE_ID', 'ENROLL_TEMPLATE_SIZE_BYTES', 'VERIF_TEMPLATE_SIZE_BYTES', 'RETCODE', 'SIMILARITY_SCORE')]
        remkdir(os.path.join(outdir, 'split%d' % (s+1)))
        csvfile = os.path.join(outdir, 'split%d' % (s+1), 'split%d.matches' % (s+1))

        #(yhat, tid) = (Yhat[s], templateID[s])
        (yhat, tid) = (Yhat[s], ijba11.verification(s+1))
        for i in range(0, len(tid)):
            csv.append( (tid[i][0], tid[i][1], templateSize, templateSize, 0, float(yhat[i]) - yhatmin) )  # nonnegative similarity
        print '[IJBA_11.export]: writing "%s"' % writecsv(csv, csvfile, separator=' ')


class IJBA_1N(CS2):
    def __init__(self, datadir=None, protocoldir=None, sparkContext=None, appname='janus_ijba_1N', partitions=None):
        self.datadir = '/Users/jeffrey.byrne/Google Drive/CS2' if datadir is None else datadir
        self.datadir = os.path.join(janus.environ.data(), 'IJB-A') if datadir is None else os.path.join(datadir, 'IJB-A')
        self.protocoldir = os.path.join(self.datadir, 'protocol', 'IJB-A', 'IJBA_1N') if protocoldir is None else protocoldir
        if not os.path.isdir(os.path.join(self.datadir)):
            raise ValueError('Download Janus IJB-A dataset manually to "%s" ' % self.datadir)
        self.sparkContext = sparkContext
        self.appname = appname
        self.minPartitions = partitions  # spark.default.parallelism if None
        self.f_remapimage = None

    def __repr__(self):
        return str('<janus.dataset.ijb.IJBA_1N: data=%s, protocol=%s>' % (self.datadir, self.protocoldir))

    def _initspark(self):
        self.sparkContext = bobo.app.init(self.appname)

    def _cs2_to_ijba1N(self, cs2, Y, Yhat):
        """Convert a list of CS2 matrices over splits into a list of IJBA 1:N identification matrices suitable for janus.metrics.ijba1N"""
        """Y = [ M1xN1, M2xN2, ..., MkxNk], Yhat =  [ M1xN1, M2xN2, ..., MkxNk] for M probes and N gallery templates.  Must be in same template id order as output from cs2.as_templates()"""
        #ijb = IJBA_1N(datadir='/proj/janus/platform/data/Janus_CS2/CS2', protocoldir='/proj/janus/platform/data/IJB-A/IJB-A_1N')
        #cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')

        (Y_ijba, Yhat_ijba) = ([],[])
        for s in range(1,len(Y)+1):
            P_ijba = self.as_templates('search_probe', s)  # csv order
            G_ijba = self.as_templates('search_gallery', s)  # in csv order, IJB-A 1:N gallery templates

            P = cs2.as_templates('probe', s)  # in csv order
            G = cs2.as_templates('gallery', s)  # in csv order

            P_id2index = {p.templateid():j for (j, p) in enumerate(P)}  # dictionary from templateids to row/column index in P
            G_id2index = {g.templateid():j for (j, g) in enumerate(G)}  # dictionary from templateids to row/column index in G

            y_reorder = []  # FIXME: this reorder may not be necessary
            yhat_reorder = []

            for (p, g) in product(P_ijba, G_ijba):
                y_reorder.append(Y[s-1][P_id2index[p.templateid()], G_id2index[g.templateid()]])
                yhat_reorder.append(Yhat[s-1][P_id2index[p.templateid()], G_id2index[g.templateid()]])
            Y_ijba.append(np.array(y_reorder).reshape( (len(P_ijba), len(G_ijba)) ))
            Yhat_ijba.append(np.array(yhat_reorder).reshape( (len(P_ijba), len(G_ijba)) ))

        return (Y_ijba,Yhat_ijba)

    def splitfile(self, dataset, split):
        csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), '%s_%d.csv' % (dataset, split))
        if not os.path.isfile(csvfile):
            raise ValueError('File not found "%s"' % csvfile)
        return csvfile

    def rdd_all_media(self):
        M = self.rdd_as_media('train',1).map(lambda m: (m.attributes['MEDIA_ID'], m))
        for (d,s) in product(['train','search_gallery','search_probe'], range(1,11)):
            M = M.union(self.rdd_as_media(d,s).map(lambda m: (m.attributes['MEDIA_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()

    def rdd_all_sightings(self):
        M = self.rdd('train',1).map(lambda m: (m.attributes['SIGHTING_ID'], m))
        for (d,s) in product(['train','search_gallery','search_probe'], range(1,11)):
            M = M.union(self.rdd(d,s).map(lambda m: (m.attributes['SIGHTING_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()

    def splits(self, split=None, rdd=CS2.rdd):
        """Use provided rdd function to return properly constructed RDDs for all splits"""
        split = range(1, 11) if split is None else split
        return [[rdd(dataset=d, split=s) for d in ['train', 'search_gallery', 'search_probe']] for s in tolist(split)]

    def all_sightings(self, P=None):
        M = []
        for (d, s) in product(['train', 'search_probe', 'search_gallery'], range(1, 11)):
            M = M + [(m.attributes['SIGHTING_ID'], m) for m in self.as_sightings(d, s)]
        return list(OrderedDict(M).values())  # in csv order



def export_ijba1N(Yhat, ijba1N, templateSize=10488, outdir='.', offset=0.0):
    """Write out IBJA-1N formatted directories: Yhat = [similarity_matrix_split1,....], Pid = [probeid_split1,...], Gid = [galleryid_split1,...]"""
    remkdir(outdir)
    #yhatmin = np.min([np.min(np.array(yh).flatten()) for yh in Yhat]) + 1E-6  # minimum similarity across all splits to guarantee export non-negative
    yhatmin = offset
    for s in range(0, len(Yhat)):
        csv = [('SEARCH_TEMPLATE_ID', 'CANDIDATE_RANK', 'ENROLL_TEMPLATE_ID', 'ENROLL_TEMPLATE_SIZE_BYTES', 'SEARCH_TEMPLATE_SIZE_BYTES', 'RETCODE', 'SIMILARITY_SCORE')]
        remkdir(os.path.join(outdir, 'split%d' % (s+1)))
        csvfile = os.path.join(outdir, 'split%d' % (s+1), 'split%d.candidate_lists' % (s+1))

        #(yhat, pid, gid) = (Yhat[s], probeID[s], galleryID[s])
        (yhat, pid, gid) = (Yhat[s], [p.templateid() for p in ijba1N.as_templates('search_probe', s+1)], [g.templateid() for g in ijba1N.as_templates('search_gallery', s+1)])
        for i in range(0, len(pid)):
            j = np.argsort(-yhat[i,:])  # yhat is similarity -> -yhat is distance -> sort in ascending distance order
            for k in range(0,20):  # 20 candidates
                csv.append( (pid[i], k, gid[j[k]], templateSize, templateSize, 0, float(yhat[i,j[k]]) - yhatmin) )  # non-negative similarity

        print '[IJB_1N.export]: writing "%s"' % writecsv(csv, csvfile, separator=' ')


def import_cs2(indir, cs2):
    """Import CS2 output in IJBA-11 csv file format into a matrix format suitable for janus.metrics.report(Y,Yhat)"""
    SCHEMA = ['SEARCH_TEMPLATE_ID', 'CANDIDATE_RANK', 'ENROLL_TEMPLATE_ID', 'ENROLL_TEMPLATE_SIZE_BYTES', 'SEARCH_TEMPLATE_SIZE_BYTES', 'RETCODE', 'SIMILARITY_SCORE']
    (Y, Yhat) = ([], [])
    for d in dirlist(indir):
        s = int(d.split('split')[1])  # split index
        f = os.path.join(d, 'split%d.candidate_lists' % s)
        csv = readcsv(f, separator=' ')[1:]

        P = cs2.as_templates('probe', s)
        G = cs2.as_templates('gallery', s)

        P_id2idx = {p.templateid():k for (k,p) in enumerate(P)}
        G_id2idx = {g.templateid():k for (k,g) in enumerate(G)}
        y = np.array([p.category() == g.category() for (p,g) in product(P,G)]).reshape( (len(P), len(G)) ).astype(np.float32)
        yhat = np.zeros( (len(P), len(G)) )
        for r in csv:
            dd = dict(zip(SCHEMA, r))
            i = P_id2idx[dd['SEARCH_TEMPLATE_ID']]
            j = G_id2idx[dd['ENROLL_TEMPLATE_ID']]
            yhat[i,j] = float(dd['SIMILARITY_SCORE'])
        Y.append(y)
        Yhat.append(yhat)

    return (Y,Yhat)


def import_ijba1N(indir, ijba1N):
    """Import ijba-1N csv file format into a matrix format suitable for janus.metrics.ijba1N(Y,Yhat)"""
    SCHEMA = ['SEARCH_TEMPLATE_ID', 'CANDIDATE_RANK', 'ENROLL_TEMPLATE_ID', 'ENROLL_TEMPLATE_SIZE_BYTES', 'SEARCH_TEMPLATE_SIZE_BYTES', 'RETCODE', 'SIMILARITY_SCORE']
    (Y, Yhat) = ([], [])
    for d in dirlist(indir):
        print d
        s = int(d.split('split')[1])  # split index
        f = os.path.join(d, 'split%d.candidate_lists' % s)
        csv = readcsv(f, separator=' ')[1:]

        P = ijba1N.as_templates('search_probe', s)
        G = ijba1N.as_templates('search_gallery', s)

        P_id2idx = {p.templateid():k for (k,p) in enumerate(P)}
        G_id2idx = {g.templateid():k for (k,g) in enumerate(G)}
        y = np.array([p.category() == g.category() for (p,g) in product(P,G)]).reshape( (len(P), len(G)) ).astype(np.float32)
        yhat = np.zeros( (len(P), len(G)) )
        for r in csv:
            dd = dict(zip(SCHEMA, r))
            i = P_id2idx[dd['SEARCH_TEMPLATE_ID']]
            j = G_id2idx[dd['ENROLL_TEMPLATE_ID']]
            #y[i,j] = float(P[i].category() == G[j].category())
            yhat[i,j] = float(dd['SIMILARITY_SCORE'])
        Y.append(y)
        Yhat.append(yhat)

    return (Y,Yhat)


def import_ijba11(indir, ijba11):
    """Import ijba-11 csv file format into a matrix format suitable for janus.metrics.ijba11(Y,Yhat)"""
    SCHEMA = ['ENROLL_TEMPLATE_ID', 'VERIF_TEMPLATE_ID', 'ENROLL_TEMPLATE_SIZE_BYTES', 'VERIF_TEMPLATE_SIZE_BYTES', 'RETCODE', 'SIMILARITY_SCORE']
    (Y, Yhat) = ([], [])
    for d in dirlist(indir):
        s = int(d.split('split')[1])  # split index
        f = os.path.join(d, 'split%d.matches' % s)
        csv = readcsv(f, separator=' ')[1:]
        V = ijba11.as_templates('verify_metadata', s)
        V_id2idx = {v.templateid():k for (k,v) in enumerate(V)}
        y = []
        yhat = []
        for r in csv:
            dd = dict(zip(SCHEMA, r))
            i = V_id2idx[dd['VERIF_TEMPLATE_ID']]
            j = V_id2idx[dd['ENROLL_TEMPLATE_ID']]
            y.append(float(V[i].category() == V[j].category()))
            yhat.append(float(dd['SIMILARITY_SCORE']))
        Y.append(y)
        Yhat.append(yhat)

    return (Y,Yhat)
