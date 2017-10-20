import gc
import os
import copy
import strpy.bobo.metrics
import strpy.bobo.util
import strpy.janus.gmm
import strpy.janus.features
from strpy.janus.features import densesift, densePCAsift, denseMultiscaleSIFT
import strpy.janus.encoding
from strpy.janus.encoding import fishervector, fishervector_pooling
import strpy.janus.reduction
import numpy as np
from strpy.bobo.classification import linearsvm
import strpy.bobo.app
from strpy.bobo.util import quietprint, seq, tolist, tempjpg, istuple, Stopwatch, writecsv
from strpy.bobo.linalg import vectorize
import sklearn.decomposition
#from pyspark.mllib.classification import SVMWithSGD
#from pyspark.mllib.regression import LabeledPoint
from itertools import product as cartesian
from itertools import combinations
import pdb
import math
from strpy.janus.cache import root as cacheDir
import ctypes
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression as LR
from sklearn.pipeline import Pipeline
from collections import defaultdict
import strpy.bobo.app
from strpy.bobo.geometry import sqdist
from itertools import product, combinations

# FIXME: DLIB should be optional
#import dlib
#from dlib import svm_c_trainer_linear, vector

import cv2


strpy.bobo.app.setverbosity(2)


# SGD helper function
def _sgd_localreduce(fModel):
    (W,V,b,L,E) = (0,0,0,0,0)
    ipaddr = ['10.1.10.147', '10.1.10.144', '10.1.10.142']
    for (k,(fW,fV,fB,fL,fE)) in enumerate(fModel):
        for j in range(1,len(ipaddr)):
            try:
                print '[tripletloss.train][%d/%d]: loading %s' % (k, len(fModel), fW)
                W += np.load(fW)
                V += np.load(fV)
                b += np.load(fB)
                L += np.load(fL)
                E += np.load(fE)
                break
            except:
                print '[tripletloss.train][%d/%d]: copying %s' % (k, len(fModel), fW)
                os.system('scp %s:%s %s' % (ipaddr[j], fW, fW))
                os.system('scp %s:%s %s' % (ipaddr[j], fV, fV))
                os.system('scp %s:%s %s' % (ipaddr[j], fB, fB))
                os.system('scp %s:%s %s' % (ipaddr[j], fL, fL))
                os.system('scp %s:%s %s' % (ipaddr[j], fE, fE))
                continue
    return (W,V,b,L,E)


class LinearSVMGalleryAdaptation():
    def __init__(self, f_encoding):
        self.f_encoding = f_encoding

    def train(self, sparkContext, trainset=None, galleryset=None, probeset=None, use_gallery_negatives=True,
              class_method='svm', n_partitions=16):
        (Tc, T) = trainset
        (Gid, Gc, G) = galleryset
        t_feat = sparkContext.broadcast(T)
        g_feat = sparkContext.broadcast(G)

        # HELPER: Train distributed one-vs-rest linear svm
        def _train_asmedia(subject, t_feat, t_lbl, g_feat, g_id, g_lbl, use_gallery_negatives, class_method):
            tid, lbl = subject
            # Construct pos-neg set according to whether we are including
            # gallery negatives or excluding other probes that may be false negatives
            feat_train, lbl_train = zip(*[(g,gc) for g, gid, gc in zip(g_feat.value, g_id, g_lbl) if (gid == tid or use_gallery_negatives)])
            if t_feat.value is not None:
                feat_train = np.vstack( (t_feat.value, feat_train) ).tolist()
                lbl_train = list(t_lbl) + list(lbl_train)
            else:
                feat_train = list(feat_train)
                lbl_train = list(lbl_train)

            y_train = np.int32([lbl == y for y in lbl_train]).flatten()
            # FIXME: Subclass rather than if-elif
            if class_method == 'lr':
                # Logistic regression only
                lr = LR().fit(feat_train, y_train)
                clf = lr
            elif class_method == 'svm-lr':
                # Platt-scaling manually
                svm = LinearSVC(C=1, fit_intercept=True, verbose=True, intercept_scaling=True).fit(feat_train, y_train)
                lr = LR().fit(svm.decision_function(feat_train).reshape((-1, 1)), y_train)
                clf = (svm, lr)
            elif class_method == 'svm-lr-pipe':
                # Platt-scaling pipeline
                svm = LinearSVC(C=1, fit_intercept=True, verbose=True, intercept_scaling=True)
                clf = Pipeline([('svc', svm), ('lr', LR())])
                clf = clf.fit(feat_train, y_train)
            elif class_method == 'svm':
                # non-calibrated SVM
                clf = LinearSVC(C=10, fit_intercept=True, verbose=True, intercept_scaling=True).fit(feat_train, y_train)
            elif class_method == 'svm-tne':
                clf = LinearSVC(C=10, loss='squared_hinge', penalty='l2', fit_intercept=False,
                                verbose=False,
                                dual=False, class_weight='balanced', tol=1e-2).fit(feat_train, y_train)
            elif class_method == 'dlib-svm_c_trainer_linear':
                labels = dlib.array()
                for y in y_train:
                    labels.append(1 if y > 0 else -1)
                samples = dlib.vectors()
                for feat in feat_train:
                    samples.append(dlib.vector(np.array(feat).tolist()))
                # Handle unbalanced positive and negative sample counts
                # Assumes num_negatives >> n_positives
                n_positives = np.count_nonzero(y_train)
                c1 = 1.0
                c2 = float(n_positives) / (len(y_train) - n_positives)
                trainer = svm_c_trainer_linear()
                trainer.c_class1 = c1
                trainer.c_class2 = c2
                clf = trainer.train(samples, labels)
            else:
                raise ValueError('Unknown classification method: %s' % class_method)
            return (tid, lbl, clf)


        # Train distributed one-vs-rest linear svm
        subjects = set(zip(Gid, Gc))
        f_train_asmedia = (lambda subject: _train_asmedia(subject,
                                                          t_feat=t_feat, t_lbl=Tc,
                                                          g_feat=g_feat, g_id=Gid, g_lbl=Gc,
                                                          use_gallery_negatives=use_gallery_negatives,
                                                          class_method=class_method))
        (tid, lbl, svm) = zip(*sparkContext.parallelize(subjects, n_partitions).map(f_train_asmedia).collect())

        return (tid, lbl, svm)

    def testsingle(self, probeset, galleryset, gallerysvms):
        (Gc, G) = galleryset
        (Pid, Pc, P) = probeset

        gX_test = P
        lbl_test = Pc
        gX_svm = gallerysvms


        # HELPER: Train distributed one-vs-rest linear svm
        def _test_asmedia(lbl, gX_svm, gX_test, lbl_test, TestTemplateID):
            svms = gX_svm
            svm = svms[lbl]

            yhat_test = vectorize(svm.decision_function(gX_test))

            y_test = np.float32([lbl == y for y in lbl_test]).flatten()  # columnwise

            Y_test = {k:0 for k in set(TestTemplateID)}
            Yhat_test = {k:0 for k in set(TestTemplateID)}
            N_test = {k:0 for k in set(TestTemplateID)}
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                N_test[tid] += 1
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                Y_test[tid] = y
                Yhat_test[tid] += float(yhat) / float(N_test[tid])

            return (Y_test.values(), Yhat_test.values(), lbl)

        subjects = set(Gc)
        (y, yhat, s) = zip(*[_test_asmedia(s, gX_svm, gX_test, lbl_test, Pid) for s in subjects])

        Y = np.array(y).transpose()  # svm evaluates probe x gallery columnwise, transpose to get back
        Yhat = np.array(yhat).transpose()

        return (Y, Yhat, len(subjects), s)

    def test(self, sparkContext, probeset, galleryset, gallerysvms=None, probesvms=None, n_partitions=8):
        quietprint('[janus.classifier.linearsvm.test]: Test')

        # HELPER: Test distributed one-vs-rest linear svm
        def _test_gallery_asmedia(lbl, gX_svms, gX_test, lbl_test, TestTemplateID):
            svm = gX_svms.value[lbl]
            y_test = np.float32([lbl == y for y in lbl_test]).flatten()  # columnwise
            if istuple(svm):
                # SVM+LR chain
                # FIXME: Update to test on mean scores if this works
                svc, lr = svm
                prob_pos = lr.predict_proba(svc.decision_function(gX_test.value).reshape((-1, 1)))[:, 1]
            elif hasattr(svm, "predict_proba"):
                prob_pos = svm.predict_proba(gX_test.value)[:, 1]
            elif type(svm) is dlib.dlib._decision_function_linear:
                prob_pos = [svm(dlib.vector(x.tolist())) for x in gX_test.value]
            else:
                prob_pos = svm.decision_function(gX_test.value)
            yhat_test = vectorize(prob_pos)

            Y_test = {k:0 for k in set(TestTemplateID)}
            Yhat_test = {k:0 for k in set(TestTemplateID)}
            N_test = {k:0 for k in set(TestTemplateID)}
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                N_test[tid] += 1
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                Y_test[tid] = y
                Yhat_test[tid] += float(yhat) / float(N_test[tid])

            return (Y_test.values(), Yhat_test.values(), [(pid, lbl) for pid in Y_test.keys()])

        # HELPER: Test distributed one-vs-rest linear svm
        def _test_probe_asmedia(s, gX_svms, lbl_test, TestTemplateID):
            lbl, G = s # one gallery template, mulitple features
            svms = gX_svms.value # dictionary of probe classifiers
            y_test = np.float32([lbl == y for y in lbl_test]).flatten()  # columnwise
            yhat_test = []
            for l in TestTemplateID:
                svm = svms[l]
                if istuple(svm):
                    # SVM+LR chain
                    # FIXME: Testing
                    svc, lr = svm
                    d_test = np.mean(svc.decision_function(G).reshape((-1, 1)))
                    prob_pos = lr.predict_proba(np.array([d_test]).reshape((-1, 1)))[:, 1]
                    prob_pos = np.mean(prob_pos) #FIXME: single value
                    # Old code
                    # svc, lr = svm
                    # prob_pos = lr.predict_proba(svc.decision_function(G).reshape((-1, 1)))[:, 1]
                    # prob_pos = np.mean(prob_pos)
                elif hasattr(svm, "predict_proba"):
                    prob_pos = svm.predict_proba(G)[:, 1]
                    prob_pos = np.mean(prob_pos)
                elif type(svm) is dlib.dlib._decision_function_linear:
                    prob_pos = np.mean([svm(dlib.vector(x.tolist())) for x in G])
                else:
                    prob_pos = svm.decision_function(G)
                    prob_pos = np.mean(prob_pos)

                yhat_test.append(prob_pos)

            Y_test = {k:0 for k in set(TestTemplateID)}
            Yhat_test = {k:0 for k in set(TestTemplateID)}
            N_test = {k:0 for k in set(TestTemplateID)}
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                N_test[tid] += 1
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                Y_test[tid] = y
                Yhat_test[tid] += float(yhat) / float(N_test[tid])

            return (Y_test.values(), Yhat_test.values(), [(pid, lbl) for pid in Y_test.keys()])


        # Begin testing
        (Gc, G) = galleryset
        (Pid, Pc, P) = probeset

        N_probe = len(set(Pid))
        N_gallery = len(set(Gc))

        Yhat_dic = None
        if gallerysvms is not None:
            quietprint('[janus.classifier.linearsvm.test]: Testing gallery svms')
            gX_svms = sparkContext.broadcast(gallerysvms)
            gX_test = sparkContext.broadcast(P)
            subjects = set(Gc)
            with Stopwatch() as sw:
                (y, yhat, tids) = zip(*sparkContext.parallelize(subjects, n_partitions).map(lambda s: _test_gallery_asmedia(s, gX_svms, gX_test, Pc, Pid)).collect())
            quietprint('[janus.classifier.linearsvm.test]: Gallery svm tests complete in %.1fs' % sw.elapsed)
            gX_svms.unpersist()
            gX_test.unpersist()
            Y_g = np.array(y).transpose() # svm evaluates probe x gallery columnwise, transpose to get back
            Yhat_g = np.array(yhat).transpose()
            TemplateIDpairs_g = np.array(tids).transpose()

            flat_ps_pairs = [tup for gal_row in tids for tup in gal_row ]
            flat_scores   = [tup for gal_row in yhat for tup in gal_row ]
            flat_truth    = [tup for gal_row in y for tup in gal_row ]
            Yhat_dic = {(p, s): (flat_scores[i], flat_truth[i]) for i, (p, s) in enumerate(flat_ps_pairs)}

        else:
            quietprint('[janus.classifier.linearsvm.test]: No gallery svm testing')
            Y_g = np.zeros((N_probe, N_gallery))
            Yhat_g = np.ones((N_probe, N_gallery))

        if probesvms is not None:
            quietprint('[janus.classifier.linearsvm.test]: Testing probe svms')
            gX_svms = sparkContext.broadcast(probesvms)
            subjects = defaultdict(list)
            for (c, f) in zip(Gc, G):
                subjects[c].append(f)
            with Stopwatch() as sw:
                (y, yhat, tids) = zip(*sparkContext.parallelize(dict(subjects).iteritems(), n_partitions).map(lambda s: _test_probe_asmedia(s, gX_svms, Pc, Pid)).collect())
            quietprint('[janus.classifier.linearsvm.test]: probe svm tests complete in %.1fs' % sw.elapsed)
            gX_svms.unpersist()
            Y_p = np.array(y).transpose()  # svm evaluates probe x gallery columnwise, transpose to get back
            Yhat_p = np.array(yhat).transpose()
            TemplateIDpairs_p = np.array(tids).transpose()

            flat_ps_pairs = [tup for gal_row in tids for tup in gal_row ]
            flat_scores =   [tup for gal_row in yhat for tup in gal_row ]
            flat_truth =    [tup for gal_row in y for tup in gal_row ]
            if Yhat_dic is not None:
              for i, (p,g) in enumerate(flat_ps_pairs):
                 Yhat_dic[(p,g)] = ((Yhat_dic[(p,g)][0] + flat_scores[i])/2, flat_truth[i])
            else:
                Yhat_dic = {(p, s): (flat_scores[i], flat_truth[i]) for i, (p, s) in enumerate(flat_ps_pairs)}
        else:
            quietprint('[janus.classifier.linearsvm.test]: No probe svm testing')
            Y_p = np.zeros((N_probe, N_gallery))
            Yhat_p = np.ones((N_probe, N_gallery))

        # FIXME: Niave avg of scores - should detect whether probabilities are being generated
#        if probesvms is not None and gallerysvms is not None:
        subjects = list(set(Gc))
        probe_tids = list(set(Pid))
        Y = np.zeros((N_probe,N_gallery))
        Yhat = np.zeros((N_probe,N_gallery))
        for i, probe_id in enumerate(probe_tids):
            for j, gallery_subject in enumerate(subjects):
                Yhat[i,j] = Yhat_dic[(probe_id,gallery_subject)][0]
                Y[i,j] = Yhat_dic[(probe_id,gallery_subject)][1]
        return (Y, Yhat, probe_tids, subjects)
        # this was bugged since Yhat_g and Yhat_p can't naively be averaged since
        # spark doesn't preserve the ordering of probe-gallery pairs. Commenting out
        # else:
        #     Y = Y_g  if np.any(Y_g) else Y_p
        #     Yhat = (Yhat_g + Yhat_p) / 2.0
        # return (Y, Yhat, Y.shape[1], TemplateIDpairs_p)

    def testprobegalleryadaptation(self, sparkContext, gallerysvms, probesvms, galleryset, probeset):
            (G_id, Gc, G) = galleryset
            (P_id, Pc, P) = probeset

            y = []
            yhat = []
            y_tup_dic = {}
            y_tup_list = []
            labels_list = []

            for g_tid in gallerysvms.keys():
                g_lbl, svm = gallerysvms[g_tid]
                yhat = svm.decision_function(P).flatten().tolist()
                labels_list += [(p_lbl, g_lbl) for p_lbl in Pc]
                y_tup_list += [(p_tid, g_tid) for p_tid in P_id]

                for i in range(0, len(yhat)):
                    p_tid = P_id[i]
                    y_tup_dic[(p_tid, g_tid)] = yhat[i]

            for p_tid in probesvms.keys():
                p_lbl, svm = probesvms[p_tid]
                yhat = svm.decision_function(G).flatten().tolist()
                # import pdb
                # pdb.set_trace()
                for i in range(0, len(yhat)):
                    g_tid = G_id[i]
                    y_tup_dic[(p_tid, g_tid)] = (y_tup_dic[(p_tid, g_tid)] + yhat[i])/2.0

            len_y = len(y_tup_list)
            y, yhat = [None] * len_y, [None] * len_y

            for i in range(0, len_y):
                y_tup = y_tup_list[i]
                labels_tup = labels_list[i]
                yhat[i] = y_tup_dic[y_tup]
                y[i] = int(labels_tup[0] == labels_tup[1])

            pg_pairs = y_tup_list
            y = np.array(y).reshape(len(G),len(P)).transpose()
            yhat = np.array(yhat).reshape(len(G),len(P)).transpose()
            return (y, yhat, pg_pairs)

    def train_and_test(self, sparkContext, trainset, probeset, galleryset):
        (Tc, T) = trainset
        (Gc, G) = galleryset
        (Pid, Pc, P) = probeset

        gX_test = sparkContext.broadcast(P)
        gX_train = sparkContext.broadcast(np.vstack( (T,G) ).tolist())
        lbl_train = Tc + Gc  # list of labels
        lbl_test = Pc

        # HELPER: Train distributed one-vs-rest linear svm
        def _train_and_test_asmedia(lbl, gX_train, lbl_train, gX_test, lbl_test, TestTemplateID):
            y_train = np.int32([lbl == y for y in lbl_train]).flatten()
            svm = LinearSVC(C=1, fit_intercept=True, verbose=True, intercept_scaling=True).fit(gX_train.value, y_train)
            yhat_test = vectorize(svm.decision_function(gX_test.value))

            y_test = np.float32([lbl == y for y in lbl_test]).flatten()  # columnwise

            Y_test = {k:0 for k in set(TestTemplateID)}
            Yhat_test = {k:0 for k in set(TestTemplateID)}
            N_test = {k:0 for k in set(TestTemplateID)}
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                N_test[tid] += 1
            for (yhat, y, tid) in zip(yhat_test, y_test, TestTemplateID):
                Y_test[tid] = y
                Yhat_test[tid] += float(yhat) / float(N_test[tid])

            return (Y_test.values(), Yhat_test.values(), lbl, svm)

        # Train distributed one-vs-rest linear svm
        subjects = set(Gc)
        (y, yhat, s, svm) = zip(*sparkContext.parallelize(subjects, 16).map(lambda s: _train_and_test_asmedia(s, gX_train, lbl_train, gX_test, lbl_test, Pid)).collect())

        Y = np.array(y).transpose()  # svm evaluates probe x gallery columnwise, transpose to get back
        Yhat = np.array(yhat).transpose()

        return (Y, Yhat, len(subjects), s, svm)


def est_b(y,yhat, old_b=0):
    """ estimate best bias b given a list of y and yhat

    If the yhat were computed with some previous value of b,
    pass that pass that as old_b
    """
    # zip, sort, unzip
    yhat, y = zip(*sorted(zip(yhat,y)))
    quietprint('[janus.classifier.est_b]: %s'%str(zip(yhat[::10],y[::10])))
    N = len(y)
    bestKeep = 0
    Ncorrect = sum(y)
    bestNcorrect = Ncorrect
    for i in xrange(N):
        if y[i] == 0:
            Ncorrect = Ncorrect + 1
            if Ncorrect > bestNcorrect:
                bestNcorrect = Ncorrect
                bestKeep = i+1
        else:
            Ncorrect = Ncorrect - 1
    if bestKeep == 0:
        y_thresh = yhat[0]-1
    elif bestKeep == N:
        y_thresh = yhat[-1]+1
    else:
        y_thresh = 0.5*(yhat[bestKeep] + yhat[bestKeep-1])
    return np.array(old_b - y_thresh)

class TripletLossMetric():
    def __init__(self, joint=False, dropconnect=False):
        self.W = None
        self.V = None
        self.b = None
        self.joint = joint
        self.dropconnect = dropconnect
        self.alpha = 1.0
        self.validation = []

    def initialized(self):
        return self.W is not None and self.V is not None and self.b is not None

    def model(self, W=None, V=None, b=None):
        self.W = W if W is not None else self.W
        self.V = V if V is not None else self.V
        self.b = b if b is not None else self.b
        return copy.deepcopy(self)

    def distance(self, x, y, z=None):
        if self.joint:
            d = 0.5*np.sum(np.square(self.W.dot(x-y)), axis=0) - np.sum(np.multiply(self.V.dot(x), self.V.dot(y)), axis=0)
        else:
            d = np.sum(np.square(self.W.dot(x-y)), axis=0)
        return float(d)  # FIXME b?

    def similarity(self, x, y, z=None):
        return -self.distance(x,y)

    def loss(self, x, y, z):
        if self.joint:
            if self.dropconnect:
                self._M = np.float32(np.random.rand(self.W.shape[0], self.W.shape[1]) >= 0.5)
                self._W = np.multiply(self._M, self.W)
                self._MV = np.float32(np.random.rand(self.V.shape[0], self.V.shape[1]) >= 0.5)
                self._V = np.multiply(self._MV, self.V)
            else:
                self._W = self.W
                self._V = self.V
            self._xmy = x-y  # cached
            self._xmz = x-z  # cached
            self._Wxy = self._W.dot(self._xmy)  # cached for sgd
            self._Wxz = self._W.dot(self._xmz)  # cached for sgd
            self._Vx  = self._V.dot(x)  # cached for sgd
            self._Vy  = self._V.dot(y)  # cached for sgd
            self._Vz  = self._V.dot(z)  # cached for sgd
            self._dpos = 0.5*np.sum(np.square(self._Wxy), axis=0) - np.sum(np.multiply(self._Vx, self._Vy), axis=0)
            self._dneg = 0.5*np.sum(np.square(self._Wxz), axis=0) - np.sum(np.multiply(self._Vy, self._Vz), axis=0)
        else:
            if self.dropconnect:
                self._M = np.float32(np.random.rand(self.W.shape[0], self.W.shape[1]) > 0.5)
                self._W = np.multiply(self._M, self.W)
            else:
                self._W = self.W
            self._xmy = x-y  # cached
            self._xmz = x-z  # cached
            self._Wxy = self._W.dot(self._xmy)  # cached for sgd
            self._Wxz = self._W.dot(self._xmz)  # cached for sgd
            self._dpos = np.sum(np.square(self._Wxy), axis=0)
            self._dneg = np.sum(np.square(self._Wxz), axis=0)
        self._loss = float(np.maximum(0, float(self.alpha - (self.b - (self._dpos - self._dneg)))))  # hinge loss
        return self._loss


    def gradient(self, x, y, z):
        Wxxt = np.outer(self._Wxy, self._xmy) - np.outer(self._Wxz, self._xmz)  # must call self.loss() first
        return Wxxt if not self.dropconnect else np.multiply(Wxxt, self._M)

    def sgd(self, x, y, z, gamma=0.25, gammaBias=10):
        #quietprint('[TripletLossMetric.sgd]: Stochastic gradient descent iteration ')
        #Wxxt = np.outer(self.W.dot(x-y), x-y) - np.outer(self.W.dot(x-z), x-z)
        if self.dropconnect:
            gammaWxxt = np.outer(gamma * self._Wxy, self._xmy) - np.outer(gamma * self._Wxz, self._xmz)  # must call self.loss() first
            self.W = self.W - np.multiply(self._M, gammaWxxt)
        else:
            gammaWxxt = np.outer(gamma * self._Wxy, self._xmy) - np.outer(gamma * self._Wxz, self._xmz)  # must call self.loss() first
            self.W = self.W - gammaWxxt
        if self.joint:
            if self.dropconnect:
                dV = 0.5*(-(np.outer(gamma*self._Vx, y) + np.outer(gamma*self._Vy, x)) + (np.outer(gamma*self._Vx, z) + np.outer(gamma*self._Vz, x)))
                self.V = self.V - np.multiply(dV, self._MV)
            else:
                self.V = self.V -  0.5*(-(np.outer(gamma*self._Vx, y) + np.outer(gamma*self._Vy, x)) + (np.outer(gamma*self._Vx, z) + np.outer(gamma*self._Vz, x)))
        #self.b = self.b + gammaBias
        return self


    def initial_conditions(self, X_pca, dimReduce=8, seed=int(42)):
        pca = sklearn.decomposition.RandomizedPCA(n_components=dimReduce, whiten=True, random_state=int(seed))
        quietprint('[TripletLossMetric.initial_conditions]: training initial projection, whitened PCA (%dx%d)->(%dx%d)' % (X_pca.shape[0], X_pca.shape[1], dimReduce, X_pca.shape[1]))
        W = pca.fit(X_pca).components_
        self.model(W, V=W, b=0)  # zero bias
        return self


    def train(self, features, numPartitions=4096, numEpochs=5, dimReduce=8, gamma=0.25, numInitialCond=1E4, seed=int(40), verbose=True, minibatch=1800, maxTriplets=1E6, alpha=1.0, valset=None):
        """Parallelized Stochastic Gradient Descent, NIPS'11"""
        """WARNING: featset requires 4-8x replication """

        # Parallelized stochastic gradient descent!
        quietprint('[TripletLossMetric.train]: Parallel SGD')
        self.alpha = 0.5*float(alpha) if self.dropconnect else alpha

        # Initial projection (whitened PCA of features)
        if not self.initialized():
            (c,X) = zip(*features)
            X_pca = np.array(X)[np.random.choice(len(features), min(int(numInitialCond), len(features)))]
            self = self.initial_conditions(X_pca, dimReduce=dimReduce)

        # SGD helper function
        def _sgd_minibatch(k_partition, k_iter, dModel, gFeatures, gamma, maxTriplets, minibatch, joint, dropconnect, verbose=False):
            model = TripletLossMetric(joint=joint, dropconnect=dropconnect).model(dModel['W'], dModel['V'], dModel['b'])

            # Minibatch stochastic gradient descent
            bobo.app.setverbosity(1)
            gk = [k for k in k_iter]  # global variable indexes of positive and negative features
            numMinibatch = int(np.floor(float(len(gk)) / max(float(minibatch), 1.0)))
            (numLoss, cumLoss) = (0.0, 0.0)
            for m in range(numMinibatch):
                quietprint('[TripletLossMetric.train][%d/%d]: Triplet selection' % (m, numMinibatch))
                gk_minibatch = gk[m*minibatch:m*minibatch+minibatch]  # minibatch index

                # Minibatch features
                #if type(gFeatures.value[0][1]) is str:
                #    X = np.array([np.load(gFeatures.value[k][1]).tolist() for k in gk_minibatch])  # features are stored in .npy files to be loaded here
                #else:
                X = np.array([gFeatures.value[k][1].ravel().tolist() for k in gk_minibatch])  # features are stored in global variable

                Wx = np.array([model.W.dot(x).ravel() for x in X])  # premultiply all features
                Tc = [gFeatures.value[k][0] for k in gk_minibatch]  # class labels for all features

                if self.joint:
                    D = sqdist(Wx,Wx)  # pairwise distance
                    Vx = np.array([model.V.dot(x).ravel() for x in X])  # premultiply features
                    D = 0.5*D - Vx.dot(Vx.transpose())
                else:
                    D = sqdist(Wx,Wx)  # pairwise distance
                Y = np.array([p==q for (p,q) in product(Tc,Tc)]).reshape(D.shape)  # ground truth labels

                # Triplet selection
                n_negperpos = 1 # randomly select one semi-hard negative for each mated pair in minibatch
                n_pospairs = 0
                triplets = []
                for i in range(len(gk_minibatch)):
                    J = np.argwhere(Y[i,:] == True).ravel()  # anchor mates
                    K = np.argwhere(Y[i,:] == False).ravel() # anchor non-mates
                    np.random.shuffle(K)  # randomly select hard negatives
                    for j in J:  # all anchor mates
                        n_pospairs = n_pospairs + 1
                        k_negperpos = 0
                        for k in K:  # all anchor non-mates
                            if (i!=j) and (D[i,k] - D[i,j]) < self.alpha:  # margin violating hard triplet ("semi-hard")
                                triplets.append( (i,j,k) )
                                k_negperpos += 1
                            if k_negperpos == n_negperpos:
                                break  # max negatives per positive
                        #if k_negperpos < n_negperpos:  # not enough semi-hard
                        #    for k in K:
                        #        if (i!=j) and (D[i,k] - D[i,j]) >= self.alpha:  # random non-margin violating triplet
                        #            triplets.append( (i,j,k) )
                        #            k_negperpos += 1
                        #        if k_negperpos == n_negperpos:
                        #            break  # max negatives per positive

                    if len(triplets) > maxTriplets:
                        break

                # Retrain
                quietprint('[TripletLossMetric.train][%d/%d]: gradient update, %d triplets' % (m, numMinibatch, len(triplets)))
                (grad, numGrad) = (0, 0)
                for (n, (i,j,k)) in enumerate(triplets):
                    (x,y,z) = (X[i,:], X[j,:], X[k,:])
                    if model.loss(x,y,z) > 0:
                        #grad = grad + model.gradient(x, y, z)  # gradient accumulator (FIXME: joint)
                        model = model.sgd(x,y,z,gamma)
                        #numGrad += 1  # gradient counter
                        cumLoss += model._loss  # cumulative loss
                    numLoss += 1

                # Minibatch update
                #model.W = model.W - (float(gamma)/max(float(numGrad),1.0))*grad  # FIXME: non-joint
                print '[TripletLossMetric.train][%d/%d]: mean loss = %f' % (m, numMinibatch, float(cumLoss)/max(float(numLoss), 1.0))

            # Save
            outfiles = [os.path.join('/data/vision/janus/tripletloss/', 'tripletloss_%s_%s_%d.npy' % (v, bobo.util.timestamp(), k_partition)) for v in ['W','V','b']]  # filenames
            [np.save(f,v) for (f,v) in zip(outfiles, [model.W, model.V, model.b])]  # save model in NFS
            yield tuple(outfiles)


        # SGD helper function
        def _sgd_nfsreduce(fModel, joint=False):
            (W,V,b) = (0,0,0)
            print '[tripletloss.train]: loading and averaging models'
            for (k,(fW,fV,fB)) in enumerate(fModel):
                #print '[tripletloss.train][%d/%d]: loading' % (k, len(fModel))
                if joint:
                    (W,V,b) = (W+np.load(fW), V+np.load(fV), b+np.load(fB))
                else:
                    (W,b) = (W+np.load(fW), b+np.load(fB))
            return (W,V,b)

        # Epochs
        dModel = {'W':self.W, 'V':self.V, 'b':self.b}  # initial model
        for n in range(0, int(numEpochs)):
            # Training
            print '[tripletloss.train][%d/%d]: training epoch' % (n+1, int(numEpochs))
            sc = bobo.app.init(appName='tripletloss_training')  # allocate spark
            gFeatures = sc.broadcast(features)
            gk = np.random.choice(range(len(features)), numPartitions*len(features)).tolist() # random subsets of data for each partition
            fModel = (sc.parallelize(gk, numPartitions)
                        .mapPartitionsWithIndex(lambda k, gk_iter: _sgd_minibatch(k, gk_iter, dModel, gFeatures, gamma, maxTriplets, minibatch, self.joint, self.dropconnect, verbose=verbose), preservesPartitioning=True)  # SGD per partition
                        .collect())
            (gFeatures.unpersist(), sc.stop())  # free spark
            dModel = {k:v/float(numPartitions) for (k,v) in zip(['W','V','b'], _sgd_nfsreduce(fModel, self.joint))}  # mean over partitions
            self.model(dModel['W'], dModel['V'], dModel['b'])
            bobo.util.save(self, 'metric.pk')

            # Validation
            if valset is not None:
                (Gid, Gc, Gx, Pid, Pc, Px) = valset
                sc = bobo.app.init('tripletloss_validation')
                gMetric = sc.broadcast(self.model())
                X = sc.parallelize(zip(Pid,Pc,Px), 128).cartesian(sc.parallelize(zip(Gid,Gc,Gx), numPartitions)).map(lambda ((pid,pc,px),(gid,gc,gx)): (pid, gid, pc==gc, gMetric.value.similarity(px,gx)), preservesPartitioning=True).collect()
                (pid, gid, y, yhat) = zip(*sorted(X, key=lambda x: str(x[0])+str(x[1])))  # probe ID order
                self.validation.append(janus.metrics.report(np.array(y), np.array(yhat), N_gallery=len(Gc), verbose=True))
                sc.stop()

        # Save
        #self.model(dModel['W'], dModel['V'], dModel['b'])
        return self

class DiscriminativeDimensionalityReduction():
    def __init__(self, seed=None, do_jointmetric=False):
        self.model = None
        self.models = {}
        #self.f_unary = f_unary
        self.seed = seed
        self.do_jointmetric = do_jointmetric


    def update(self, trainset, numIterations=1E6, gamma=0.25, gammaBias=10, categoryVsRest=None):
        """Assume that metric has been trained, and we wish to update the metric to a new (local) training set of a list of tuples of (category, feature) pairs"""
        quietprint('[janus.classifier.ddr.update]: updating trained model')
        do_pospair = True;  n = 0;
        np.random.shuffle(trainset)  # random shuffle to get positive pairs not in order
        num_updates = 0
        while n < numIterations:
            for (i, (cp, p)) in enumerate(trainset):
                for (j, (cq, q)) in enumerate(trainset):
                    if (j<=i) or (do_pospair and (cp != cq)) or (not do_pospair and (cp == cq)):
                        continue  # skip until found next positive or negative combination
                    elif categoryVsRest not in [None, cp, cq]:
                        continue # skip until target category is in the training pair
                    else:
                        b_prev = self.model['b']
                        (self.model['W'], self.model['b'], self.model['V']) = self._sgd_iteration(np.array(p).flatten(), np.array(q).flatten(), (+1.0 if (cp==cq) else -1.0), self.model['W'], self.model['b'], self.model['V'], gamma, gammaBias)
                        if self.model['b'] != b_prev:
                            num_updates += 1
                        do_pospair = True if do_pospair==False else False  # toggle positive/negative pair updates
                        n = n + 1
                        if (n % 100) == 0:
                            quietprint('[janus.classifier.ddr.update][%d/%d]: warm start iteration' % (n, numIterations))
                        break  # move on to next (cp, p)

            if (categoryVsRest is not None) and (i == j == len(trainset)-1) and (n == 0):
                quietprint('[janus.classifier.ddr.update]: Category [%s] has no positive pairs, aborting update.' % categoryVsRest)
                break

            np.random.shuffle(trainset)  # random shuffle to get new negative pairs
        quietprint('[janus.classifier.ddr.update]: Performed %d updates in %d iterations' % (num_updates, n), 2)
        return self


    def train(self, trainset, f_unary=None, dimReduce=128, gamma=0.25, gammaBias=10, numPca=1E3, numBiasTrain=1E2, numIterations=1E6, pairs=None):
        """
        TRAIN
        """
        if self.do_jointmetric:
            quietprint('[janus.classifier.ddr.train]: training joint discriminative dimensionality reduction')
        else:
            quietprint('[janus.classifier.ddr.train]: training discriminative dimensionality reduction')

        # Parallelized feature extraction
        if f_unary is None:
            (labels, X) = zip(*trainset.collect())
        else:
            (labels, X) = zip(*trainset.map(lambda x: (x.category(), f_unary(x).flatten())).collect()) # bring back features to the driver for all pairs training
        X = np.array(X)

        # Training pairs
        K_pospairs = []; K_negpairs = []
        if pairs is None:
            for (i, (p_category, p)) in enumerate(zip(labels,X)):
                for (j, (q_category, q)) in enumerate(zip(labels,X)):
                    if (j > i) and (p_category == q_category):
                        K_pospairs.append( (i,j) )
                    elif (j > i):
                        K_negpairs.append( (i,j) )
        else:
            K_pospairs = pairs.filter(lambda (i,j,y): y==1).map(lambda (i,j,y): (i,j)).collect()
            K_negpairs = pairs.filter(lambda (i,j,y): y==0).map(lambda (i,j,y): (i,j)).collect()
        K_pospairs = np.array(K_pospairs)
        K_negpairs = np.array(K_negpairs)


        # Initial projection
        f = lambda x, K_pairs: int(np.floor(float(x)/(numPca + numBiasTrain)*K_pairs.shape[0]))

        quietprint('%i %i %s %s'%(numPca, numBiasTrain, str(K_pospairs.shape), str(K_negpairs.shape)))
        N_pospairs_pca, N_pospairs_bias = (f(numPca, K_pospairs), f(numBiasTrain,K_pospairs)) if numPca + numBiasTrain > K_pospairs.shape[0] \
                else (numPca, numBiasTrain)
        N_negpairs_pca, N_negpairs_bias = (f(numPca,K_negpairs), f(numBiasTrain, K_negpairs)) if numPca + numBiasTrain > K_negpairs.shape[0] \
                else (numPca, numBiasTrain)
        quietprint('%s %s :: %s %s'%(str(N_pospairs_pca), str(N_pospairs_bias), str(N_negpairs_pca), str(N_negpairs_bias)))
        K_pospairs_pca = K_pospairs[0:N_pospairs_pca, :]
        K_negpairs_pca = K_negpairs[0:N_negpairs_pca, :]
        X_posleft = np.array(X[K_pospairs_pca[:,0],:])
        X_posright = np.array(X[K_pospairs_pca[:,1],:])
        X_posdiff = (X_posleft - X_posright)
        X_negleft = np.array(X[K_negpairs_pca[:,0],:])
        X_negright = np.array(X[K_negpairs_pca[:,1],:])
        X_negdiff = (X_negleft - X_negright)
        #X_pca = np.concatenate( (X_posdiff, X_negdiff) )  # PCAW on fisher vector difference
        X_pca = np.concatenate( (X_posleft, X_posright, X_negleft, X_negright) )  # PCAW on original fisher vectors
        pca = sklearn.decomposition.RandomizedPCA(n_components=dimReduce, whiten=True, random_state=self.seed)
        quietprint('[janus.classifier.ddr.train]: training initial projection, whitened PCA (%dx%d) ' % (X_pca.shape[0], X_pca.shape[1]))
        W = pca.fit(X_pca).components_;
        X_pca=None;  K_pospairs_pca=None; K_negpairs_pca=None; pca=None;  # memory cleanup
        V = W if self.do_jointmetric else None

        # Initial threshold
        quietprint('[janus.classifier.ddr.train]: training initial threshold')
        if V is not None:
            dpos = 0.5*np.sum(np.square(W.dot(X_posdiff.transpose())), axis=0) - np.sum(np.multiply(V.dot(X_posleft.transpose()), V.dot(X_posright.transpose())), axis=0)
            dneg = 0.5*np.sum(np.square(W.dot(X_negdiff.transpose())), axis=0) - np.sum(np.multiply(V.dot(X_negleft.transpose()), V.dot(X_negright.transpose())), axis=0)
        else:
            dpos = np.sum(np.square(W.dot(X_posdiff.transpose())), axis=0)
            dneg = np.sum(np.square(W.dot(X_negdiff.transpose())), axis=0)
        y = np.concatenate( (np.ones( (N_pospairs_pca, 1) ), np.zeros( (N_negpairs_pca, 1) ) ))
        yhat = np.concatenate( (-dpos, -dneg), axis=1).reshape( (len(y),1) )
        b = -yhat[np.argmax([np.mean(np.float32(np.float32(yhat>t)==y)) for t in yhat])]


        # Training using all pairs (balanced)
        k_idxpos = 0; k_idxneg = 0;
        for n in range(0, int(numIterations)):
            # Alternate positive/negative pairs
            if (n % 2) == 0:
                (i, j) = (K_pospairs[k_idxpos % K_pospairs.shape[0], 0], K_pospairs[k_idxpos % K_pospairs.shape[0], 1])
                (p, q, y) = (X[i,:], X[j,:], +1.0)
                k_idxpos += 1
            else:
                #k_idxneg = k_idxpos  # FIXME: THIS IS A BUG IN THE MATLAB CODE
                (i, j) = (K_negpairs[k_idxneg % K_negpairs.shape[0], 0], K_negpairs[k_idxneg % K_negpairs.shape[0], 1])
                (p, q, y) = (X[i,:], X[j,:], -1.0)
                k_idxneg += 1

            # Stochastic gradient descent
            (W,b,V) = self._sgd_iteration(p,q,y,W,b,V,gamma,gammaBias)
            if (n % np.floor(numIterations/10.0)) == 0:
                quietprint('[janus.classifier.ddr.train][%d/%d]: stochastic gradient descent' % (n,numIterations), 1)
                self.models[n] = {'W':W.copy(), 'V':V.copy(), 'b':b.copy()}


        # Save me
        self.model = {'W':W, 'V':V, 'b':b}
        return self


    def initial_conditions(self, X, K_pospairs, K_negpairs, numPca, dimReduce):
        # Initial projection
        n_pos = int(np.minimum(numPca, K_pospairs.shape[0]))
        n_neg = int(np.minimum(numPca, K_negpairs.shape[0]))
        K_pospairs_pca = K_pospairs[0:n_pos, :]
        K_negpairs_pca = K_negpairs[0:n_neg, :]
        X_posleft = np.array(X[K_pospairs_pca[:,0],:])
        X_posright = np.array(X[K_pospairs_pca[:,1],:])
        X_posdiff = (X_posleft - X_posright)
        X_negleft = np.array(X[K_negpairs_pca[:,0],:])
        X_negright = np.array(X[K_negpairs_pca[:,1],:])
        X_negdiff = (X_negleft - X_negright)
        X_pca = np.concatenate( (X_posleft, X_posright, X_negleft, X_negright) )  # PCAW on original fisher vectors
        pca = sklearn.decomposition.RandomizedPCA(n_components=dimReduce, whiten=True, random_state=self.seed)
        quietprint('[janus.classifier.ddr.train]: training initial projection, whitened PCA (%dx%d) ' % (X_pca.shape[0], X_pca.shape[1]))
        W = pca.fit(X_pca).components_;
        X_pca=None;  K_pospairs_pca=None; K_negpairs_pca=None; pca=None;  # memory cleanup
        V = W if self.do_jointmetric else None

        # Initial threshold
        quietprint('[janus.classifier.ddr.train]: training initial threshold')
        if V is not None:
            dpos = 0.5*np.sum(np.square(W.dot(X_posdiff.transpose())), axis=0) - np.sum(np.multiply(V.dot(X_posleft.transpose()), V.dot(X_posright.transpose())), axis=0)
            dneg = 0.5*np.sum(np.square(W.dot(X_negdiff.transpose())), axis=0) - np.sum(np.multiply(V.dot(X_negleft.transpose()), V.dot(X_negright.transpose())), axis=0)
        else:
            dpos = np.sum(np.square(W.dot(X_posdiff.transpose())), axis=0)
            dneg = np.sum(np.square(W.dot(X_negdiff.transpose())), axis=0)
        y = np.concatenate( (np.ones( (n_pos, 1) ), np.zeros( (n_neg, 1) ) ))
        yhat = np.concatenate( (-dpos, -dneg), axis=1).reshape( (len(y),1) )
        b = -yhat[np.argmax([np.mean(np.float32(np.float32(yhat>t)==y)) for t in yhat])]
        return (W,b,V)


    def _sgd_iteration(self, p,q,y, W,b,V, gamma=0.25, gammaBias=10):
        """Function to compute a single iteration of stochastic gradient descent for feature vectors p and q with label y \in {-1,1} given current learned metric parameters (W,b,V)"""

        # Iterative update
        p = p.reshape( (len(p), 1) ) # column vector
        q = q.reshape( (len(q), 1) )  # column vector
        x = (p-q)  # column vector
        Wx = W.dot(x)  # px1
        normsq_Wp_minus_Wq = np.sum(np.square(Wx))  # 1x1
        if V is not None:
            Vp = V.dot(p)  # px1
            Vq = V.dot(q)  # px1
            pVVq = Vp.transpose().dot(Vq) # 1x1
            score = 0.5*normsq_Wp_minus_Wq - pVVq
        else:
            score = normsq_Wp_minus_Wq

        # Stochastic gradient descent iteration
        if ((score > (b - 1)) and (y == 1)) or ((score < (b + 1)) and (y == -1)):
            Wxxt = Wx.dot(x.transpose()) # px1 * 1xn
            W = W - (y*gamma*Wxxt)
            b = b + y*gammaBias
            if V is not None:
                V = V + (y*gamma*Vp).dot(q.transpose()) + (y*gamma*Vq).dot(p.transpose())
        return (W,b,V)


    def train_parallel(self, trainset, dimReduce=128, gamma=0.25, gammaBias=10, numBiasTrain=1E3, numIterations=1E6, seed=42, numBatches=1E2):
        """Parallelized Stochastic Gradient Descent, NIPS'11"""
        quietprint('[janus.classifier.ddr.train]: Parallel SGD training joint discriminative dimensionality reduction')

        # Function to compute SGD over an iteratable of (label,f) pairs for a single partition, returning iterable
        def _f_sgd(X_iter, k_partition, W, b, V, numIterations, iteration=0):

            # Data: [(label,x), (label,x), ...]
            (labels, X) = zip(*X_iter)
            X = np.array(X).squeeze()

            # Pairs index
            K = np.array([(i,j,p==q) for ((i,p), (j,q)) in combinations(zip(xrange(len(labels)), labels), 2)])
            K_pospairs = K[np.argwhere(K[:,2] == 1).flatten(), 0:2]
            K_negpairs = K[np.argwhere(K[:,2] == 0).flatten(), 0:2]

            # Stochastic gradient descent over balanced pairs
            k_idxpos = int(iteration*numIterations); k_idxneg=k_idxpos;
            for n in range(0, int(numIterations)):
                # Alternate positive/negative pairs
                if (n % 2) == 0:
                    (i, j) = (K_pospairs[k_idxpos % K_pospairs.shape[0], 0], K_pospairs[k_idxpos % K_pospairs.shape[0], 1])
                    (p, q, y) = (X[i,:], X[j,:], +1.0)
                    k_idxpos += 1
                else:
                    #k_idxneg = k_idxpos  # FIXME: THIS IS A BUG IN THE MATLAB CODE
                    (i, j) = (K_negpairs[k_idxneg % K_negpairs.shape[0], 0], K_negpairs[k_idxneg % K_negpairs.shape[0], 1])
                    (p, q, y) = (X[i,:], X[j,:], -1.0)
                    k_idxneg += 1

                # Stochastic gradient descent
                (W,b,V) = self._sgd_iteration(p,q,y,W,b,V,gamma, gammaBias)

                if (n % np.floor(numIterations/10.0)) == 0:
                    quietprint('[janus.classifier.ddr.train][%d/%d][%d][%s/%s]: stochastic gradient descent' % (n,numIterations, k_partition, labels[i], labels[j]))

            yield (W,b,V)

        # Initial condition
        quietprint('[janus.classifier.ddr.train]: Parallel SGD training initial conditions')
        biasset = trainset.takeSample(withReplacement=False, num=int(5*numBiasTrain), seed=seed)  # HACK: take large sample to guarantee enough pos pairs
        (labels, X) = zip(*biasset)
        X = np.array(X).squeeze()
        K = np.array([(i,j,p==q) for ((i,p), (j,q)) in combinations(zip(xrange(len(labels)), labels), 2)])
        K_pospairs = K[np.argwhere(K[:,2] == 1).flatten(), 0:2]
        K_negpairs = K[np.argwhere(K[:,2] == 0).flatten(), 0:2]
        (W,b,V) = self.initial_conditions(X, K_pospairs, K_negpairs, numBiasTrain, dimReduce)
        model = {'W':W, 'b':b, 'V':V}    # initial conditions

        # Parallelized stochastic gradient descent!
        quietprint('[janus.classifier.ddr.train]: Parallel SGD training')
        #N = trainset.getNumPartitions()
        N = 32;  # FIXME: '!!!FORCED N=32!!!'
        categories = trainset.map(lambda (label,x): label).distinct().collect()
        partition_to_label = [(k,categories[k%len(categories)]) for k in range(0,N)]  # assign each partition at least one label
        numIterationsPerBatch = int(np.floor(float(numIterations)/float(N*numBatches)))
        trainset = (trainset.flatMap(lambda (label,x): [(p, (label,x)) for (p,lbl) in partition_to_label if lbl==label] + [(hash(str((x).data))%N, (label,x)), (hash(str((x*2).data))%N, (label,x)), (hash(str((x*4).data))%N, (label,x))])  # Increase size of training set for overlap
                            .partitionBy(N, lambda key: key)   # Assign class to fixed partition by key, assign copies to other partitions uniformly at random
                            .map(lambda (k, (label,x)): (label,x))   # Remove partition index
                            .cache())  # cache to avoid repartitioning
        for n in range(0, int(numBatches)):
            quietprint('[janus.classifier.ddr.train]: Batch %d/%d' % (n+1,numBatches))
            gModel = trainset.context.broadcast(model)  # global variables for model
            model = (trainset.mapPartitionsWithIndex(lambda k,X_iter: _f_sgd(X_iter, k, gModel.value['W'], gModel.value['b'], gModel.value['V'], numIterations=numIterationsPerBatch, iteration=n))  # independent batch SGD updates in partition
                             .flatMap(lambda (W,b,V): [('W',W), ('b',b), ('V',V)])  # (W,b,V) tuples to RDD of ('W',W),('V',V),('b',b) key-value pairs
                             .reduceByKey(lambda a,b: a+b if (a != None and b != None) else None)  # sum up W,b,V separately
                             .map(lambda (k,v): (k, v/float(N) if v != None else None))  # expectation
                             .collectAsMap())  # return dictionary {'W':W, 'V':V, 'b':b}
        trainset = trainset.unpersist()

        # Save me
        self.model = model
        return self


    def test(self, probeset, galleryset, f_unary):
        quietprint('[janus.classifier.ddr.test]: testing discriminative dimensionality reduction')

        (P_label, P, Pid) = zip(*probeset.map(lambda im: (im.category(), f_unary(im).flatten(), im.templateid())).collect())
        (G_label, G, Gid) = zip(*galleryset.map(lambda im: (im.category(), f_unary(im).flatten(), im.templateid())).collect())

        if self.do_jointmetric:
            W = self.model['W']
            V = self.model['V']
            b = self.model['b']
            yhat = []
            for (p,g) in cartesian(P,G):
                p = p.reshape( (len(p),1) ) # column vector
                g = g.reshape( (len(g),1) ) # column vector
                dist = 0.5 * float(np.sum(np.square(W.dot(p-g)))) - float(np.sum(np.multiply(V.dot(p), V.dot(g))))
                yhat.append(float(b - dist))
        else:
            W = self.model['W']
            b = self.model['b']
            yhat = [float(b-float(np.sum(np.square(W.dot(p.reshape( (len(p),1) ) - g.reshape( (len(g),1) )))))) for (p,g) in cartesian(P,G)]

        y = [float(p==g) for (p,g) in cartesian(P_label,G_label)]
        tid = [(pid,gid) for (pid,gid) in cartesian(Pid,Gid)]      # template ID pairs

        return (y, yhat, tid)

    def test_flattened(self, probeset, galleryset):
        quietprint('[janus.classifier.ddr.test]: testing discriminative dimensionality reduction')
        # Gallery and probesets are lists of (templateid, category, feature) tuples
        (Pid, P_label, P) = zip(*probeset)
        (Gid, G_label, G) = zip(*galleryset)

        if self.do_jointmetric:
            W = self.model['W']
            V = self.model['V']
            b = self.model['b']
            yhat = []
            for (p,g) in cartesian(P,G):
                p = p.reshape( (len(p),1) ) # column vector
                g = g.reshape( (len(g),1) ) # column vector
                dist = 0.5 * float(np.sum(np.square(W.dot(p-g)))) - float(np.sum(np.multiply(V.dot(p), V.dot(g))))
                yhat.append(float(b - dist))
        else:
            W = self.model['W']
            b = self.model['b']
            yhat = [float(b-float(np.sum(np.square(W.dot(p.reshape( (len(p),1) ) - g.reshape( (len(g),1) )))))) for (p,g) in cartesian(P,G)]

        y = [float(p==g) for (p,g) in cartesian(P_label,G_label)]
        pgid = [(pid,gid) for (pid,gid) in cartesian(Pid,Gid)]      # template ID pairs
        pglbl = [(plbl,glbl) for (plbl,glbl) in cartesian(P_label,G_label)]      # label pairs
        info = {'templateIDpairs':pgid, 'labelpairs':pglbl}
        return (y, yhat, info)


    def similarity(self, x, y):
        """Return the scalar similarity between fisher vectors x and y using the learned metric"""
        if self.do_jointmetric:
            W = self.model['W']
            V = self.model['V']
            b = self.model['b']
            p = x.reshape( (len(x.flatten()),1) ) # column vector
            g = y.reshape( (len(y.flatten()),1) ) # column vector
            s = float(b - 0.5 * float(np.sum(np.square(W.dot(p-g)))) - float(np.sum(np.multiply(V.dot(p), V.dot(g)))))
        else:
            W = self.model['W']
            b = self.model['b']
            p = x.reshape( (len(x.flatten()),1) ) # column vector
            g = y.reshape( (len(y.flatten()),1) ) # column vector
            s = float(b-float(np.sum(np.square(W.dot(p - g)))))
        return s



    def projection(self, x):
        """Return the projection y=W*x for fisher vector x"""
        if self.do_jointmetric:
            W = self.model['W']
            V = self.model['V']
            b = self.model['b']
            return W.dot(x.flatten())
        else:
            W = self.model['W']
            b = self.model['b']
            return W.dot(x.flatten())

    def train_bias(self, encodedset, pairs):
        """Re-train the bias on a given trainset (RDD of (label, encoding) pairs) and given pairs"""
        quietprint('[janus.classifier.ddr.train_bias]: training bias on %i pairs'%pairs.count())
        # Parallelized feature extraction
        (labels, X) = zip(*encodedset.collect()) # bring back features to the driver for all pairs training
        sc = encodedset.context
        X = sc.broadcast(np.array(X))

        try:
            pairs.count()
        except:
            pairs = encodedset.context.parallelize(pairs)

        W = sc.broadcast(self.model['W'])
        V = sc.broadcast(self.model['V'])
        if self.do_jointmetric and V.value is not None:
            f_metric_unbiased = lambda p,q: -(0.5*np.sum(np.square(W.value.dot(p)-W.value.dot(q))) - (V.value.dot(p)).dot(V.value.dot(q)))
        else:
            f_metric_unbiased = lambda p,q: -(0.5*np.sum(np.square(W.value.dot(p)-W.value.dot(q))))
        quietprint('%s %s'%(str(X.value.shape), str(pairs.take(5))))
        y = pairs.map(lambda (i,j,y): y).collect()
        yhat = pairs.map(lambda (i,j,y): f_metric_unbiased(X.value[i,:], X.value[j,:])).collect()

        b = est_b(y,yhat)
        quietprint('[janus.classifier.ddr.train_bias]: updated bias old: %f new: %f'%(float(self.model['b']),float(b)))
        self.model['old_b'] = self.model['b']
        self.model['b'] = b
        return self

class RankingSVM():
    def __init__(self, rng=np.random.RandomState()):
        self.model = None
        #self.f_unary = f_unary
        #self.f_pairwise = f_pairwise
        self.rng = rng

    def train(self, trainset, f_unary, svmLambda=1E-8, numIterations=1E6):
        """ One vs. rest structured SVM for ranking same vs. different classifier """
        quietprint('[janus.classifier.ranking.train]: training ranking classifier')

        # Feature extraction to construct data matrix
        quietprint('[janus.classifier.ranking.train]: feature extraction...')
        labels = trainset.map(lambda x: x.category()).collect()
        X = trainset.map(lambda x: f_unary(x)).collect()  # feature extraction and coding

        # Same/different pair indexes
        K_same = []; K_diff = []
        for (i, (p_category, p)) in enumerate(zip(labels,X)):
            for (j, (q_category, q)) in enumerate(zip(labels,X)):
                if (j > i) and (p_category == q_category):
                    K_same.append( (i,j) )
                elif (j > i):
                    K_diff.append( (i,j) )

        # Iterative optimization
        quietprint('[janus.classifier.ranking.train]: iterative optimization')
        k_iter = 1
        w = None
        while k_iter < numIterations:
            (i_same, j_same) = K_same[self.rng.randint(len(K_same))]
            (i_diff, j_diff) = K_diff[self.rng.randint(len(K_diff))]
            x_same = np.square(X[i_same] - X[j_same])
            x_diff = np.square(X[i_diff] - X[j_diff])
            x = (np.array(x_same) - np.array(x_diff)).flatten()

            # Iterative update
            gamma = 1.0 / (svmLambda * k_iter)
            w = np.zeros_like(x.flatten()) if w is None else w
            if np.dot(w,x) > -1:
                w = w * (1 - gamma * svmLambda) - gamma * x
            else:
                w = w * (1 - gamma * svmLambda)
            k_iter += 1

            if ((k_iter-1) % 10000) == 0:
                quietprint('[janus.classifier.ranking.train][%d/%d]: training' % (k_iter,numIterations))

        self.model = w;
        return self


    def trainLocal(self, imfeatset, svmLambda=1E-8, numIterations=1E6):
        """ One vs. rest structured SVM for ranking same vs. different classifier on (im, features) tuples already collected"""
        quietprint('[janus.classifier.ranking.train]: training ranking classifier')

        # Same/different pair indexes
        K_same = []; K_diff = []
        for (i, (imp, p)) in enumerate(imfeatset):
            for (j, (imq, q)) in enumerate(imfeatset):
                if (j > i) and (imq.category() == imp.category()):
                    K_same.append( (i,j) )
                elif (j > i):
                    K_diff.append( (i,j) )

        # Iterative optimization
        quietprint('[janus.classifier.ranking.train]: iterative optimization')
        k_iter = 1
        w = None
        while k_iter <= numIterations:
            (i_same, j_same) = K_same[np.random.randint(len(K_same))]
            (i_diff, j_diff) = K_diff[np.random.randint(len(K_diff))]
            x_same = np.square(imfeatset[i_same][1] - imfeatset[j_same][1])
            x_diff = np.square(imfeatset[i_diff][1] - imfeatset[j_diff][1])
            #x_same = (np.hstack( (imfeatset[i_same][1], imfeatset[j_same][1]) ))
            #x_same = x_same / np.linalg.norm(x_same)
            #x_diff = (np.hstack( (imfeatset[i_diff][1], imfeatset[j_diff][1]) ))
            #x_diff = x_diff / np.linalg.norm(x_diff)
            x = (np.array(x_same) - np.array(x_diff)).flatten()

            # Iterative update
            gamma = 1.0 / (svmLambda * k_iter)
            w = np.zeros_like(x.flatten()) if w is None else w
            if np.dot(w,x) > -1:
                w = w * (1 - gamma * svmLambda) - gamma * x
            else:
                w = w * (1 - gamma * svmLambda)
            k_iter += 1

            if ((k_iter-1) % 10000) == 0:
                quietprint('[janus.classifier.ranking.train][%d/%d]: training' % (k_iter-1,numIterations))

        self.model = w;
        return self



    def train_samediff(self, sameset, diffset, svmLambda=1E-8, numIterations=1E6, batchFraction=0.15):
        """ One vs. rest structured SVM for ranking same vs. different classifier """
        quietprint('[janus.classifier.ranking.train]: training ranking classifier')

        # Feature extraction to construct data matrix
        X_same = sameset.map(lambda (imp,imq): (self.f_unary(imp),self.f_unary(imq))).map(self.f_pairwise).cache()  # feature extraction and coding
        X_diff = diffset.map(lambda (imp,imq): (self.f_unary(imp),self.f_unary(imq))).map(self.f_pairwise).cache()

        # Iterative optimization
        ssvm_lambda = svmLambda
        n_iter = numIterations
        k_iter = 1
        w = None
        while k_iter < n_iter:
            x_same = X_same.sample(withReplacement=False, fraction=batchFraction).collect()
            x_different = X_diff.sample(withReplacement=False, fraction=batchFraction).collect()
            for (s,d) in cartesian(x_same,x_different):
                if ((k_iter-1) % 10000) == 0:
                    quietprint('[janus.classifier.ranking.train][%d/%d]: training' % (k_iter,n_iter))
                x = (np.array(s) - np.array(d)).flatten()
                gamma = 1.0 / (ssvm_lambda * k_iter)
                w = np.zeros_like(x.flatten()) if w is None else w
                if np.dot(w,x) > -1:
                    w = w * (1 - gamma * ssvm_lambda) - gamma * x
                else:
                    w = w * (1 - gamma * ssvm_lambda)
                k_iter += 1

        # Garbage collection
        X_same = X_same.unpersist()
        X_diff = X_diff.unpersist()

        self.model = w;
        return self


    def test(self, probeset, galleryset, f_unary):
        """Parallel evaluation of models using features computed on testset, returning a tuple of lists ( {0,1} true label, predictedlabel ) for each model"""
        quietprint('[janus.classifier.ranking.test]: testing ranking classifier')

        # Feature extraction to construct data matrix
        X_probe = probeset.map(f_unary).collect()
        X_gallery = galleryset.map(f_unary).collect()

        w = self.model.flatten()
        yhat = [-np.dot(np.array(np.square(p-g)).flatten(), w) for (p,g) in cartesian(X_probe, X_gallery)]
        y = [float(p.category() == g.category()) for (p,g) in cartesian(probeset.collect(), galleryset.collect())]

        return (y,yhat)

    def testLocal(self, probeset, galleryset):
        """Evaluation of structured svm for precollected (im, f) features"""
        quietprint('[janus.classifier.ranking.test]: testing ranking classifier')

        w = self.model.flatten()
        yhat = [-np.dot(np.array(np.square(p-q)).flatten(), w) for ((imp, p), (imq, q)) in cartesian(probeset, galleryset)]
        y = [float(imp.category() == imq.category()) for ((imp, p), (imq, q)) in cartesian(probeset, galleryset)]
        return (y,yhat)


class Verification():
    def __init__(self, binaryclassifier=linearsvm, features=None):
        self.model = None
        self.classifier = binaryclassifier
        self.features = features

    def train(self, trainset):
        """ Parallel one vs. rest verification classifier """
        quietprint('[janus.classifier.verification.train]: training verification classifier')

        # Feature extraction to construct data matrix
        if self.features is not None:
            X = (trainset.map(self.features)   # feature extraction
                         .cache())  # cache features in memory
        else:
            X = trainset.cache()

        # Same vs. different labels
        y = trainset.map(lambda (improbe, imgallery): float(improbe.category() == imgallery.category()))

        self.model = self.classifier(X, y)

        # Garbage collection
        X = X.unpersist()

        return self

    def test(self, testset):
        """Parallel evaluation of models using features computed on testset, returning a tuple of lists ( {0,1} true label, predictedlabel ) for each model"""
        quietprint('[janus.classifier.verification.test]: testing verification classifier')

        # Feature extraction to construct data matrix
        if self.features is not None:
            X = (testset.map(self.features)   # feature extraction
                        .cache())  # cache features in memory
        else:
            X = testset.cache()

        # FIXME: spark-1.1.0 predictions are binary, need manual inner product.
        eval = testset.zip(X).map(lambda ((improbe,imgallery), x): (float(improbe.category() == imgallery.category()), float(np.matrix(x) * np.matrix(self.model.weights).transpose()))).collect()
        (y,yhat) = zip(*eval)

        # Garbage Collection
        X = X.unpersist()

        return (y,yhat)


class StructuredSVMForRanking():
    """http://www.cs.cornell.edu/People/tj/publications/joachims_02c.pdf"""

    def __init__(self, features=None):
        self.model = None
        self.features = features

    def train(self, trainset, svmLambda=1E-8, numIterations=1E6, batchFraction=0.5):
        """ One vs. rest structured SVM for ranking same vs. different classifier """
        quietprint('[janus.classifier.ranking.train]: training ranking classifier')

        # Feature extraction to construct data matrix
        if self.features is None:
            X = trainset.cache()
        else:
            X = trainset.map(self.features).cache()  # feature extraction

        # Same vs. different labels
        y = trainset.map(lambda (improbe, imgallery): float(improbe.category() == imgallery.category()))

        # SVM dataset
        from pyspark.mllib.regression import LabeledPoint
        dataset = X.zip(y).map(lambda (x,y): LabeledPoint(float(y), np.array(x)))
        self.trainOnFeatures(trainset=dataset,
                             svmLambda=svmLambda,
                             numIterations=numIterations,
                             batchFraction=batchFraction)

        X = X.unpersist()
        trainset = trainset.unpersist()
        dataset = dataset.unpersist()
        return self

    def trainOnFeatures(self,
                        trainset,
                        svmLambda=1e-8,
                        numIterations=1e6,
                        batchFraction=0.5):
        """ One vs. rest structured SVM for ranking same vs. different classifier """
        # trainset is RDD of (LabeledPoints)

        sameset = trainset.filter(lambda lp: lp.label==1).cache()
        differentset = trainset.filter(lambda lp: lp.label==0).cache()

        # Iterative optimization
        ssvm_lambda = svmLambda
        n_iter = numIterations
        k_iter = 1
        w = None
        while k_iter < n_iter:
            same = sameset.sample(withReplacement=False, fraction=batchFraction).collect()  # WARNING: do not set seed!
            different = differentset.sample(withReplacement=False, fraction=batchFraction).collect() # WARNING: do not set seed!
            for (s,d) in cartesian(same,different):
                if ((k_iter-1) % 10000) == 0:
                    quietprint('[janus.classifier.ranking.train][%d/%d]: training' % (k_iter,n_iter))
                x = np.array(s.features - d.features).flatten()
                gamma = 1.0 / (ssvm_lambda * k_iter)
                w = np.zeros_like(x.flatten()) if w is None else w
                if np.dot(w,x) > -1:
                    w = w * (1 - gamma * ssvm_lambda) - gamma * x
                else:
                    w = w * (1 - gamma * ssvm_lambda)
                k_iter += 1

        # Garbage collection
        sameset = sameset.unpersist()
        differenset = differentset.unpersist()

        # Done
        self.model = w;
        return self





    def test(self, testset):
        """Parallel evaluation of models using features computed on testset, returning a tuple of lists ( {0,1} true label, predictedlabel ) for each model"""
        quietprint('[janus.classifier.ranking.test]: testing ranking classifier')

        # Feature extraction to construct data matrix
        X = (testset.map(self.features)   # feature extraction
                    .cache())  # cache features in memory

        # re-form as LabeledPoint
        from pyspark.mllib.regression import LabeledPoint
        eval = testset.zip(X).map(
            (lambda ((improbe,imgallery),x): LabeledPoint(label=float(improbe.category() == imgallery.category()),
                                                          features=x))).cache()
        (y,yhat) = self.testOnFeatures(eval)

        # Garbage collection
        X = X.unpersist()
        eval = eval.unpersist()

        # Done
        return (y,yhat)

    def testOnFeatures(self, testset):
        """Parallel evaluation of models using features computed on testset, returning a tuple of lists ( {0,1} true label, predictedlabel ) for each model"""
        # testset is RDD of (descriptor,boolean)

        # Model evaluation (without intercept, note negative dot product )
        eval = testset.map(
            lambda lp: (float(lp.label),-np.dot(np.array(lp.features).flatten(),self.model.flatten()))).collect()
        (y,yhat) = zip(*eval)

        return (y,yhat)

class OneVsRest():
    def __init__(self, binaryclassifier=linearsvm):
        self.models = None
        self.categories = None
        self.classifier = binaryclassifier

    def train(self, trainset, classes=None):
        """ Parallel One vs. rest linear SVM learning - return (category, model) tuples """
        if classes is None:
            f_categories = (lambda (descriptors,category): category)
            classes = trainset.map(f_categories).distinct().collect()
        quietprint('[janus.classifier.train]: training linear svm for %d %s' % (len(classes), 'class' if len(classes)==1 else 'classes'))

        # Data Sphering: FIXME
        #mu = bow.sum() / bow.count()  # FIXME: mean() throws numpy exception
        #sigma = bow.map(lambda x: (x-mu)*(x-mu)).sum() / bow.count()
        #bow = bow.map(lambda x: (x-mu)/sigma).cache()

        f_data = (lambda (descriptors,category): descriptors)
        (self.categories, self.models) = zip(*[(c, self.classifier(trainset.map(f_data), trainset.map(lambda (descriptors,category): float(category.lower() == c.lower())))) for c in classes])
        return self

    def test(self, testset):
        """Parallel evaluation of models using features computed on testset, returning a tuple of lists ( {0,1} true label, predictedlabel ) for each model"""
        quietprint('[janus.classifier.test]: testing models for %d classes' % len(self.categories))

        # FIXME: spark-1.0.1 predictions are binary, need manual inner product.  Fixed in spark-1.0.2?
        #return [zip(*testset.zip(features).map(lambda (im, x): (float(im.iscategory(testclass)), float(model.predict(x)))).collect()) for (testclass,model) in zip(categories, models)]
        eval = [testset.map(lambda (descriptors,category): (float(category.lower() == testclass.lower()), float(np.matrix(descriptors) * np.matrix(model.weights).transpose()))).collect() for (testclass, model) in zip(self.categories, self.models)]

        # Return similarity matrix and mask
        (Y,Yhat) = zip(*eval)
        return (np.array(Y), np.array(Yhat))
