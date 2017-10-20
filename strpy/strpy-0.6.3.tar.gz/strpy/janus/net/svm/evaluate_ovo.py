import janus.net.svm
import os
import subprocess
import argparse
import itertools
import sys

if __name__ == '__main__':

    experiments = [
        ['resnet101_msceleb1m_14APR17', 'GAovo', 'centercrop', 'GA-centercrop'],
        ['resnet101_msceleb1m_14APR17', 'GAovo_dual', 'centercrop_5-test-jitter', 'GA-5J'],
        ['resnet101_msceleb1m_14APR17', 'PAovo', 'centercrop', 'PA-centercrop']
        ]
    exec_name = 'train_test_ovo_svm.py'
    protocols = ['P_mixed']
    splits = ['G_S1', 'G_S2']
#    splits = ['G_S1']
    n_threads = 8
    fit_bias = True; add_bias = False; award_points = False
    C = 10; tournaments = 11; E = 3.
    alphaP = 0.0; alphaG = 0.0
    cache_size = int(1e6)
    curr_experiment = experiments[0]
    probe_l = -1
    default_params = (alphaG, E, tournaments, award_points, C)
    alphaGs = [0.0]
    Ks = [15, 50, 300]
    Es = [3.]
    award_points = [False]
    dry_run = False; serial = False; default_run = True;

    # debug_path = None

    if default_run:
        parameter_vector = [default_params]
    else:
        parameter_vector = []
        for it in itertools.product(alphaGs, Es, Ks, award_points):
            curr_param = (it[0], it[1], it[2], it[3], default_params[4])
            parameter_vector.append(curr_param)

    for protocol in protocols:
        for split in splits:

            for parameter in parameter_vector:
                alphaG = parameter[0]
                E = parameter[1]
                tournaments = parameter[2]
                award_points = parameter[3]
                C = parameter[4]
                debug_path = '/data/janus/debug/ovo/svms%s_%s.pk' % (C, split);

                print "starting run with alphaG=%s; E=%s; K=%s; AP=%s; C=%s" % (alphaG, E, tournaments,
                                                                                award_points, C)
                exec_args = ['python', 'train_test_ovo_svm.py',
                             '--model', curr_experiment[0],
                             '--protocol', protocol,
                             '--split', split,
                             '--dataset', 'cs4',
                             '--jittering', 'centercrop',
                             '--svm', curr_experiment[1],
                             '--C', str(C),
                             '--E', str(E),
                             '--alphaG', str(alphaG),
                             '--alphaP', str(alphaP),
                             '--K', str(tournaments),
                             '--cache_size', str(cache_size),
                             '--do_restricted', str(probe_l)
                             ]
                if fit_bias:
                    exec_args.append('--fitbias')
                if add_bias:
                    exec_args.append('--addbias')
                if award_points:
                    exec_args.append('--awardpoints')
                if dry_run:
                    exec_args.append('--dry')
                if serial:
                    exec_args.append('--serial')
                if debug_path is not None:
                    exec_args += ['--debug', debug_path]

                subprocess.call(exec_args)
