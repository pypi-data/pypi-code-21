import os.path
import dill
import argparse
from janus.dataset.csN import Protocols
import subprocess
import itertools
import numpy as np
if __name__ == '__main__':

    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')
    janus_source = os.environ.get('JANUS_SOURCE')
    # default params
    fit_bias = True; add_bias = False; award_points = False; detailed_string = False
    C = 10; K = 10; E = 3.; H = 5
    alphaP = 0.0; alphaG = 0.0
    cache_size = int(1e6)

    parser = argparse.ArgumentParser(description=" parse ovo run")

    parser.add_argument("--model", help="name of the model to test", default='resnet101_msceleb1m_14APR17')
    parser.add_argument("--protocol", help="split", default="all")
    parser.add_argument("--split", help="split", default="all")
    parser.add_argument("--nthreads", help="Number of spark jobs", default=8)
    parser.add_argument("--dataset", help="name of the dataset to test on", choices=['cs2', 'cs3', 'cs4', 'ijba', 'ijbb'], default='cs4')
    parser.add_argument("--jittering", help="type of jittering found in encodings",
                        choices=['centercrop', 'centercrop_5-test_jitter', 'frcnn_centercrop'], default='centercrop')
    parser.add_argument("--svm", help="type of svm to train", choices=['GAovo', 'PAovo', 'TAovo'], default='TAovo')
    parser.add_argument("--dual_jittering", help="treat jittered media if any as individual samples", action="store_true", default=False)
    parser.add_argument("--force", help="retrain svms if already found on disk", action="store_true", default=False)
    parser.add_argument("--dry", help="Do not save eval results to disk", action="store_true", default=False)
    parser.add_argument("--test_templates", help="Evaluate svms on templates rather than individual media", action="store_true", default=True)

    args = parser.parse_args()
    current_protocols = Protocols(janus_data)
    protocol_pairs = current_protocols.get_1N_protocol_ids(args.dataset)
    results_base = os.path.join(janus_root, 'results', args.dataset, 'ovo_partial')
    dual_string = 'dual' if args.dual_jittering else 'nDual'
    py_ovo_exec = os.path.join(janus_source,
                               'python', 'janus', 'net', 'svm',
                               'evaluate_ovo_svm_protocol_split.py')
    results_dic = {'%s--%s' % (p, g): None for (p, g) in protocol_pairs}
    final_experiment_string = '%s_%s_gNeg_%s_tmpl' % (args.dataset, args.svm, dual_string)
    results_dic_path = os.path.join(janus_root, 'results', args.dataset, '%s_%s_%s_results.pk' % (args.model, final_experiment_string, args.jittering))
    print("Placing results in %s" % results_dic_path)
    for (p_str, g_str) in protocol_pairs:
        svm_type = [args.svm] if args.svm != 'TAovo' else ['GAovo', 'PAovo']
        for svm_t in svm_type:
            experiment_string = '%s_%s_gNeg_%s_tmpl' % (args.dataset, svm_t, dual_string)
            cur_results_dic_path = os.path.join(results_base,
                                                '%s_%s_%s_%s_%s_results.pk' % (args.model, experiment_string,
                                                                               args.jittering, p_str, g_str))
            if os.path.exists(cur_results_dic_path) and not args.force:
                print("Results for experiment [%s]: (%s, %s) already exist in %s" % (svm_t, p_str, g_str, cur_results_dic_path))
                continue;
            exec_args = ['python', py_ovo_exec,
                         '--model', args.model,
                         '--protocol', p_str,
                         '--split', g_str,
                         '--dataset', args.dataset,
                         '--jittering', args.jittering,
                         '--svm', svm_t,
                         '--C', str(C),
                         '--E', str(E),
                         '--alphaG', str(alphaG),
                         '--alphaP', str(alphaP),
                         '--K', str(K),
                         '--H', str(H),
                         '--cache_size', str(cache_size),
                         '--nthreads', str(args.nthreads)
                         ]
            if fit_bias:
                exec_args.append('--fitbias')
            if add_bias:
                exec_args.append('--addbias')
            if award_points:
                exec_args.append('--awardpoints')
            if args.dry:
                exec_args.append('--dry')

            subprocess.call(exec_args)
        # combine results for probe and gallery adaptation
        Pid_final = None
        cats_final = None
        Y_final = None
        Yh_final = None
        for svm_t in svm_type:
            experiment_string = '%s_%s_gNeg_%s_tmpl' % (args.dataset, svm_t, dual_string)
            cur_results_dic_path = os.path.join(results_base,
                                                '%s_%s_%s_%s_%s_results.pk' % (args.model, experiment_string,
                                                                            args.jittering, p_str, g_str))
            with (open(cur_results_dic_path, 'rb')) as f:
                cur_results_dic = dill.load(f)
            Y, Yh, Pid, cats = cur_results_dic['%s--%s' % (p_str, g_str)]
            if type(Yh) != np.ndarray:
                Yh = np.array(Yh)
            if type(Pid) != list:
                Pid = list(Pid)
                cats = list(cats)
                if len(Pid) != Yh.shape[0]:
                    print "Wrong number of Pids compared to the columns of Yh for experiment (%s, %s)" % (p_str, g_str)
            probe_header_dic = {(p, g): (i, j) for i, p in enumerate(Pid) for j, g in enumerate(cats)}
            # this is set once
            if Yh_final is None:
                Pid_final = Pid
                cats_final = cats
                Y_final = Y
                Yh_final = Yh / len(svm_type)
            else:
                Yh_reordered = np.zeros(Yh_final.shape)
                Y_reordered = np.zeros(Y_final.shape)
                assert(len(Pid) == len(Pid_final))
                assert(len(cats) == len(cats_final))
                for i in xrange(0, len(Pid_final)):
                    for j in xrange(0, len(cats_final)):
                        Yh_reordered[i, j] = Yh[probe_header_dic[Pid_final[i], cats_final[j]]]
                        Y_reordered[i, j] = Y[probe_header_dic[Pid_final[i], cats_final[j]]]
                assert((Y_reordered == Y_final).all())
                Yh_final += Yh_reordered / len(svm_type)
        results_dic['%s--%s' % (p_str, g_str)] = (Y_final, Yh_final, Pid_final, cats_final)
    with open(results_dic_path, 'wb') as f:
        dill.dump(results_dic, f)
