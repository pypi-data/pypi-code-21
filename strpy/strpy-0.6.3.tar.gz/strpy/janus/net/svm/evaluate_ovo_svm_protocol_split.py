import janus.net.svm
import os
import numpy as np
from janus.net.svm.govo import TournamentOvOSVM
from janus.net.svm.povo import ProbeOvOSvm
from janus.dataset.strface import STRface
from janus.openbr import readbinary
from janus.dataset.csN import Protocols
from janus.net.csN_evaluation_utils import compute_csN_media, csN_pool_media_into_templates
import bobo.util
import shutil
import dill
import time
import argparse
import subprocess


def compute_hard_gallery_negatives(args):
    py_compute_hard_negatives = os.path.join(os.environ.get('JANUS_SOURCE'),
                                             'python', 'janus', 'net', 'svm',
                                             'compute_hard_gallery_negatives.py')

    exec_args = ['python', py_compute_hard_negatives,
                 '--model', args.model,
                 '--split', args.split,
                 '--dataset', args.dataset,
                 '--jittering', args.jittering,
                 '--C', str(args.C),
                 '--E', str(args.E),
                 '--alphaG', str(0.0),
                 '--alphaP', str(0.0),
                 '--K', str(30),
                 '--cache_size', str(args.cache_size),
                 '--nthreads', str(args.nthreads)
                 ]
    if fit_bias:
        exec_args.append('--fitbias')
    if add_bias:
        exec_args.append('--addbias')
    if args.serial:
        exec_args.append('--serial')
    if args.debug is not None:
        exec_args += ['--debug', args.debug]

    subprocess.call(exec_args)


if __name__ == '__main__':

    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')

    parser = argparse.ArgumentParser(description=" parse ovo run")

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
    parser.add_argument("--H", help="number of hard negatives to use", default=10, type=int)
    parser.add_argument("--nthreads", help="number of threads for multiproce", default=8, type=int)
    parser.add_argument("--fitbias", help="fit intercept on svms", default=False, action='store_true')
    parser.add_argument("--addbias", help="add intercept on svm testing", default=False, action='store_true')
    parser.add_argument("--awardpoints", help="award points instead of margins", default=False, action='store_true')
    parser.add_argument("--cache_size", help="number of svms to keep in the cache", default=int(1.5e6), type=int)
    parser.add_argument("--debug", help="location of debug dir", default="", type=str)
    parser.add_argument("--do_restricted", help="do a restricted number of probes", default=-1, type=int)
    parser.add_argument("--dry", help="don't save the results", default=False, action='store_true')
    parser.add_argument("--serial", help=" dont run in parallel", default=False, action='store_true')
    parser.add_argument("--detailed_string", help=" svm string includes hyperparameters", default=False, action='store_true')
    parser.add_argument("--redo_media", help=" recompute media and store it in dics", default=False, action='store_true')
    args = parser.parse_args()
    svm_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'ovo_svm')
    encodings_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'sighting_encodings')

    dual_string = 'dual' if args.dual_jittering else 'nDual'
    experiment_string = '%s_%s_gNeg_%s' % (args.dataset, args.svm, dual_string)

    probe_adaptation = args.svm == 'PAovo'

    current_protocols = Protocols(janus_data)
    probe_protocols, gallery_splits = zip(*current_protocols.get_1N_protocol_ids(args.dataset))

    probe_protocols = list(set(probe_protocols))  # deduplicate probe protocols
    gallery_splits = list(set(gallery_splits))  # deduplicate gallery splits

    if args.protocol not in probe_protocols:
        print("protocol %s is not one of the valid protocols" % args.protocol, probe_protocols)
        exit();
    if args.split not in gallery_splits:
        print("split %s is not one of the valid splits" % args.split, gallery_splits)
        exit();

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

    media_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, '%s_%s_%s_%s.pk' % (args.model, args.dataset,
                                                                                               args.jittering, media_suffix))
    templates_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, '%s_%s_%s_templates.pk' % (args.model, args.dataset,
                                                                                                         args.jittering))
    # Load media
    if os.path.isfile(media_dic_path) and not args.redo_media:
        with open(media_dic_path, 'rb') as f:
            media_dic = dill.load(f)
            f.close()
    else:
        media_dic = compute_csN_media(mtxfile, args.dataset, jitter_mtx_file=jitter_mtx_file,
                                      augment_media=augment_media)
        if media_dic is None:
            exit();

        with open(media_dic_path, 'wb') as f:
            dill.dump(media_dic, f)
    # Load templates
    if os.path.isfile(templates_dic_path) and not args.redo_media:
        with open(templates_dic_path, 'rb') as f:
            templates_dic = dill.load(f)
    else:
        templates_dic = compute_csN_templates(mtxfile, args.dataset)
        if templates_dic is None:
            exit();
        with open(templates_dic_path, 'wb') as f:
            dill.dump(templates_dic, f)

    retrain = True; n_threads = args.nthreads
    fit_bias = args.fitbias; add_bias = args.addbias
    C = args.C; tournaments = args.K; E = args.E
    alpha = args.alphaP if probe_adaptation else args.alphaG
    max_cache_size = args.cache_size

    svm_string = experiment_string
    if fit_bias and not add_bias:
        svm_string += '_B-'
    elif fit_bias and add_bias:
        svm_string += '_B+'
    if C != 10:
        svm_string += '_C%s' % C
    svm_string += '_K%s' % tournaments
    svm_string += '_A%s' % alpha
    if args.awardpoints:
        svm_string += 'pt'
    else:
        svm_string += 'mg'
    if E != 0.0:
        svm_string += '_E%s' % E
    results_base = os.path.join(janus_root, 'results', args.dataset, 'ovo_partial')
    final_experiment_string = svm_string if args.detailed_string else experiment_string
    final_experiment_string += '_tmpl'  # svms are always evaluated against template features
    results_dic_path = os.path.join(results_base,
                                    '%s_%s_%s_%s_%s_results.pk' % (args.model, final_experiment_string,
                                                                   args.jittering, args.protocol, args.split))
    bobo.util.remkdir(results_base)

    if not args.dry:
        print "saving results in ", results_dic_path
    else:
        print "Dry Run! NOT saving results in ", results_dic_path

    debug_path = args.debug if args.debug != "" else None
    results_dic = {}
    if not probe_adaptation:
        G, Gid, Gc = zip(*media_dic[args.split])  # Train on gallery media
        P, Pid, Pc = zip(*templates_dic[args.protocol])  # Evaluate on probe templates
        start = 0; end = args.do_restricted if args.do_restricted > 0 else len(P)

        ovo_engn = TournamentOvOSVM(tournaments=tournaments, C=C, threads=n_threads, E=E,
                                    alpha=alpha, fit_bias=fit_bias, award_points=args.awardpoints,
                                    max_cache_size=max_cache_size, debug_dic_path=debug_path,
                                    add_bias=add_bias, use_fast_cache=True, serial=args.serial)
        start_t = time.time()

        (Y, Yh, ordered_cats, Pid_out) = ovo_engn.evaluate(P=P[start: end], Pc=Pc[start: end],
                                                           Pid=Pid[start: end], G=G, Gc=Gc, Gid=Gid)
        end_t = time.time()

        print "Total trained svms: %s and total cache hits %s in %s m" % (ovo_engn._svms_trained.value, ovo_engn._cache_hits.value, (end_t - start_t) / 60.)
    else:
        G, Gid, Gc = zip(*templates_dic[args.split])
        P, Pid, Pc = zip(*media_dic[args.protocol])
        start = 0; end = args.do_restricted if args.do_restricted > 0 else len(P)
        negatives_mtx_file = os.path.join(janus_root, 'checkpoints', 'str_broadface', 'str_broadface_resnet101_msceleb1m_14APR17.mtx')
        ranked_negatives_path = os.path.join(svm_path,
                                             '%s_tmpl_%s_%s_hard_negatives.pk' % (args.model, args.jittering, args.split))
        if not os.path.isfile(ranked_negatives_path):
            print " No hard negatives on disk in ", ranked_negatives_path
            compute_hard_gallery_negatives(args)
        with open(ranked_negatives_path, 'rb') as f:
            ranked_negatives, Gid_negs = dill.load(f)
            print " Loaded hard negatives from ", ranked_negatives_path

        N = readbinary(negatives_mtx_file).astype(np.float)
        strface = STRface('/data/janus')
        str_templates = strface.all_templates()
        Nc = [tmpl.category() for tmpl in str_templates]
        ovo_engn = ProbeOvOSvm(tournaments=tournaments, C=C, threads=n_threads,
                               alpha=alpha, fit_bias=fit_bias,
                               add_bias=add_bias, serial=args.serial)
        start_t = time.time()

        (Y, Yh, ordered_cats, Pid_out) = ovo_engn.evaluate(P[start: end], Pid[start: end], Pc[start: end],
                                                           G, Gid, Gc, Nc, N,
                                                           ranked_negatives, Gid_negs, args.H)
        end_t = time.time()
        print "Finished probe adaptation in %s" % ((end_t - start_t) / 60.)

    results_dic['%s--%s' % (args.protocol, args.split)] = (Y, Yh, Pid_out, ordered_cats)
    assert(len(Pid_out) == Yh.shape[0])
    if not args.dry:
        with open(results_dic_path, 'wb') as f:
            dill.dump(results_dic, f)
