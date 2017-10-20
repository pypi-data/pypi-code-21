import janus.net.svm
import os
import numpy as np
from janus.net.svm.govo import TournamentOvOSVM
from janus.net.svm.povo import ProbeOvOSvm, ComputeHardGalleryNegatives
from janus.dataset.cs4 import CS4
from janus.dataset.cs3 import CS3
from janus.dataset.strface import STRface
from janus.openbr import readbinary
import shutil
import dill
import time
import argparse
import bobo.util

class ArgsPlaceHolder:

    def __init__(self):
        self.model = 'resnet101_msceleb1m_14APR17'
        self.dataset = 'cs4'
        self.jittering = 'centercrop'
        self.protocol = 'P_mixed'
        self.split = 'G_S2'
        self.nthreads = 8
        self.E = 2.0
        self.C = 10
        self.fitbias = True
        self.addbias = False
        self.awardpoints = False
        self.alphaP = 0.0
        self.alphaG = 0.0
        self.K = 30
        self.cache_size = int(1e6)
        self.do_restricted = -1
        self.serial = False
        self.debug = ""

if __name__ == '__main__':

    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')
    args_namespace = ArgsPlaceHolder()
    parser = argparse.ArgumentParser(description=" Hard Negatives ovo run ")
    parser.add_argument("--model", help="name of the model to test", default='resnet101_msceleb1m_14APR17')
    parser.add_argument("--protocol", help="identification protocol", default="all")
    parser.add_argument("--split", help="split", default="G_S1")
    parser.add_argument("--dataset", help="name of the dataset to test on", choices=['cs3', 'cs4', 'ijba', 'ijbb', 'cs2'], default='cs4')
    parser.add_argument("--jittering", help="type of jittering found in encodings",
                        choices=['centercrop', 'centercrop_5-test_jitter'], default='centercrop')
    parser.add_argument("--dual_jittering", help="treat jittered media if any as individual samples", action="store_true", default=False)
    parser.add_argument("--svm", help="type of svm to train", choices=['GAovo', 'PAovo'], default='GAovo')
    parser.add_argument("--C", help="C penalty for svm", default=10., type=float)
    parser.add_argument("--alphaG", help="minimum win margin for gallery", default=0.5, type=float)
    parser.add_argument("--alphaP", help="minimum win margin for probe", default=1., type=float)
    parser.add_argument("--E", help="score exponential ", default=0, type=float)
    parser.add_argument("--K", help="number of tournaments", default=10, type=int)
    parser.add_argument("--nthreads", help="number of threads for multiproce", default=8, type=int)
    parser.add_argument("--fitbias", help="fit intercept on svms", default=False, action='store_true')
    parser.add_argument("--addbias", help="add intercept on svm testing", default=False, action='store_true')
    parser.add_argument("--cache_size", help="number of svms to keep in the cache", default=int(1.5e6), type=int)
    parser.add_argument("--debug", help="location of debug dir", default="", type=str)
    parser.add_argument("--do_restricted", help="do a restricted number of probes", default=-1, type=int)
    parser.add_argument("--dry", help="don't save the results", default=False, action='store_true')
    parser.add_argument("--serial", help=" dont run in parallel", default=False, action='store_true')
    parser.add_argument("--detailed_string", help=" svm string includes hyperparameters", default=True, action='store_true')
    args = parser.parse_args()

    svm_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'ovo_svm')
    bobo.util.remkdir(svm_path)
    encodings_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'sighting_encodings')
    jitter_mtx_file = os.path.join(encodings_path, '%s_%s_%s.mtx' % (args.model,
                                                                     args.dataset, 'centercrop_5-test-jitter')) if '-test-jitter' in args.jittering else None
    encodings_mtx_file = os.path.join(encodings_path, '%s_%s_%s.mtx' % (args.model, args.dataset, 'centercrop'))

    probe_adaptation = True

    if 'test-jitter' in args.jittering:
        jitter_mtx_file = os.path.join(encodings_path, '%s_%s_%s.mtx' % (args.model, args.dataset, args.jittering))
        encodings_og_suffix = '_'.join(args.jittering.split('_')[0: 1])
        augment_media = args.dual_jittering
        media_suffix = 'media_dual' if args.dual_jittering else 'media'
    else:
        jitter_mtx_file = None
        encodings_og_suffix = args.jittering
        augment_media = False
        media_suffix = 'media'
    mtxfile = os.path.join(encodings_path, '%s_%s_%s.mtx' % (args.model, args.dataset, encodings_og_suffix))

    templates_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, '%s_%s_%s_templates.pk' % (args.model, args.dataset,
                                                                                                          args.jittering))

    with open(templates_dic_path, 'rb') as templates_file:
        print "Opening gallery templates from ", templates_dic_path
        templates_dic = dill.load(templates_file)
    results_dic = {}

    protocol = args.protocol
    retrain = True; n_threads = args.nthreads
    fit_bias = args.fitbias; add_bias = args.addbias
    C = args.C; tournaments = args.K; E = args.E
    alpha = args.alphaP if probe_adaptation else args.alphaG
    max_cache_size = args.cache_size

    ranked_negatives_path = os.path.join(svm_path,
                                         '%s_tmpl_%s_%s_hard_negatives.pk' % (args.model, args.jittering, args.split))
    print("Computing hard negatives and placing results in %s" % ranked_negatives_path)

    negatives_mtx_file = os.path.join(janus_root, 'checkpoints', 'str_broadface', 'str_broadface_resnet101_msceleb1m_14APR17.mtx')
    G, Gid, Gc = zip(*templates_dic[args.split])
    N = readbinary(negatives_mtx_file).astype(np.float)
    strface = STRface(janus_data)
    str_templates = strface.all_templates()
    Nc = [tmpl.category() for tmpl in str_templates]
    start = 0; end = args.do_restricted if args.do_restricted > 0 else len(N)
    debug_path = args.debug if args.debug != "" else None

    ovo_engn = ComputeHardGalleryNegatives(tournaments=tournaments, C=C, threads=n_threads, E=E,
                                           alpha=alpha, fit_bias=fit_bias, award_points=False,
                                           max_cache_size=max_cache_size, debug_dic_path=debug_path,
                                           add_bias=add_bias, serial=args.serial)
    start_t = time.time()

    (ranked_negatives, Yh, ordered_cats, Gid_out) = ovo_engn.evaluate(G=G[start: end], Gc=Gc[start: end],
                                                                      Gid=Gid[start: end], N=N, Nc=Nc)
    end_t = time.time()

    print "Total trained svms: %s and total cache hits %s in %s m" % (ovo_engn._svms_trained.value, ovo_engn._cache_hits.value, (end_t - start_t) / 60.)

    with open(ranked_negatives_path, 'wb') as f:
        dill.dump((ranked_negatives, Gid_out), f)
