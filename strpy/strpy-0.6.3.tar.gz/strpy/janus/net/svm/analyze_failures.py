import itertools
import numpy as np
import dill
from itertools import product, combinations
from janus.dataset.cs4 import CS4
import os
import shutil
from janus.dataset.cs4 import uniq_cs4_id
import glob
import janus.pvr.python_util.io_utils as io_utils
import bobo.image
import bobo.geometry
import dlibnet
import face3d
import vxl
import janus.pvr.python_util.io_utils as io_utils
import janus.pvr.camera_decomposition as camera_decomposition
import janus.pvr.python_util.geometry_utils as geometry_utils
from sklearn.svm import SVC, LinearSVC
from janus.openbr import readbinary
janus_root = os.environ.get('JANUS_ROOT')
janus_data = os.environ.get('JANUS_DATA')
pix2face_root = os.environ.get('PIX2FACE_SOURCE')

def centercrop(img, w=224, h=224, nrows=256):
    img.resize(nrows=nrows)
    xmin = round(0.5 * (img.width() - w));
    ymin = round(0.5 * (img.height() - h));
    xmax = xmin + w - 1;
    ymax = ymin + h - 1;
    try:
        img.crop([xmin, ymin, xmax, ymax])
        return img
    finally:
        return img


def preprocess_im(im, dilate=1.1, nrows=256, ncols=None):
    try:
        dil_box = im.bbox.dilate(dilate)
        bbox = bobo.geometry.BoundingBox(xmin=round(dil_box.xmin), ymin=round(dil_box.ymin),
                                         width=round(dil_box.width()), height=round(dil_box.height()))
        im.crop(bbox=dil_box).resize(cols=ncols, rows=nrows)
        return im
    except:
        print "could not crop image ", im.filename()
        return im

import janus.pvr.python_util.io_utils as io_utils
import janus.pvr.camera_decomposition as camera_decomposition
import janus.pvr.python_util.geometry_utils as geometry_utils

def guess_face_rect(img_shape):
    min_dim = int(np.min(img_shape[0:2]) * 0.9)
    wpad = (img_shape[1] - min_dim)/2
    hpad = (img_shape[0] - min_dim)/2
    return dlibnet.rectangle(wpad, hpad, wpad+min_dim, hpad+min_dim)

def face_rect_from_det(img_shape, det_rect):
    center_x = (det_rect.left + det_rect.right)/2
    center_y = (det_rect.top + det_rect.bottom)/2
    width = (det_rect.right - det_rect.left)
    height = (det_rect.bottom - det_rect.top)
    size = max(width,height)
    half_size = int(size*1.5 / 2)
    face_rect = dlibnet.rectangle(max(0, center_x - half_size), max(0, center_y - half_size),
                                  min(img_shape[1]-1,center_x + half_size), min(img_shape[0]-1,center_y+half_size))
    return face_rect


def create_jitter_cam(cam_og, yaw, pitch, roll):
    R0 = np.diag((1,-1,-1))
    R_head = geometry_utils.Euler_angles_to_matrix(yaw, pitch, roll, order='YXZ')
    R_cam = vxl.vgl_rotation_3d(np.dot(R0, R_head))
    rot_off = np.array((0,10,-50))
    T_off = np.dot(R_head, rot_off) - rot_off
    T_cam = np.array(cam_og.translation) + np.dot(R0, T_off)
    T_cam = vxl.vgl_vector_3d(T_cam)
    new_cam = face3d.perspective_camera_parameters(cam_og.focal_len, cam_og.principal_point, R_cam, T_cam, cam_og.nx, cam_og.ny)
    return new_cam


def encode_images(images):
    if len(images) == 0:
        return list(), np.zeros((0, 2048))
    chips = list()
    for img in images:
        dets = face_detector.detect(img)
        if len(dets) > 0:
            dets.sort(key=lambda x: -x.detection_confidence)
            face_rect = face_rect_from_det(img.shape, dets[0].rect)
        else:
            face_rect = guess_face_rect(img.shape)
            print('no faces')
        if face_rect is None:
            plt.figure()
            plt.imshow(img)
        chip = img[face_rect.top:face_rect.bottom, face_rect.left:face_rect.right, :]
        chips.append(chip)
    encodings = encoder.encode(chips)
    encodings /= np.linalg.norm(encodings, axis=1).reshape(-1, 1)
    return chips, encodings

def encode_template(T):
    media_list = []
    for im in T:
        img_list = [preprocess_im(im).rgb().data for f in im]
        current_enc = np.sum(encoder.encode(img_list), axis=0)
        current_enc /= np.linalg.norm(current_enc)
        media_list.append(current_enc)
    return np.array(media_list)


def encode_jitters(jitter_dic, pool_jitters=True, pool_media=True):
    encoding_dic = {k: [] for k in xrange(0, 3)}
    for key in xrange(0, 3):
        for media in jitter_dic[key]:
            curr_media_features = None
            for imset in media:
                if imset:
                    curr_chips, curr_enc = encode_images([im[:, :, 0:3] for im in imset])
                    if pool_jitters:
                        curr_enc = np.mean(curr_enc, axis=0)[np.newaxis, :]
                    if curr_media_features is None:
                        curr_media_features = curr_enc
                    else:
                        curr_media_features = np.vstack((curr_media_features, curr_enc))
            if pool_media and curr_media_features is not None:
                media_enc = np.mean(curr_media_features, axis=0)[np.newaxis, :]
                media_enc /= np.linalg.norm(media_enc, axis=1).reshape(-1, 1)
            elif curr_media_features is not None:
                media_enc = curr_media_features / np.linalg.norm(curr_media_features, axis=1).reshape(-1, 1)
            else:
                media_enc = None # no jitters per media
            encoding_dic[key].append(media_enc)
    return encoding_dic



def get_jitters_uniform(image, coeffs, jitterer, subject_components, expression_components, N=10):
    yaw_vals = np.linspace(-np.pi / 2, np.pi / 2, N)
    cam = coeffs.camera(0)
    R_im = np.dot(np.diag((1, -1, -1)), cam.rotation.as_matrix())
    yaw_im, pitch_im, roll_im = geometry_utils.matrix_to_Euler_angles(R_im, order='YXZ')


    new_cams = [create_jitter_cam(cam, yaw, pitch_im, roll_im) for yaw in yaw_vals]

    jitter_imgs = [jitterer.render_perspective(new_cam, coeffs.subject_coeffs(),
                                               coeffs.expression_coeffs(0),
                                               subject_components, expression_components) for new_cam in new_cams]

    return jitter_imgs

def retrain_and_test_with_jitters(id, jitter_dic, G, Gc, P, Pid, pool_probe_media=True, score_og=-1):

    GA_inds = np.where(Gc == id[1])[0]
    GB_inds = np.where(Gc == id[2])[0]

    P_inds = np.where(Pid == id[0])[0]

    P = P[P_inds, :]
    featuresA = list(G[GA_inds, :]); featuresB = list(G[GB_inds,:])

    features_probe = []

    jittered_probe_feat = np.vstack([m_enc for m_enc in jitter_dic[0]])
    print jittered_probe_feat.shape
    if pool_probe_media:
        jittered_probe_feat = np.mean(np.array(jittered_probe_feat), axis=0)[np.newaxis, :]
        jittered_probe_feat /= np.linalg.norm(jittered_probe_feat)
    test_probe = np.vstack((P, jittered_probe_feat))
    print test_probe.shape

    for m_encs in jitter_dic[1]:
        for enc in m_encs:
            featuresA.append(enc)
    for m_encs in jitter_dic[2]:
        for enc in m_encs:
            featuresB.append(enc)

    train_f = featuresA + featuresB
    train_l = [id[1]] * len(featuresA) + [id[2]] * len(featuresB)

    svc = LinearSVC(C=10, loss='squared_hinge', penalty='l2',
                    fit_intercept=True, verbose=False, dual=False,
                    class_weight='balanced',
                    tol=1e-2).fit(train_f, train_l)
    svm_tup = (svc.coef_.reshape(1, -1), svc.intercept_)
    if svc.classes_[0] == id[1]:  # svc -1 class is first
        svm_tup = (-1 * svc.coef_, -1 * svc.intercept_)
    score = np.dot(test_probe, svm_tup[0].T)
    score = np.mean(score)

    print "score changed from %.3f fot %.3f" % (score_og, score )

    print " classes are %s, %s and true class is %s" % (svc.classes_[0], svc.classes_[1], id[1])
    print "predictions are", svc.predict(test_probe.tolist())
    return score







def jitter_pair(id):

    jitter_dic = {0: [], 1: [], 2: []}
    if debug_dir is not None:
        curr_jitter_output_dir = os.path.join(debug_dir, '%s_%s_%s' % (id[0], id[1], id[2]))
        shutil.rmtree(curr_jitter_output_dir, ignore_errors=True)
        os.mkdir(curr_jitter_output_dir)

    for i in xrange(0, 3):
        template_id = id[i] if i == 0 else C2G[id[i]]
        for im in TMPL[template_id]:
            media_images = []
            for f in im:
                cs4id = uniq_cs4_id(f)
                coeff_path = os.path.join(coeff_dir, cs4id + '_coeffs.txt')
                if os.path.exists(coeff_path):
                    coeffs = face3d.subject_perspective_sighting_coefficients(coeff_path)
                    if coeffs.camera(0) is None:
                        print "sighting %s has no camera "% cs4id
                        continue;
                    nx, ny = coeffs.camera(0).nx, coeffs.camera(0).ny
                    print nx, ny
                    image = preprocess_im(f, nrows=512, ncols=None, dilate=1.5).rgb().data
                    image = io_utils.imread(os.path.join(chip_dir, cs4id + ".png"))

                    print cs4id, "shape is",  image.shape

                    jitterer = face3d.media_jitterer_perspective([image, ], coeffs,
                                                                 head_mesh, subject_components,
                                                                 expression_components, renderer, debug_dir)
                    jittered_images = get_jitters_uniform(image, coeffs, jitterer, subject_components, expression_components)
                    if debug_dir is not None:
                        for j in xrange(0, len(jittered_images)):
                            io_utils.imwrite(jittered_images[j], os.path.join(curr_jitter_output_dir,
                                                                     cs4id + "_%s.png" % j))
                    media_images.append(jittered_images)
                else:
                    print coeff_path, " does not exist!"
            jitter_dic[i].append(media_images)
    return jitter_dic

if __name__ == '__main__':


    cs4 = CS4(janus_data)
    gallery_templates = cs4._cs4_1N_gallery_S1() + cs4._cs4_1N_gallery_S2()
    probe_templates = cs4._cs4_1N_probe_mixed()
    C = 10; split = 'G_S1'
    protocol = 'P_mixed'
    debug_path = '/data/janus/debug/ovo/svms%s_%s.pk' % (C, split)
    debug_dir = os.path.dirname(debug_path)
    pvr_data_path = os.path.join(pix2face_root, 'data_3DMM')
    model_path = os.path.join(janus_root, 'models', 'dlib-dnn', 'resnet101_msceleb1m_14APR17.dlib')
    face_detector_path = os.path.join(janus_root, 'models', 'dlib', 'mmod_human_face_detector.dat')
    work_dir = os.path.join(janus_root, 'checkpoints', 'cs4', 'ovo_svm', 'failure_analysis')
    chip_dir = os.path.join(janus_data, 'Janus_CS4', 'CS4_chips', 'chips')
    coeff_dir = os.path.join(janus_data, 'Janus_CS4', 'CS4_chips', 'coeffs')

    # CS4 stuff
    C2G = {t.category(): t.templateid() for t in gallery_templates}
    T2subj = {t.templateid(): t.category() for t in gallery_templates + probe_templates}
    TMPL = {t.templateid(): t for t in gallery_templates + probe_templates}
    media_dic_path = os.path.join(janus_root, 'checkpoints', 'cs4', '%s_%s_%s_%s.pk' % ('resnet101_msceleb1m_14APR17', 'cs4', 'centercrop', 'Gmedia_Ptemplates'))

    with open(media_dic_path, 'rb') as media_file:
        print "Opening media from ", media_dic_path
        media_dic = dill.load(media_file)
        G, Gid, Gc = zip(*media_dic[split])
        G = np.array(G)
        Gc = np.array(Gc)
        P, Pid, Pc = zip(*media_dic[protocol])
        P = np.array(P)
        Pc = np.array(Pc)
        Pid = np.array(Pid)
        ovo_svms = dill.load(open(debug_path, 'rb'))
        ids = ovo_svms['id']
        scores = ovo_svms['scores']

        failure_inds = np.where(scores < 0)

        failure_ids = np.squeeze(ids[failure_inds, :])
        failure_scores = np.squeeze(scores[failure_inds])
        ranking = np.argsort(-failure_scores)

        # PVR stuff
        head_mesh = face3d.head_mesh(pvr_data_path)
        renderer = face3d.mesh_renderer()
        subject_components = np.load(os.path.join(pvr_data_path, 'pca_components_subject.npy'))
        expression_components = np.load(os.path.join(pvr_data_path, 'pca_components_expression.npy'))
        # dlib setup

        face_detector = dlibnet.mm_object_detector(face_detector_path)
        encoder = dlibnet.resnet101_encoder(model_path, 0, "centercrop", "")

        # experiment tests
        score_recomp = []
        for rank in ranking[2:5]:

            test_id = failure_ids[rank]
            print "==============Starting test_id %s ==================" % test_id
            test_score = failure_scores[rank]
            jitter_dic_out = jitter_pair(test_id)
            encodings = encode_jitters(jitter_dic_out, pool_media=False, pool_jitters=False)
            score = retrain_and_test_with_jitters(test_id, encodings, G, Gc, P, Pid, score_og=test_score)
            score_recomp.append(score)
