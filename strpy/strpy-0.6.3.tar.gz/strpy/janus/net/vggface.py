import os
from bobo.util import writecsv, mktemp, tempcsv, loadmat, readcsv, writecsv, imlist
from viset.vggface import VGGFace
from viset.strface import STRFaceCrops
from random import shuffle
from janus.openbr import readbinary, writebinary
from janus.dataset.cs2 import CS2
from janus.dataset.cs3 import CS3
from janus.dataset.strface import STRface
from janus.dataset.IJB_A import IJBA_1N
from bobo.linalg import row_normalized
from bobo.geometry import sqdist
import janus.metrics
from itertools import product, groupby
import numpy as np
import janus.recognition
import janus.metrics
from bobo.image import ImageDetection
from janus.classifier import LinearSVMGalleryAdaptation
import bobo.app
import itertools
import matplotlib
matplotlib.rcParams['toolbar'] = 'toolbar2'  # I like the data cursor
class VGG_VD(object):
    def __init__(self, exe='vggface', model='vggface.dlib'):
        self._exe = os.path.abspath(exe)
        self._model = os.path.abspath(model)

    def __repr__(self):
        return str('<vggface.vgg_vd: exe=%s, model=%s>' % (self._exe, self._model))

    def encode(self, csvfile, mtxfile=None):
        f = mktemp('mtx') if mtxfile is None else mtxfile
        cmd = '%s --encode --dataset=%s --mtx=%s --model=%s' % (self._exe, csvfile, f, self._model)
        print '[vgg_vd.encode]: executing "%s"' % cmd
        if os.system(cmd) != 0:
            raise IOError('Error running %s' % self._exe)
        #return readbinary(f)
        return f




def cs2_encode_d20(mtxfile):
    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    R = janus.recognition.RecognitionD20()
    F = np.array([R.encode(im.boundingbox(dilate=1.1), normalize=False) for im in S])  # dilation, anisotropic scaling
    writebinary(F.astype(np.float32), mtxfile)

def cs2_encode_d20_anisotropic_flips(mtxfile):
    cs2 = CS2(datadir='/proj/janus/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    R = janus.recognition.RecognitionD20()
    F = []
    for im in S:
        im = im.boundingbox(dilate=1.1).crop()
        x = np.array(R.encode(im, normalize=False)) + np.array(R.encode(im.fliplr(), normalize=False))
        F.append(x)
    writebinary(np.array(F).astype(np.float32), mtxfile)


def cs2_encode_d20_from_crops(mtxfile):
    R = janus.recognition.RecognitionD20()
    imgs = [os.path.join('/proj/janus3/jebyrne/cs2_sightings_crops', '%08d.jpg' % k) for k in range(0,25817)]
    F = np.array([R.encode(ImageDetection(filename=f, category=None, xmin=0, ymin=0, xmax=224, ymax=224), normalize=False) for f in imgs])
    writebinary(F.astype(np.float32), mtxfile)

def cs2_encode_d20_multi(mtxfile):
    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    R = janus.recognition.RecognitionD20(gpu=True)
    import bobo.util
    bobo.util.setverbosity(1)
    print 'f_encoding is', R.encode_media
    F = np.squeeze(np.array([R.encode_media([im],multiscale = True) for im in S]))  # dilation, anisotropic scaling
    F = np.sum(F,1) / F.shape[1]

    import pdb; pdb.set_trace()
    writebinary(F.astype(np.float32), mtxfile)


def cs2_encode_d20_centercrop(mtxfile):
    cs2 = CS2(datadir='/proj/janus/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    R = janus.recognition.RecognitionD20()
    F = []
    for im in S:
        im = im.boundingbox(dilate=1.1).crop().rescale(256.0 / float(np.min([im.width(), im.height()]))).boundingbox(xmin=16,ymin=16,width=224,height=224).crop()
        F.append( R.encode(im, normalize=False) )
    writebinary(np.array(F).astype(np.float32), mtxfile)

def export_cs2_sightings_crops(outdir):
    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    for (k,im) in enumerate(S):
        im.boundingbox(dilate=1.1).crop().resize(224,224).saveas(os.path.join(outdir, '%08d.png' % k)).flush()

def cs2_encode_d20_custom(mtxfile, D20):
    """D20 = janus.recognition.RecognitionD20_retrained('str_vggface_22MAY16/vgg-m.prototxt', 'str_vggface_22MAY16/vgg-m.caffemodel')"""
    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    #R = janus.recognition.RecognitionD20()
    F = np.array([D20.encode(im.boundingbox(dilate=1.1), normalize=False) for im in S])  # TESTING
    writebinary(F.astype(np.float32), mtxfile)

def cs2_encode_caffe(mtxfile, prototxt, caffemodel):
    """Encode all sightings in CS2 using provided caffe model and save encodings to mtxfile"""
    N = janus.recognition.RecognitionD20_retrained(prototxt, caffemodel)
    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    F = np.array([N.encode(im.boundingbox(dilate=1.1), normalize=False) for im in S])
    writebinary(F.astype(np.float32), mtxfile)


def cs2_splitone_evaluation(mtxfile):
    F = readbinary(mtxfile)

    cs2 = CS2(datadir='/proj/janus/platform/data/Janus_CS2/CS2')
    P = cs2.as_templates('probe',1)
    G = cs2.as_templates('gallery',1)
    S = cs2.all_sightings()

    sightingid_to_index = {im.attributes['SIGHTING_ID']:k for (k,im) in enumerate(S)}

    X = np.zeros( (len(P), F.shape[1]) )
    for (k, tmpl) in enumerate(P):  # templates
        for m in tmpl:  # media in templates
            for im in m:  # frames/images in media
                X[k,:] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']],:]
    X = row_normalized(X)

    Y = np.zeros( (len(G), F.shape[1]))
    for (k, tmpl) in enumerate(G):
        for m in tmpl:
            for im in m:
                Y[k,:] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']],:]
    Y = row_normalized(Y)

    yhat = -sqdist(X,Y)
    y = np.array([p.category()==g.category() for (p,g) in product(P,G)]).astype(np.float32)

    import janus.metrics
    janus.metrics.report(y.flatten(), yhat.flatten(), N_gallery=[len(G)], display=False)


def cs2_evaluation(mtxfile, output_splitfile = ''):
    F = readbinary(mtxfile)

    cs2 = CS2(datadir='/proj/janus/data/Janus_CS2/CS2')
    S = cs2.all_sightings()
    sightingid_to_index = {im.attributes['SIGHTING_ID']:k for (k,im) in enumerate(S)}

    (Y_all,Yhat_all) = ([],[])
    for s in range(1,11):
        P = cs2.as_templates('probe',s)
        G = cs2.as_templates('gallery',s)

        X = np.zeros( (len(P), F.shape[1]) )
        for (k, tmpl) in enumerate(P):  # templates
            for m in tmpl:  # media in templates
                for im in m:  # frames/images in media
                    X[k,:] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']],:]
        X = row_normalized(X)

        Y = np.zeros( (len(G), F.shape[1]) )
        for (k, tmpl) in enumerate(G):
            for m in tmpl:
                for im in m:
                    Y[k,:] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']],:]
        Y = row_normalized(Y)

        yhat = -sqdist(X,Y)
        y = np.array([p.category() == g.category()
                      for (p,g) in product(P,G)]).astype(np.float32).reshape(len(P),len(G))

        Y_all.append(y)
        Yhat_all.append(yhat)

        if output_splitfile != '':
            export_split_for_error_eval(y, yhat, G, P, X, Y,
                                        output_splitfile, s)

    janus.metrics.report(Y_all, Yhat_all, N_gallery=None, display=False)
    return [Y_all, Yhat_all]



def ijba1N_evaluation(mtxfile, cmcFigure=3, detFigure=4, prependToLegend='D3.0', hold=False, output_splitfile='', splitmean=False,
                      detLegendSwap=False, cmcLegendSwap=False, cmcMinY=0.0, metrics=True):
    F = readbinary(mtxfile)

    ijba = IJBA_1N(datadir='/proj/janus/data/IJB-A/CS2/',
                   protocoldir='/proj/janus/data/IJB-A/IJB-A_1N/')

    S = ijba.all_sightings()
    sightingid_to_index = {im.attributes['SIGHTING_ID']: k for (k, im) in enumerate(S)}

    (Y_all, Yhat_all) = ([], [])
    for s in range(1, 11):
        P = ijba.as_templates('search_probe', s)
        G = ijba.as_templates('search_gallery', s)

        X = np.zeros((len(P), F.shape[1]))
        for (k, tmpl) in enumerate(P):  # templates
            for m in tmpl:  # media in templates
                for im in m:  # frames/images in media
                    X[k, :] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']], :]
        X = row_normalized(X)

        Y = np.zeros((len(G), F.shape[1]))
        for (k, tmpl) in enumerate(G):
            for m in tmpl:
                for im in m:
                    Y[k, :] += (1.0 / float(len(m))) * F[sightingid_to_index[im.attributes['SIGHTING_ID']],:]
        Y = row_normalized(Y)

        yhat = -sqdist(X, Y)
        y = np.array([p.category() == g.category()
                      for (p, g) in product(P, G)]).astype(np.float32).reshape(len(P), len(G))

        Y_all.append(y)
        Yhat_all.append(yhat)

        if output_splitfile != '':
            export_split_for_error_eval(y, yhat, G, P, X, Y,
                                        output_splitfile, s)
    if metrics:
        janus.metrics.ijba1N(Y_all, Yhat_all,
                             cmcFigure=cmcFigure, detFigure=detFigure, splitmean=splitmean,
                             prependToLegend=prependToLegend, detLegendSwap=detLegendSwap,
                             cmcLegendSwap=cmcLegendSwap, hold=hold, cmcMinY=cmcMinY)
    return [Y_all, Yhat_all]



def cs2_sightings_dataset(outfile='cs2.csv'):
    cs2 = CS2('/proj/janus/platform/data/Janus_CS2/CS2')
    imset = cs2.all_sightings()
    S = {s:k for (k,s) in enumerate(cs2.subjects())}  # category to identifier (zero indexed)
    L = []
    for im in imset:
        im = im.boundingbox(dilate=1.1)
        L.append((im.filename(), S[im.category()], round(im.boundingbox().xmin), round(im.boundingbox().ymin), round(im.boundingbox().width()), round(im.boundingbox().height())))
    return writecsv(L, outfile)


def partition_vggface_dataset():
    #V = VGGFace('/proj/janus3/vgg-face/vgg-face-janus')
    V = VGGFace('/mnt/vggface/vgg-face-janus')
    S = {s:k for (k,s) in enumerate(V.subjects())}  # category to identifier (zero indexed)
    L = [(im.filename(), S[im.category()]) for im in V.fastset()]  # fastset does not load images
    shuffle(L)  # in place
    n = int(0.01*len(L))  # 0.01 of dataset is validation set
    print '[vggface.dataset]: exporting testset to "%s"' % writecsv(L[0:250], 'testset.csv')
    print '[vggface.dataset]: exporting validationset to "%s"' % writecsv(L[251:n], 'valset.csv')
    print '[vggface.dataset]: exporting trainset to "%s"' % writecsv(L[n+1:], 'trainset.csv')

def partition_vggface_dataset_using_imdb():
    """Load imdb.mat in matlab, save imdb.images.names to vgg_face_names.mat, save imdb.images.set to vgg_face_set.mat"""
    #V = VGGFace('/proj/janus3/vgg-face/vgg-face-janus')
    V = VGGFace('/mnt/vggface/vgg-face-janus')
    #V = VGGFace('/data/janus/vgg-face/vgg-face-janus')
    vgg_filenames = [str(s[0]) for s in loadmat('vgg_face_names.mat')['a'][0]]
    vgg_sets = loadmat('vgg_face_set.mat')['b'][0]
    D = {n:s for (n,s) in zip(vgg_filenames, vgg_sets)}  # dictionary from relative paths to set index (1=train, 2=val, 3=test)

    S = {s:k for (k,s) in enumerate(V.subjects())}  # category to identifier (zero indexed)
    L_train = []
    L_val = []
    for im in V.fastset():
        (impath, imbase) = os.path.split(im.filename())  # (/a/b/c, d.jpg)
        imrelpath = os.path.join(os.path.basename(impath), imbase)  # c/d.jpg
        if (D[imrelpath] == 1):
            L_train.append((im.filename(), S[im.category()]))
        if (D[imrelpath] == 2 or D[imrelpath] == 3 ):
            L_val.append((im.filename(), S[im.category()]))

    print '[vggface.dataset]: exporting trainset to "%s"' % writecsv(L_train, 'trainset_from_imdb.csv')
    print '[vggface.dataset]: exporting trainset to "%s"' % writecsv(L_val, 'valset_from_imdb.csv')



def merge_vggface_strface():
    A = readcsv('trainset_from_imdb.csv')  # subjectid = 0,2622
    B = readcsv('valset_from_imdb.csv')
    str = STRFaceCrops()
    S = {s:k for (k,s) in enumerate(str.subjects())}  # category to identifier (zero indexed)
    maxid = np.max([int(r[1]) for r in A+B])
    C = [(im.filename(),S[im.category()]+maxid+1) for im in str.fastset()]  # entire set

    c = []
    N = np.floor(float(len(A)+len(B)) / float(len(S.keys())))  # balanced
    for key, group in groupby(C, lambda x: x[1]):
        G = list(group)  # from iterator
        K = np.random.choice(len(G),N)  # randomly select N indices
        c = c + [G[k] for k in K]  # balanced set

    print writecsv(A+B+c, 'train_vggface_plus_strface.csv')


def export_split_for_error_eval(Y,yhat,gallery_templates,probe_templates,P_feat,G_feat, basename, split):
    n_probe = len(P_feat);
    n_gallery = len(G_feat);

    if (n_probe != Y.shape[0]) or (n_gallery != Y.shape[1]):
        print 'Dimensions mismatch in matrix sizes ', (n_probe,n_gallery), ' vs ', Y.shape
    gtMatrix_orig = Y; similarityMatrix = yhat.copy(); gtMatrix = np.zeros(Y.shape);
    sorted_gallery_tids = [];

    probe_tids = np.array([p_template.templateid() for p_template in probe_templates])
    gallery_tids = np.array([g_template.templateid() for g_template in gallery_templates])

    for i in range(0,n_probe):
        k = np.argsort(-similarityMatrix[i,:])  # index of sorted rows in descending order
        similarityMatrix[i,:] = similarityMatrix[i,k]  # reorder columns in similarityOrder
        gtMatrix[i,:] = gtMatrix_orig[i,k]  # reorder ground truth in same order
        sorted_gallery_tids.append(gallery_tids[k[0]])  # Predicted gallery Template IDs for all probes
    gt_indeces = [np.where(gtMatrix_orig[i, :] == 1)[0] for i, ptid in enumerate(probe_tids)]
    gallery_tids_gt = np.array([gallery_tids[idx[0]] if idx else -1 for idx in gt_indeces])  # Correct Gallery Template id for all probes
    correct_gallery_feat = np.array([G_feat[np.where(gallery_tids == g)[0]] for g in gallery_tids_gt])  # Features of the correct gallery template
    gallery_feat = [G_feat[np.where(gallery_tids == g)[0]] for g in sorted_gallery_tids ]

    output_dic = {'G_tids':sorted_gallery_tids,
                  'P_tids' :probe_tids,
                  'G_tids_correct':gallery_tids_gt,
                  'probe_feat':P_feat,
                  'gallery_feat':gallery_feat,
                  'gallery_feat_correct':correct_gallery_feat,
                  'gt':gtMatrix[:,0],
                  'mean_gallery':np.mean(np.array(G_feat),0)}

    with open(basename + "_split_%s.pk" % split, 'wb') as f:
        import dill
        dill.dump(output_dic,f)
