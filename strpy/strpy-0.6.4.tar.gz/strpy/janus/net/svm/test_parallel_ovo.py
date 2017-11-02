from multiprocessing import Pool, Lock, Process, Manager
from multiprocessing.sharedctypes import Value, Array, RawArray
from ctypes import Structure, c_double, c_int, POINTER
import itertools
import numpy as np
from itertools import product, combinations
from janus.dataset.cs4 import CS4
import numpy.ctypeslib
from govo import SharedSvmCache, feature_t, feat_size

class ovoSVM_C(Structure):
    _fields_ = [('G_A', c_int), ('G_B', c_int),
                ('W', feature_t),
                ('B', feature_t)
                ]


def f(i):

    tmp_w = np.ones((feat_size)) * svms[i].G_A
    tmp_b = np.ones((feat_size)) * svms[i].G_B
    # item.W = feature_t(tmp_w.ctypes.data_as(ctypes.POINTER(c_double)).contents)
    # item.B = feature_t(tmp_b.ctypes.data_as(ctypes.POINTER(c_double)).contents)
    svms[i].W = numpy.ctypeslib.as_ctypes(tmp_w)
    svms[i].B = numpy.ctypeslib.as_ctypes(tmp_b)
    print "updated pair %s , % s" % (svms[i].G_A, svms[i].G_B)
    return


def gg(item):

    tmp_w = np.ones((feat_size)) * int(item[0])
    tmp_b = np.ones((feat_size)) * int(item[1])

    p_svms[item] = (tmp_w, tmp_b)


def F(A, i):
    for a in A:
        f(a)

def h(item):
    cache[item] = (np.ones(feat_size) * int(item[0]), int(item[1]))


def initf(svms_, p_svms_, cache_):
    global svms, p_svms, cache
    svms = svms_
    p_svms = p_svms_
    cache = cache_

def inith(cache_):
    global cache
    cache = cache_

if __name__ == '__main__':

    lock= Lock()
    cs4 = CS4('/data/janus/')
    lock = Lock()
    gallery_templates = cs4._cs4_1N_gallery_S1() + cs4._cs4_1N_gallery_S2()
    Gt = [g.templateid() for g in gallery_templates]
    category_pairs = [pair for pair in itertools.combinations(Gt, 2)]
    feat_size = 2048
    cache = SharedSvmCache(200, feat_size, Gt)
    import pdb
    pdb.set_trace()
    # c_svms = Array(ovoSVM_C, [(c_int(int(cp[0])),
    #                            c_int(int(cp[1])),
    #                            feature_t(nan),
    #                            feature_t(nan)) for cp in category_pairs],lock=lock)
#    p_svms = Manager().dict({(cp[0], cp[1]): None for cp in category_pairs})

#    workers=Pool(3, initializer=inith, initargs=(cache,))
    workers=Pool(3)
    np.random.shuffle(category_pairs)
    workers.map(h, category_pairs[0:300])
#    workers=Pool(8,initializer=initf,initargs=(c_svms, p_svms,))
#    workers.map(f,range(0,len(c_svms)))
#    workers.map(gg, category_pairs)
    workers.close()
    workers.join()
    print [(item.G_B, item.I) for i, item in enumerate(cache._c_index_array) if item.I != -1]
    print [(i, svm.B) for i, svm in enumerate(cache._svm_buffer) if  not np.isnan(svm.B)]
    # n = Value('i', 7)
    # p = Process(target=F,args=(c_svms,n))
    # p.start()
    # p.join()
