import os
import numpy as np
from bobo.util import load, tolist, tolist
from janus.dataset.cs2 import CS2
from sklearn.preprocessing import normalize
import itertools
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate

def pool_media_into_templates(G, Gtid, Gc):
    templates = {}
    for i in range(0, len(Gtid)):
        if templates.has_key(Gtid[i]):
            templates[Gtid[i]].append(i)
        else:
            templates[Gtid[i]] = [i]

    new_G = [None] * len(templates.keys())
    new_Gtid = templates.keys()
    new_Gc = [None] * len(templates.keys())

    for i in range(0, len(new_Gtid)):
        feat = np.zeros(G[0].shape)
        ts = templates[new_Gtid[i]]
        for j in ts:
            feat = feat + G[j]
        feat = feat
        new_G[i] = feat
        new_Gc[i] = Gc[templates[new_Gtid[i]][0]]

    return new_G, new_Gtid, new_Gc

def norm(feat):
    normalized_feat = [None] * len(feat)
    for i in range(0, len(feat)):
        feat[i] = np.reshape(feat[i], (1, feat[i].size))
        normalized_feat[i] = normalize(feat[i], norm='l2')[0]
    return normalized_feat

def get_raw_and_fro_features(media, f_encoding,multiscale = False):
    mfeat = None
    nimages = 0
    batch_size = 10

    raw_ims = [im for im in media if len(im.attributes['SIGHTING_ID'].split('_')) == 1]
    fro_ims = [im for im in media if len(im.attributes['SIGHTING_ID'].split('_')) != 1]

    raw_feat, fro_feat = None, None
    n_raw, n_fro = 0, 0

    for i in range(0, max(len(raw_ims), len(raw_ims)-batch_size), batch_size):
        tmp_feat = f_encoding(raw_ims[i: i+batch_size], multiscale=multiscale)
        tmp_nraw = len(tmp_feat)
        tmp_feat = np.sum(tmp_feat, axis=0)
        raw_feat = raw_feat + tmp_feat if raw_feat is not None else tmp_feat
        n_raw += tmp_nraw

    if fro_ims != []:
        fro_feat = None
        for i in range(0, max(len(fro_ims), len(fro_ims)-batch_size), batch_size):
            tmp_feat = f_encoding(fro_ims[i: i+batch_size], multiscale=False)
            tmp_nfro = len(tmp_feat)
            tmp_feat = np.sum(tmp_feat, axis=0)
            fro_feat = fro_feat + tmp_feat if fro_feat is not None else tmp_feat
            n_fro += tmp_nfro

    return raw_feat, n_raw, fro_feat, n_fro

def get_raw_and_fro_features_uneq_weights(media, f_encoding,multiscale = False,do_bads = False):
    mfeat = None
    nimages = 0
    batch_size = 10

    culled_media = cull_bads_from_media(media) if do_bads else None

    target_media = culled_media if culled_media is not None else media;

    if do_bads and media.mediatype() =='video' and len(media.frames()) != len(target_media.frames()):
        print 'Difference  in length after culling for media %s is %s' % ( media.frames()[0].attributes['MEDIA_ID'],len(media) - len(target_media))

    raw_ims = [im for im in target_media if len(im.attributes['SIGHTING_ID'].split('_')) == 1]

    fro_feature_dict ={}

    fro_dict = {k:list(g) for k,g in itertools.groupby(target_media, lambda im : im.attributes['SIGHTING_ID'].split('_')[0] if len(im.attributes['SIGHTING_ID'].split('_')) != 1  else None )}


    raw_feat, fro_feat = None, None
    n_raw, n_fro = 0, 0

    for i in range(0, max(len(raw_ims), len(raw_ims)-batch_size), batch_size):
        tmp_feat = f_encoding(raw_ims[i: i+batch_size], multiscale=multiscale)
        tmp_nraw = len(tmp_feat)
        tmp_feat = np.sum(tmp_feat, axis=0)
        raw_feat = raw_feat + tmp_feat if raw_feat is not None else tmp_feat
        n_raw += tmp_nraw

    if fro_dict.keys():
        fro_feat = None
        for sid in fro_dict.keys():
            frontal_images = fro_dict[sid]
            front_feat_list = f_encoding(frontal_images, multiscale=False)
            nfeat = len(front_feat_list)
            fro_feature_dict[sid] = np.sum(front_feat_list,0)/nfeat
            fro_feat = fro_feat + fro_feature_dict[sid] if fro_feat is not None else fro_feature_dict[sid]
        fro_dict.pop(None,None)
    # import pdb
    # pdb.set_trace()

    n_fro = len(fro_dict.keys()) # we have one extra key

    return raw_feat, n_raw, fro_feat, n_fro

def simple_media_pooling(media, f_encoding, multiscale = True,do_bads = False):
    mfeat = None
    nimages = 0
#    raw_feat, n_raw, fro_feat, n_fro = get_raw_and_fro_features(media, f_encoding, multiscale)
    raw_feat, n_raw, fro_feat, n_fro = get_raw_and_fro_features_uneq_weights(media, f_encoding, multiscale,do_bads)
    if fro_feat is None:
        mfeat = raw_feat / (n_raw*1.0)
    else:
        mfeat = (raw_feat + fro_feat)/((n_raw + n_fro)*1.0)
    mfeat = np.reshape(mfeat, (1, mfeat.size))
    return mfeat

def load_feature_file(sc, split, featurefile, feat=None, pool=False,do_bads = False,cs2 = None):

    cs2 = CS2(sparkContext=sc) if cs2 is None else cs2
    template_capturing_func = cs2.rdd_as_good_image_templates if do_bads else cs2.rdd_as_templates
    dataset = cs2.splits(split=split, rdd = template_capturing_func)
    trainset, galleryset, probeset = dataset[0]

    feat = load(featurefile)
    subjects, media_ids, features = feat['subjects'], feat['media_ids'], feat['feat']

    media_feat_dic = {}

    for i in range(0, len(media_ids)):
        media_feat_dic[media_ids[i]] = (subjects[i], features[i])

    G, Gid, Gc = collect_template_medias(galleryset, media_feat_dic)
    T, Tid, Tc = collect_template_medias(trainset, media_feat_dic)
    P, Pid, Pc = collect_template_medias(probeset, media_feat_dic)
    print 'T: %s, G: %s, P: %s' % (len(T), len(G), len(P))
    print 'before pooling :',len(G),len(P),len(T)
    G, P, T = list(G), list(P), list(T)
    if pool == True:
        G, Gid, Gc = pool_media_into_templates(G, Gid, Gc)
        P, Pid, Pc = pool_media_into_templates(P, Pid, Pc)
        T, Tid, Tc = pool_media_into_templates(T, Tid, Tc)
    G, P, T = norm(G), norm(P), norm(T)
    print 'after pooling :',len(G),len(P),len(T)
    return T, Tid, Tc, G, Gid, Gc, P, Pid, Pc

def collect_template_medias(dataset, media_feat_dic):

    dataset = dataset.flatMap(lambda t: [(m.attributes['MEDIA_ID'] , t.templateid()) for m in t.media()])
    dataset_media, dataset_template = zip(*dataset.collect())
    nmedia = len(dataset_media)

    R, Rid, Rc = [None] * nmedia, [None] * nmedia, [None] * nmedia
    Rid = dataset_template

    for i in range(0, nmedia):
        mID = dataset_media[i]
        if mID not in media_feat_dic.keys():
            raise Exception('mid: %s not present' % mID)
            continue
        Rc[i] = media_feat_dic[mID][0]
        R[i] =  media_feat_dic[mID][1]

    return R, Rid, Rc

def load_feature_file_one_split(featurefile, pool=True):
    if not os.path.exists(featurefile):
        raise Exception('File: %s does not exist' % featurefile)
    else:
        print 'Loading features from %s ' % featurefile
        feat = load(featurefile)
        Gid, Gc, G, Pid, Pc, P = feat['gid'], feat['gc'], feat['gf'], feat['pid'], feat['pc'], feat['pf']
        Tid, Tc, T = feat['tid'], feat['tc'], feat['tf']
        G, P, T = list(G), list(P), list(T)
        print 'before pooling :',len(G),len(P),len(T)
        if pool == True:
            G, Gid, Gc = pool_media_into_templates(G, Gid, Gc)
            P, Pid, Pc = pool_media_into_templates(P, Pid, Pc)
            T, Tid, Tc = pool_media_into_templates(T, Tid, Tc)
        G, P, T = norm(G), norm(P), norm(T)
        print 'after pooling :',len(G),len(P),len(T)
    return T, Tid, Tc, G, Gid, Gc, P, Pid, Pc

class anatomical_articulation(object):
    def __init__(self, articulation_string = "template_A"):
        if articulation_string == "template_A":
            self.poses = [('+00','+00'),('-40','+00'),('+40','+00')]
            self.expressions_per_pose = 6
            self.capture_strings = ['yaw_%s_pitch_%s_template_A_%03d' % (pose[0],pose[1],i) for pose in self.poses for i in xrange(0,self.expressions_per_pose) ]
        else:
            self.poses = 0
            self.expressions_per_pose = 0
            self.capture_strings = ['None']

def cull_bads_from_template(T):
    good_videos = []
    good_images = [im for im in T.images() if im.attributes['GOOD'] == 1.0]

    for vid in T.videos():
        new_frames = [f for f in vid.frames() if f.attributes['GOOD'] == 1.0]
        if new_frames:
            good_videos.append(VideoDetection(frames = new_frames,attributes={'MEDIA_ID':new_frames[0].attributes['MEDIA_ID'],'TEMPLATE_ID':T.templateid()}))

    if T.videos() and not good_videos:
        print "template ID ", T.templateid(), " had all videos bad"
    if not good_images and not good_videos:
#        print "template ID ", T.templateid(), " had all images bad"
        return T
    elif not good_images:
        return GalleryTemplate(media = tolist(good_videos) )
    else:
        return GalleryTemplate(media = tolist(good_videos + good_images))

def cull_bads_from_media(M):
    culled_set = [im for im in M if im.attributes['GOOD'] == 1]

    if not culled_set:
        return None

    return VideoDetection(frames = culled_set, attributes={'MEDIA_ID':culled_set[0].attributes['MEDIA_ID'],'SUBJECT_ID':culled_set[0].attributes['SUBJECT_ID'] }, category = culled_set[0].attributes['SUBJECT_ID']) if len(culled_set) !=1 else culled_set[0]
