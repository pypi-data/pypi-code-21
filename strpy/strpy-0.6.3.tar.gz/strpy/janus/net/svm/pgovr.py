import os
from janus.openbr import readbinary, writebinary
from janus.dataset.csN import Protocols
from pyspark import SparkContext
from janus.net.csN_evaluation_utils import compute_csN_media, compute_csN_templates
import dill
from janus.classifier import LinearSVMGalleryAdaptation
from janus.dataset.strface import STRface
import janus.metrics
import bobo.util


def train_ovr_svm_csN(mtxfile, sc, dataset_str, media_dic_path, svm_param_dic_path, redo_media=False, augment_media=False,
                      probeadaptation=False, negative_mtxfile=None, jitter_mtx_file=None, n_partitions=8):

    if not os.path.isfile(negative_mtxfile):
        nF = None
    else:
        nF = readbinary(negative_mtxfile)
    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')

    current_protocols = Protocols(janus_data)
    probe_protocols, gallery_splits = zip(*current_protocols.get_1N_protocol_ids(dataset_str))

    probe_protocols = list(set(probe_protocols))  # deduplicate probe protocols
    gallery_splits = list(set(gallery_splits))  # deduplicate gallery splits

    media_dic = {label: [] for label in probe_protocols + gallery_splits}
    svm_param_dic = {label: [] for label in probe_protocols + gallery_splits}

    if os.path.isfile(media_dic_path) and not redo_media:
        import dill
        with open(media_dic_path, 'rb') as f:
            media_dic = dill.load(f)
            f.close()
    else:
        media_dic = compute_csN_media(mtxfile, dataset_str, jitter_mtx_file=jitter_mtx_file,
                                      augment_media=augment_media)

        with open(media_dic_path, 'wb') as f:
            import dill
            dill.dump(media_dic, f)

    if probeadaptation and nF is None:
        print "Empty negative matrix file!"
        return  None
    trainset = (None, None)
    if probeadaptation:
        strface = STRface(janus_data)
        str_templates = strface.all_templates()
        trainset = ([tmpl.category() for tmpl in str_templates], nF)
        del strface

    template_adaptation = LinearSVMGalleryAdaptation(None)
    for set_str in probe_protocols + gallery_splits:
        if not probeadaptation and set_str in probe_protocols:
            continue;
        use_gallery_negatives = True if set_str in gallery_splits else False
        trainset_cur = (None, None) if set_str in gallery_splits else trainset

        X, X_tid, X_cat = zip(*media_dic[set_str])
        print("Training protocol %s", set_str)
        [Tid, cat, svm] = template_adaptation.train(sc, galleryset=(X_tid, X_cat, X),
                                                    trainset=trainset_cur,
                                                    n_partitions=n_partitions,
                                                    class_method='svm-tne',
                                                    use_gallery_negatives=use_gallery_negatives)
        # Prepare svm dict for testing API
        if set_str in probe_protocols:  # one svm per probe templateID
            svm_param_dic[set_str] = {tid: (c, svm) for (tid, c, svm) in zip(Tid, cat, svm)}
        else:  # one svm per gallery subject
            svm_param_dic[set_str] = {c: (tid, svm) for (tid, c, svm) in zip(Tid, cat, svm)}

        print "Finished training of svms for protocol %s" % set_str
        svm_dir, svm_fname = os.path.split(svm_param_dic_path)
        bobo.util.remkdir(svm_dir)
        with open(svm_param_dic_path, 'wb') as f:
            dill.dump(svm_param_dic, f)


def test_ovr_svm_csN(mtxfile, dataset_str, svm_param_file_path, templates_dic_path, sc, media_dic_path=None,
                     metrics=True, n_partitions=8, do_PA=True, do_GA=True, splitmean=False):

    (Y_all, Yhat_all) = ([], [])
    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')

    current_protocols = Protocols(janus_data)
    protocol_pairs = current_protocols.get_1N_protocol_ids(dataset_str)
    if os.path.isfile(templates_dic_path):
        with open(templates_dic_path, 'rb') as f:
            templates_dic = dill.load(f)
    else:
        templates_dic = compute_csN_templates(mtxfile, dataset_str)
    if os.path.isfile(svm_param_file_path):
        with open(svm_param_file_path, 'rb') as f:
            svm_params = dill.load(f)
    else:
        print "cannot open svm param file ", svm_param_file_path," ; run janus.net.svm.pgovr.train_ovr_svm_csN"
        return None

    results_dic = {'%s--%s' % (tup[0], tup[1]): [] for tup in protocol_pairs}

    template_adaptation = LinearSVMGalleryAdaptation(None)
    for protocol_index, (p_str, g_str) in enumerate(protocol_pairs):

        try:
            X, Pid, Pc = zip(*templates_dic[p_str])
            Y, Gid, Gc = zip(*templates_dic[g_str])
        except ValueError:
            X, Pid, Pc, _ = zip(*templates_dic[p_str])
            Y, Gid, Gc, _ = zip(*templates_dic[g_str])

        #  restructure gallery and probe svms:
        gallery_svms = {cat: svm_params[g_str][cat][1] for cat in svm_params[g_str]} if do_GA else None  # subject:svm

        probe_svms = {tid: svm_params[p_str][tid][1]
                      for tid in svm_params[p_str]} if p_str in svm_params and do_PA else None  # TmplID:svm

        (y, yhat, probes, subjects) = template_adaptation.test(sparkContext=sc, probeset=(Pid, Pc, X),
                                                               galleryset=(Gc, Y),
                                                               gallerysvms=gallery_svms,
                                                               probesvms=probe_svms,
                                                               n_partitions=n_partitions)

        results_dic['%s--%s' % (p_str, g_str)] = (y, yhat, probes, subjects)
        Y_all.append(y)
        Yhat_all.append(yhat)
        if metrics and not splitmean:
            print "========= Results for protocol %s vs %s =========" % (p_str, g_str)
            janus.metrics.ijba1N(y, yhat)

    if metrics and splitmean:
        print "========= Results for protocol %s vs %s =========" % (p_str, g_str)
        janus.metrics.ijba1N(Y_all, Yhat_all)

    return results_dic
