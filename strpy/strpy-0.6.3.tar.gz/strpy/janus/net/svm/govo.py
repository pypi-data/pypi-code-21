from janus.dataset.cs3 import CS3
from janus.dataset.cs4 import CS4
import janus.net.svm.multiproc_globals as mpg
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
from janus.net.svm.multiproc_globals import feat_size, feature_t

class TournamentOvOSVM(object):

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
        self._manager = Manager()
        self._threads = threads
        self._cats = None
        self.serial = serial
        self._cache_hits = Value('i', 0)
        self._svms_trained = Value('i', 0)
        self.fast_cache = use_fast_cache
        self.max_cache_size = max_cache_size

    def evaluate(self, P, Pc, Pid, G, Gc, Gid):
        self._cats = list(set(Gc))
        G = list(G)
        for i, g in enumerate(G):
            G[i] = g.astype(np.float32)  # need to ensure float32 inputs
        self._media_c = Array(TournamentOvOSVM.Media_C, [(c_char_p("%s" % (Gc[i])),
                              (numpy.ctypeslib.as_ctypes(g))) for i, g in enumerate(G)], lock=self.lock)

        self._media_index = {gc: [] for gc in self._cats}
        for i, c_media in enumerate(self._media_c):
            self._media_index[c_media.Fc].append(i)  # regular dict

        category_pairs = [pair for pair in itertools.combinations(self._cats, 2)]

        if not self.fast_cache:
            self._c_index_array = Array(SharedSvmCache.IndexOf, [(c_char_p(cp[0]),
                                                                  c_char_p(cp[1]),
                                                                  c_int(-1)) for cp in category_pairs], lock=self.gallery_lock)
            self._svm_cache = self._manager.dict({(cp[0], cp[1]): None for cp in category_pairs})
        else:
            self._svm_cache = SharedSvmCache(self.max_cache_size, feat_size, self._cats)
            self._c_index_array = None


        self._Y = np.array([pc == category for pc in Pc for category in self._cats]).reshape(len(Pid), len(self._cats))


        worker_task = EvaluateMultiProc(self._c_index_array, self.C, self.E, self.alpha, self.add_bias,
                                        self.fit_bias, self.tournaments,
                                        self.award_points, self.fast_cache, self.max_cache_size)
        if not self.serial:

            workers = Pool(self._threads, initializer=self._init_multiproc, maxtasksperchild=1)

            (winners, Yhs, Pid_out, output_pairs) = zip(*workers.map(worker_task, zip(P, Pid, Pc)))

            workers.close()
            workers.join()

        else:
            self._init_multiproc()
            Yhs = []; Pid_out = []; output_pairs = []; winners = []
            for i in xrange(0, len(P)):
                winners_i, Yh_i, Pid_out_i, output_pairs_i = worker_task(probe_tup=(P[i], Pid[i], Pc[i]))
                Yhs.append(Yh_i); winners.append(winners_i); Pid_out.append(Pid_out_i); output_pairs.append(output_pairs_i)

        Yhat = self._soft_eval(winners, Yhs, Pid_out, Pid, Pc)
        if self.debug_dic_path is not None:
            self._consolidate_svm_outputs(output_pairs, Pid_out)

        return self._Y, Yhat, self._cats, Pid


    def _soft_eval(self, winners, Yhs, Pid_out, Pid_in, Pc):

        Yh_unordered = {pid_o: Yhs[i] for i, pid_o in enumerate(Pid_out)}
        Pcat_dict = {pid: Pc[i] for i, pid in enumerate(Pid_in)}
        Yhat = np.array([Yh_unordered[pid] for pid in Pid_in]).reshape(len(Yhs), len(self._cats))
        n_mates = np.sum(np.sum(self._Y, axis=1))
        if n_mates == 0:
            print  "No mated probes in evaluation set"
            return
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
            uniq, counts = np.unique(winners[j], return_counts=True)
            winner_dict = {u: counts[i] for i, u in enumerate(uniq)}
            cat = max(winner_dict, key=lambda k: winner_dict[k])
            if winner_dict[cat] != self.tournaments:
                flippable += 1
            if cat == Pcat_dict[pid]:
                count_correct += 1

        print float(count_correct) / float(n_mates), " with %.3f %% flippable" % (100 * float(flippable) / len(winners))

        return Yhat

    def _init_multiproc(self):

        mpg.cats = self._cats
        mpg.svm_cache = self._svm_cache
        mpg.debug_dic_path = self.debug_dic_path
        mpg.c_index_array = self._c_index_array
        mpg.svm_media = self._media_c
        mpg.media_index = self._media_index
        mpg.svms_trained = self._svms_trained
        mpg.cache_hits = self._cache_hits

    def _consolidate_svm_outputs(self, output_pairs, Pid):
        ids = []
        rscores = []
        for i in xrange(0, len(Pid)):
            L = list(output_pairs[i])
            for l in L:
                ids.append((Pid[i], l[0], l[1]))
                rscores.append(l[2])
        # import pdb
        # pdb.set_trace()

        dic = {'id': np.array(ids), 'scores': np.array(rscores)}
        if self.debug_dic_path is not None:
            with open(self.debug_dic_path, 'wb') as f:
                dill.dump(dic, f)

    class ovoSvmIndicator(Structure):
        _fields_ = [('C_A', c_char_p), ('C_B', c_char_p),
                    ('exists', c_bool),
                    ]

    class Media_C(Structure):
        _fields_ = [('Fc', c_char_p),
                    ('F', feature_t),
                    ]


def C2NP(c_array):
    ptr = ctypes.cast(c_array, POINTER(feature_t))
    return numpy.frombuffer(ptr.contents, dtype=np.float32)


class EvaluateMultiProc(object):

    def __init__(self, c_index_array, C, E, alpha, add_bias, fit_bias, tournaments,
                 award_points, use_fast_cache, cache_size):
        self.tournaments = tournaments
        self.E = E
        self.C = C
        self.alpha = alpha
        self.award_points = award_points
        self.fit_bias = fit_bias
        self.add_bias = add_bias
        self.use_fast_cache = use_fast_cache
        self.cache_size = cache_size
        if not use_fast_cache:
            self.local_cache = {(c_svm.C_A, c_svm.C_B): i for i, c_svm in enumerate(c_index_array)}
        else:
            self.local_cache = None

    def __call__(self, probe_tup):

        (P, Pid, Pc) = probe_tup
        winner = []

        local_cache_hits = 0
        local_trained_svms = 0
        C2I = {cat: i for i, cat in enumerate(mpg.cats)}
        Yh = OrderedDict([(cat, 0) for cat in mpg.cats])
        start = time.time()
        init_t = 0; cache_read = 0; svm_training = 0; multiplication_op = 0; scoring = 0; gall_read = 0; svm_check = 0; gal_updt = 0
        curr_cats = []; all_byes = []
        N = len(mpg.cats)
        npof2 = int(2 ** np.ceil(np.log(N) / np.log(2)))
        num_byes = npof2 - N
        round = 0
        local_cache = self.local_cache
        max_rounds = int(np.floor(np.log(N) / np.log(2))) + 1
        output_pairs = set([])
        K = self.tournaments

        curr_cats = np.array(K * mpg.cats).reshape(K, -1)
        for k in xrange(0, K):
            np.random.seed(k)
            np.random.shuffle(curr_cats[k, :])
        all_byes = curr_cats[:, len(mpg.cats) - num_byes: len(mpg.cats)]
        curr_cats = curr_cats[:, 0: len(mpg.cats) - num_byes]
        while (N > 1):
            # print "started round %s" % round

            N = curr_cats.shape[1]
            ts = time.time()
            matchups = [(curr_cats[k][i],
                         curr_cats[k][N - i - 1]) for k in xrange(0, K) for i in xrange(0, N / 2)]
            for m in xrange(0, len(matchups)):
                if self.use_fast_cache:
                    reverse_match = matchups[m] not in mpg.svm_cache.dict
                else:
                    reverse_match = matchups[m] not in local_cache
                if reverse_match:
                    matchups[m] = (matchups[m][1], matchups[m][0])


            # match_array = np.zeros((P.shape[0], len(matchups)))
            # bias_array = np.zeros((1, len(matchups)))
            scores = np.zeros((1, len(matchups)))
            te = time.time()
            init_t += (te - ts)

            for m in xrange(0, len(matchups)):
                ts = time.time()
                match = matchups[m]
                svm_tup = None
                if not self.use_fast_cache:
                    data_index = local_cache[match]
                    empty = mpg.c_index_array[data_index].I == -1
                else:
                    train_current_match = match not in mpg.svm_cache
                te = time.time()
                svm_check += (te - ts)
                if not train_current_match:
                    ts = time.time()
                    svm_tup = mpg.svm_cache[match]  # this can be None
                    te = time.time()
                    cache_read += (te - ts)
                    mpg.cache_hits.value += 1
                    local_cache_hits += 1
                if train_current_match or svm_tup is None:  # train svm

                    mpg.svms_trained.value += 1
                    local_trained_svms += 1
                    train_feat = []
                    train_label = []
                    tgs = time.time()
                    for train_i in mpg.media_index[match[0]] + mpg.media_index[match[1]]:
                        curr_media = mpg.svm_media[train_i]
                        train_feat.append(C2NP(curr_media.F))
                        train_label.append(curr_media.Fc)

                    tge = time.time()
                    gall_read += (tge - tgs)

                    ts = time.time()
                    svc = LinearSVC(C=self.C, loss='squared_hinge', penalty='l2',
                                    fit_intercept=self.fit_bias, verbose=False, dual=False,
                                    class_weight='balanced',
                                    tol=1e-2).fit(train_feat, train_label)
                    svm_tup = (svc.coef_.reshape(1, -1), svc.intercept_)
                    if svc.classes_[0] == match[0]:  # svc -1 class is first class in matchup
                        svm_tup = (-1 * svc.coef_, -1 * svc.intercept_)
                    mpg.svm_cache[match] = svm_tup  # write this svm in the cache
                    if not self.use_fast_cache:
                        mpg.c_index_array[data_index].I = 1
                    te = time.time()
                    svm_training += (te - ts)
                tus = time.time()
                # match_array[:, m] = svm_tup[0]
                # bias_array[:, m] = svm_tup[1]
                if not self.add_bias:
                    scores[:, m] = np.dot(P, svm_tup[0].T)
                else:
                    scores[:, m] = np.dot(P, svm_tup[0].T) + svm_tup[1]
                tue = time.time()
                gal_updt += (tue - tus)

            ts = time.time()
            # if not self.add_bias:
            #     scores = np.dot(P, match_array)
            # else:
            #     scores = np.dot(P, match_array) + bias_array
            te = time.time()
            multiplication_op += 0;  # (te - ts)
            ts = time.time()
            score_arr = np.reshape(scores, (K, N / 2))
            matchups_arr = np.swapaxes(np.array(matchups).T.reshape(2, K, N / 2), 2, 1).T

            if mpg.debug_dic_path is not None:
                interest_inds = np.where(matchups_arr == Pc)
                interest_categories = matchups_arr[interest_inds[0], interest_inds[1], :]
                interest_scores = score_arr[interest_inds[0], interest_inds[1]]
                for i in xrange(0, len(interest_scores)):
                    if Pc == interest_categories[i, 0]:
                        curr_pair = (interest_categories[i, 0],
                                     interest_categories[i, 1], interest_scores[i])
                    else:
                        curr_pair = (interest_categories[i, 1],
                                     interest_categories[i, 0], -interest_scores[i])
                    output_pairs.add(curr_pair)

            score_arr = np.dstack((score_arr, -score_arr))

            random_mat = np.random.rand(score_arr.shape[0], score_arr.shape[1], 1) * (2 * self.alpha) - self.alpha
            random_mat = np.dstack((random_mat, -random_mat))
            score_arr += random_mat

            slice_inds = np.argmax(score_arr, axis=2)  # take the maximum after adding alpha
            mesh = np.mgrid[0: K, 0: N / 2]
            winner_inds = (mesh[0, :, :].flatten(),
                           mesh[1, :, :].flatten(), slice_inds.flatten())  # 3d indeces

            curr_cats = matchups_arr[winner_inds].reshape(K, N / 2)
            winner_scores = score_arr[winner_inds].reshape(K, N / 2)

            if self.award_points:
                winner_scores = np.ones(winner_scores.shape) / (self.tournaments * max_rounds)
            else:
                winner_scores *= self.E ** (round + 1 - max_rounds)
                winner_scores = (winner_scores) / (self.tournaments)
            te = time.time()
            scoring += (te - ts)
            for k in xrange(0, K):
                for n in xrange(0, N / 2):
                    Yh[curr_cats[k, n]] += winner_scores[k, n]
            if round == 0:
                curr_cats = np.hstack((curr_cats, all_byes))

            if N % 2 == 1:
                curr_cats.append(random_cats[N / 2])
            if curr_cats.shape[1] == 1:
                break;
            round += 1
        winner.append(np.squeeze(curr_cats[:, 0]))
        end = time.time()
        misct = (end - start) - (init_t + svm_training + cache_read + multiplication_op + scoring + gall_read + svm_check + gal_updt)
        print "[Probe ID_%s]:: tot %.3f; init %.3f; chk %.3f; G_read %.3f; train %.3f; CHread %.3f; dot %.3f; maxS %.3f; galU %.3f; misc %.3f || new_svm %s; hits %s " % (Pid,
                                                                                                          (end - start),
                                                                                                          init_t,
                                                                                                          svm_check,
                                                                                                          gall_read,
                                                                                                          svm_training,
                                                                                                          cache_read,
                                                                                                          multiplication_op,
                                                                                                          scoring,
                                                                                                          gal_updt,
                                                                                                          misct,
                                                                                                          local_trained_svms,
                                                                                                          local_cache_hits)

        return (winner, Yh.values(), Pid, output_pairs)



class SharedSvmCache(collections.MutableMapping, dict):

    def __init__(self, size, feat_size, cats):

        self.max_size = size
        self.feat_size = feat_size
        self.lock = Lock()
        self._svm_buffer = Array(SharedSvmCache.Svm, [(feature_t(0),
                                                       c_float(0)) for i in xrange(0, self.max_size)])
        self._cats = cats
        self._head = Value('i', 0)
        self._length = Value('i', 0)
        self._last_key = SharedSvmCache.CacheKey('null', 'null')

        category_pairs = [pair for pair in itertools.combinations(self._cats, 2)]
        self._c_index_array = Array(SharedSvmCache.IndexOf, [(c_char_p(cp[0]),
                                                              c_char_p(cp[1]),
                                                              c_int(-1)) for cp in category_pairs])

        self.dict = {(c_svm.C_A, c_svm.C_B): i for i, c_svm in enumerate(self._c_index_array)}

    def __getitem__(self, key):
        try:
            i = self._c_index_array[self.dict[key]].I
            if i != -1:
                svm = self._svm_buffer[i]
                return (C2NP(svm.W).reshape(1, -1), svm.B)

            else:
                return None
        except KeyError:
            print key

    def __setitem__(self, key, value):
        self.lock.acquire()
 #       print key, " acuired lock"
        try:
            if not self.__contains__(key):
                self._head.value += 1
                self._length.value += 1
                if self._length.value >= self.max_size:
                    self._head.value = self.max_size
                    self._length.value = self.max_size
#                    print "Max cache sized reached!"
                    return
                    # Reserved for LRU cache implementation
                    #
                    #
                w_npfloat32 = np.squeeze(value[0]).astype(np.float32)
                W = numpy.ctypeslib.as_ctypes(w_npfloat32)
                B = c_float(value[1])
                self._svm_buffer[self._head.value] = SharedSvmCache.Svm(W, B)
                self._c_index_array[self.dict[key]].I = self._head.value

        except KeyError:
            print key
        finally:
#            print key, " attempted release lock"
            self.lock.release()
#            print key, "  lock released"

    def __len__(self):
        return self._length.value

    def __iter__(self):
        for key in self.dict:
            i = self._c_index_array[self.dict[key]].I
            if i != -1:
                yield key

    def __del__(self):
        for i in xrange(0, self.max_size):
            ptr = ctypes.cast(self._svm_buffer[i].W, POINTER(feature_t))
            del ptr
        # for i in xrange(0, len(self._c_index_array)):
        #     ptr = ctypes.cast(self._svm_buffer[i], POINTER(SharedSvmCache.IndexOf))
        #     del ptr

        del self._c_index_array

    def __contains__(self, key):
        return key in self.dict and self._c_index_array[self.dict[key]].I != -1

    class CacheKey(Structure):
        _fields_ = [('C_A', c_char_p), ('C_B', c_char_p)]

    class IndexOf(Structure):
        _fields_ = [('C_A', c_char_p), ('C_B', c_char_p),
                    ('I', c_int),
                    ]

    class Svm(Structure):
        _fields_ = [('W', feature_t), ('B', c_float)]
