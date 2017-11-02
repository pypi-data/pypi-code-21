from janus.dataset.cs3 import CS3
from janus.dataset.cs4 import CS4
from multiprocessing import Pool, Lock, Process, Manager
from multiprocessing.sharedctypes import Value, Array, RawArray
from ctypes import Structure, c_double, c_float, c_int, POINTER, c_char_p, c_bool
import itertools
import numpy as np
import collections
import ctypes
from collections import OrderedDict, MutableMapping
from itertools import product, combinations
from sklearn.svm import SVC, LinearSVC
import numpy.ctypeslib
import time
import os
import dill
from janus.net.svm.govo import EvaluateMultiProc, TournamentOvOSVM, SharedSvmCache, C2NP
import janus.net.svm.multiproc_globals as mpg
from janus.net.svm.multiproc_globals import feat_size, feature_t


class ProbeOvOSvm:

    def __init__(self, tournaments=10, E=3., C=10, alpha=0.0,
                 threads=8, fit_bias=True, add_bias=False, serial=False):
        self.tournaments = tournaments
        self.threads = threads
        self.fit_bias = fit_bias
        self.add_bias = add_bias
        self.alpha = alpha
        self.serial = serial
        self.C = C
        self.E = E

    def evaluate(self, P, Pid, Pc, G, Gid, Gc, Nc, N, hard_negatives_array, hard_negatives_gids, rankN=20):

        N = list(N)
        for i, n in enumerate(N):
            N[i] = n.astype(np.float32)

        self._negatives_c = Array(ProbeOvOSvm.NegativeTemplate_C, [(c_char_p("%s" % (Nc[i])),
                                                                   (numpy.ctypeslib.as_ctypes(n))) for i, n in enumerate(N)])

        # negative media

        gset = list(set(Gc))
        assert(set(Gid) == set(hard_negatives_gids))
        Gid2Gc = {gid: Gc[i] for i, gid in enumerate(Gid)}
        self.hard_negatives = {Gid2Gc[gallery_id]: hard_negatives_array[i, :] for i, gallery_id in enumerate(hard_negatives_gids)}
        unique_hard_negatives = set(hard_negatives_array[:, 0:rankN].flatten().tolist())
        print "found ", len(unique_hard_negatives), " unique hard negatives instead of ", rankN * len(Gc)
        self._gcats = Gc
        self._ncats = list(set(Nc))
        assert(len(gset) == len(G))
        self._NEG = {nc: [] for nc in self._ncats}
        self._GAL = {gc: -1 for gc in self._gcats}
        for i, gc in enumerate(self._gcats):
            self._GAL[gc] = i  # regular dict to map from gal cateogry to array

        for i, n_media in enumerate(self._negatives_c):
            self._NEG[n_media.Nc].append(i)  # regular dict
        negative_inds = {neg: i for i, neg in enumerate(self._ncats)}
        G = list(G)
        for i, g in enumerate(G):
            G[i] = g.astype(np.float32)

        self._gallery_c = Array(feature_t, [numpy.ctypeslib.as_ctypes(g) for g in G])  # gal templates as ctypes in shared memory
        self._gallery = np.array(G)  # memory to be copied. This will not scale;
        # generate score mask as per the hard negatives
        score_mask = ([], [])
        for i, gc in enumerate(Gc):
            for j, neg in enumerate(self.hard_negatives[gc][0: rankN]):
                score_mask[0].append(i)
                score_mask[1].append(negative_inds[neg])  # append index of negative category fron N_gal x N_neg array

        worker_task = EvaluateMultiProcProbe(self._gallery, self._NEG,
                                             self.C, self.E, self.alpha,
                                             self.add_bias, self.fit_bias, self.tournaments,
                                             self.hard_negatives, unique_hard_negatives,
                                             score_mask, negative_inds,
                                             rankN=rankN)
        pdict = {pid: [] for pid in Pid}
        for i, pid in enumerate(Pid):
            pdict[pid].append((P[i], Pc[i]))
        self.pdict = pdict

        self._Y = np.array([pdict[pid][0][1] == category for pid in pdict for category in self._gcats]).reshape(len(pdict), len(self._gcats))
        if not self.serial:

            workers = Pool(self.threads, initializer=self._init_multiproc, maxtasksperchild=1)
            (winners, Yhs, Pid_out) = zip(*workers.map(worker_task, zip(pdict.keys(), pdict.values())))

            workers.close()
            workers.join()
            Yhat = self._soft_eval(winners, Yhs, Pid_out, Pid, Pc)

            return self._Y, Yhat, self._gcats, Pid_out
        else:
            self._init_multiproc()
            for pid in pdict:
                winners, Yhs, Pid_out = worker_task((pid, pdict[pid]))
            return self._Y, Yhs, self._gcats, Pid_out

    def _init_multiproc(self):
        global gcats, ncats, gallery, negatives
        negatives = self._negatives_c

        gallery = np.ctypeslib.as_array(self._gallery_c.get_obj(), shape=(len(self._gcats), feat_size))
        gcats = np.array(self._gcats)
        ncats = np.array(self._ncats)

    def _soft_eval(self, winners, Yhs, Pid_out, Pid_in, Pc):

        Yh_unordered = {pid_o: Yhs[i] for i, pid_o in enumerate(Pid_out)}
        Pcat_dict = {pid: self.pdict[pid][0][1] for pid in self.pdict}

        Yhat = np.array([Yh_unordered[pid] for pid in set(Pid_in)]).reshape(len(Yhs), len(self._gcats))
        n_mates = np.sum(np.sum(self._Y, axis=1))
        if n_mates != 0:
            rank = [1, 5, 10, 20]
            print " ====== with score sorting ========:"
            ranked = np.zeros(self._Y.shape)
            Yh_sorted = np.zeros(self._Y.shape)
            for i in xrange(0, self._Y.shape[0]):
                k = np.argsort(-Yhat[i, :])
                ranked[i, :] = self._Y[i, k]
                Yh_sorted[i, :] = Yhat[i, k]

            for r in rank:
                n_correct_mates = np.sum(ranked[:, 0:r])
                print "Rank %s retrieval is %.3f" % (r, (n_correct_mates / float(n_mates)))
            print " ====== winner count ========:"
            flippable = 0; count_correct = 0
            for j, pid in enumerate(Pid_out):
                if Pcat_dict[pid] == winners[j]:
                    count_correct += 1

            print float(count_correct) / float(n_mates), " with %.3f %% flippable" % (100 * float(flippable) / len(winners))

        return Yhat


    class NegativeTemplate_C(Structure):
        _fields_ = [('Nc', c_char_p),
                    ('N', feature_t),
                    ]


class EvaluateMultiProcProbe(object):

    def __init__(self, local_gallery, neg_dict, C, E, alpha, add_bias, fit_bias, tournaments,
                 hard_negatives, unique_hard_negatives,
                 score_mask, negative_inds,
                 rankN=20):
        self.tournaments = tournaments
        self.E = E
        self.C = C
        self.alpha = alpha
        self.fit_bias = fit_bias
        self.NEG = neg_dict
        self.add_bias = add_bias
        self.local_gallery = local_gallery
        self.add_bias = add_bias
        self.hard_negatives = hard_negatives
        self.unique_hard_negatives = unique_hard_negatives
        self.rankN = rankN
        self.score_mask = score_mask
        self.negative_inds = negative_inds

    def __call__(self, probe_tup):

        (Pid, Plist) = probe_tup
        P, Pc = zip(*Plist)
        probe_category = set(Pc)
        assert(len(probe_category) == 1)
        neg_svm_dic = {uniq_hard_neg: None for uniq_hard_neg in self.unique_hard_negatives}
        svm_training = 0; neg_read = 0; mdot = 0; mfill = 0; thresh = 0;
        tsglob = time.time()
        scores = np.zeros((len(gcats), self.rankN))
        svm_mat = np.zeros((feat_size, len(ncats)))
        for i, gc in enumerate(gcats):
#            svm_mat = np.zeros((feat_size, self.rankN))
            biases = np.zeros((1, self.rankN))
            curr_hard_negatives = self.hard_negatives[gc][0:self.rankN]
            for n, neg in enumerate(curr_hard_negatives):  # compute rankN svms
                if neg_svm_dic[neg] is None:  # train if not in local neg svm cache
                    train_f = list(P); train_l = list(Pc)
                    ts = time.time()
                    for index in self.NEG[neg]:
                        curr_neg = negatives[index]
                        train_f.append(C2NP(curr_neg.N))
                        train_l.append(curr_neg.Nc)
                    te = time.time()
                    neg_read += (te - ts)
                    ts = time.time()
                    svc = LinearSVC(C=self.C, loss='squared_hinge', penalty='l2',
                                    fit_intercept=self.fit_bias, verbose=False, dual=False,
                                    class_weight='balanced',
                                    tol=1e-2).fit(train_f, train_l)
                    svm_tup = (svc.coef_.reshape(1, -1), svc.intercept_)
                    if svc.classes_[0] in probe_category:  # svc -1 class is first class in matchup
                        svm_tup = (-1 * svc.coef_, -1 * svc.intercept_)
                    te = time.time()
                    svm_training += (te - ts)
                    neg_svm_dic[neg] = svm_tup
                    ts = time.time()
                    ind_of_neg = self.negative_inds[neg]
                    # ind_of_neg = n
                    svm_mat[:, ind_of_neg] = np.squeeze(svm_tup[0])
                    biases[: ind_of_neg] = svm_tup[1]
                    te = time.time()
                    mfill += (te - ts)
                else:
                    continue;
            ts = time.time()
            # if self.add_bias:
            #     scores[i, :] = np.dot(self.local_gallery[i, :], svm_mat) + biases
            # else:
            #     scores[i, :] = np.dot(self.local_gallery[i, :], svm_mat)
            # te = time.time()
            # mdot += (te - ts)
        ts = time.time()
        if self.add_bias:
            scores = np.dot(self.local_gallery, svm_mat) + biases
        else:
            scores = np.dot(self.local_gallery, svm_mat)
        scores = scores[self.score_mask].reshape(len(gcats), self.rankN)
        te = time.time()
        mdot += (te - ts)

        ts = time.time()
        # inds_greater = np.where(scores >= self.alpha)
        # inds_smaller = np.where(scores < - self.alpha)
        # scores[inds_greater] = 1.
        # scores[inds_smaller] = 0.
        if self.alpha != 0:
            inds_between = np.where(np.logical_and((scores < self.alpha),
                                                   (scores > -self.alpha)))

            scores[inds_between] = (scores[inds_between]) / (2 * self.alpha) + 0.5
        # import pdb
        # pdb.set_trace()
        Yh = np.squeeze(np.sum(scores, axis=1)) / float(self.rankN)
        te = time.time();
        thresh += (te - ts)
        winner_index = np.argmax(Yh)
        teglob = time.time()
        tot = teglob - tsglob
        misc_t = tot - (neg_read + svm_training + mfill + mdot + thresh)
        print "[Probe ID_%s]: tot %.3f; N_read %.3f; S_train %.3f; Mfill %.3f; Gdot = %.3f; Thr = %.3f; misc_t %.3f" % (Pid, tot,
                                                                                                            neg_read, svm_training,
                                                                                                            mfill, mdot, thresh, misc_t)

        return (gcats[winner_index], Yh, Pid)


class ComputeHardGalleryNegatives(object):

    def __init__(self, tournaments=10, E=0.0, C=10, alpha=0.5,
                 threads=8, max_cache_size=400000, debug_dic_path=None,
                 award_points=True, fit_bias=True, add_bias=False, use_fast_cache=True, serial=False):
        self.tournaments = tournaments
        self.E = E
        self.C = C
        self.debug_dic_path = debug_dic_path
        self.alpha = alpha
        self.award_points = award_points
        self._media_c = None
        self._c_index_array = None
        self.fit_bias = fit_bias
        self.add_bias = add_bias
        self.lock = Lock()
        self.gallery_lock = Lock()
        self._threads = threads
        self._cats = None
        self.serial = serial
        self._cache_hits = Value('i', 0)
        self._svms_trained = Value('i', 0)
        self.fast_cache = use_fast_cache
        self.max_cache_size = max_cache_size

    def _init_multiproc(self):

        mpg.cats = self._cats
        mpg.svm_cache = self._svm_cache
        mpg.debug_dic_path = self.debug_dic_path
        mpg.c_index_array = self._c_index_array
        mpg.svm_media = self._media_c
        mpg.media_index = self._media_index
        mpg.svms_trained = self._svms_trained
        mpg.cache_hits = self._cache_hits

    def evaluate(self, G, Gc, Gid, N, Nc):
        self._cats = list(set(Nc))

        N = list(N)
        for i, n in enumerate(N):
            N[i] = n.astype(np.float32)

        self._media_c = Array(TournamentOvOSVM.Media_C, [(c_char_p("%s" % (Nc[i])),
                                                          (numpy.ctypeslib.as_ctypes(n))) for i, n in enumerate(N)], lock=self.lock)

        self._media_index = {nc: [] for nc in self._cats}
        for i, c_media in enumerate(self._media_c):
            self._media_index[c_media.Fc].append(i)  # regular dict

        category_pairs = [pair for pair in itertools.combinations(self._cats, 2)]

        self._svm_cache = SharedSvmCache(self.max_cache_size, feat_size, self._cats)
        self._c_index_array = None

        worker_task = EvaluateMultiProc(self._c_index_array, self.C, self.E, self.alpha, self.add_bias,
                                        self.fit_bias, self.tournaments,
                                        self.award_points, self.fast_cache, self.max_cache_size)
        if not self.serial:

            workers = Pool(self._threads, initializer=self._init_multiproc, maxtasksperchild=1)

            (winners, Yhs, Gid_out, output_pairs) = zip(*workers.map(worker_task, zip(G, Gid, Gc)))

            workers.close()
            workers.join()

        else:
            self._init_multiproc()
            Yhs = []; Gid_out = []; output_pairs = []; winners = []
            for i in xrange(0, len(G)):
                winners_i, Yh_i, Gid_out_i, output_pairs_i = worker_task(probe_tup=(G[i], Gid[i], Gc[i]))
                Yhs.append(Yh_i); winners.append(winners_i); Gid_out.append(Gid_out_i); output_pairs.append(output_pairs_i)
        Yhat, ranked_negatives = self._soft_eval(winners, Yhs, Gid_out, Gid, Gc)

        return ranked_negatives, Yhat, self._cats, Gid

    def _soft_eval(self, winners, Yhs, Gid_out, Gid_in, Gc):

        Yh_unordered = {pid_o: Yhs[i] for i, pid_o in enumerate(Gid_out)}
        Yhat = np.array([Yh_unordered[gid] for gid in Gid_in]).reshape(len(Yhs), len(self._cats))
        print " ====== with score sorting ========:"
        ranked_negatives = np.array([self._cats] * len(Yhs)).reshape(Yhat.shape)
        Yh_sorted = np.zeros(Yhat.shape)
        for i in xrange(0, Yhat.shape[0]):
            k = np.argsort(-Yhat[i, :])
            ranked_negatives[i, :] = ranked_negatives[i, k]
            Yh_sorted[i, :] = Yhat[i, k]

        return (Yhat, ranked_negatives)
