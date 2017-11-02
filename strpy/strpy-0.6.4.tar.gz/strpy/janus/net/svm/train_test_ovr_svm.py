from janus.net.svm.pgovr import train_ovr_svm_csN, test_ovr_svm_csN
from pyspark import SparkContext
import os.path
import dill
import argparse
if __name__ == '__main__':

    sc = SparkContext()
    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')

    parser = argparse.ArgumentParser(description=" parse ovr run")

    parser.add_argument("--model", help="name of the model to test", default='resnet101_msceleb1m_14APR17')
    parser.add_argument("--protocol", help="split", default="all")
    parser.add_argument("--split", help="split", default="all")
    parser.add_argument("--jobs", help="Number of spark jobs", default=8)
    parser.add_argument("--dataset", help="name of the dataset to test on", choices=['cs2', 'cs3', 'cs4', 'ijba', 'ijbb'], default='cs4')
    parser.add_argument("--jittering", help="type of jittering found in encodings",
                        choices=['centercrop', 'centercrop_5-test_jitter', 'frcnn_centercrop'], default='centercrop')
    parser.add_argument("--svm", help="type of svm to train", choices=['GAovr', 'PAovr', 'TAovr'], default='TAovr')
    parser.add_argument("--dual_jittering", help="treat jittered media if any as individual samples", action="store_true", default=False)
    parser.add_argument("--force", help="retrain svms if already found on disk", action="store_true", default=False)
    parser.add_argument("--dry", help="Do not save eval results to disk", action="store_true", default=False)
    parser.add_argument("--test_templates", help="Evaluate svms on templates rather than individual media", action="store_true", default=True)

    args = parser.parse_args()
    svm_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'ovr_svm')
    encodings_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'sighting_encodings')

    dual_string = 'dual' if args.dual_jittering else 'nDual'
    experiment_string = '%s_%s_gNeg_%s' % (args.dataset, args.svm, dual_string)
    if args.test_templates:
        experiment_string += "_tmpl"
    do_probeadaptation = args.svm == 'TAovr' or args.svm == 'PAovr'
    do_galleryadaptation = args.svm == 'TAovr' or args.svm == 'GAovr'
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

    if 'vggface' in args.model:
        negatives_mtx_file = os.path.join(janus_root, 'checkpoints', 'str_broadface', 'str_broadface_vggface_05JUN16.mtx')
    else:
        negatives_mtx_file = os.path.join(janus_root, 'checkpoints', 'str_broadface', 'str_broadface_resnet101_msceleb1m_19MAR17.mtx')

    media_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, '%s_%s_%s_%s.pk' % (args.model, args.dataset,
                                                                                               args.jittering, media_suffix))
    template_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, '%s_%s_%s_templates.pk' % (args.model, args.dataset,
                                                                                                         args.jittering))

    results_dic_path = os.path.join(janus_root, 'results', args.dataset, '%s_%s_%s_results.pk' % (args.model, experiment_string, args.jittering))
    mtxfile = os.path.join(encodings_path, '%s_%s_%s.mtx' % (args.model, args.dataset, encodings_og_suffix))
    print 'Loading encodings from ', mtxfile
    svm_dic_path = os.path.join(janus_root, 'checkpoints', args.dataset, 'ovr_svm', '%s_%s_svms_%s.pk' % (args.model, args.jittering, experiment_string))
    print "loading media from", media_dic_path

    if not os.path.isfile(svm_dic_path) and os.path.isfile(mtxfile) or args.force:
        print "Re-evaluating and saving svms in", svm_dic_path
        train_ovr_svm_csN(mtxfile, sc, args.dataset, media_dic_path, svm_dic_path, redo_media=True,
                          augment_media=args.dual_jittering, jitter_mtx_file=jitter_mtx_file,
                          probeadaptation=do_probeadaptation, negative_mtxfile=negatives_mtx_file, n_partitions=args.jobs)
    "Testing svms in", svm_dic_path
    test_path = template_dic_path if args.test_templates else media_dic_path
    results_dic = test_ovr_svm_csN(mtxfile, args.dataset, svm_dic_path, test_path, sc, n_partitions=args.jobs,
                                   do_PA=do_probeadaptation, do_GA=do_galleryadaptation)
    if results_dic is not None and not args.dry:
        print "placing results in ", results_dic_path
        with open(results_dic_path, 'wb') as f:
            dill.dump(results_dic, f)
    else:
        print " Dry run; Not saving in  ", results_dic_path
