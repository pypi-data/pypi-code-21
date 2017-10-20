from janus.dataset.csN import Protocols
import os
from bobo.linalg import row_normalized
from bobo.linalg import row_normalized
from bobo.geometry import sqdist
import janus.metrics
from janus.openbr import readbinary, writebinary
import numpy as np
import itertools
#from functools import reduce


def compute_csN_templates(mtxfile, dataset_str):
    F = readbinary(mtxfile)

    janus_data = os.environ.get('JANUS_DATA')
    current_protocols = Protocols(janus_data)
    S = current_protocols.all_sightings(dataset_str)
    if len(S) != F.shape[0]:
        print("The number of sightings in dataset str %s is %s while the size of file %s is %s " % (dataset_str, len(S), mtxfile, F.shape[0]))
        return None
    sightingid_to_index = {im.attributes['SIGHTING_ID']: k for (k, im) in enumerate(S)}

    templates_dic = current_protocols.get_templates(dataset_str)
    unique_func = current_protocols.unique_funcs[dataset_str]
    sightingid_to_index = {unique_func(im): k for (k, im) in enumerate(S)}

    template_encodings_dic = {protocol_key: [] for protocol_key in templates_dic}
    for protocol_key in templates_dic:
        T = templates_dic[protocol_key]
        X = np.zeros((len(T), F.shape[1]))
        for (k, tmpl) in enumerate(T):  # templates
            for m in tmpl:  # media in templates
                for im in m:  # frames/images in media
                    key = unique_func(im)
                    if key not in sightingid_to_index:
                        print im, " is not in sid list with attributes %s" % key
                    else:
                        X[k, :] += (1.0 / float(len(m))) * F[sightingid_to_index[key], :]
        X = row_normalized(X)

        category = [t.category() for t in T]
        template_id = [t.templateid() for t in T]
        template_encodings_dic[protocol_key] = zip(X, template_id, category)

    return template_encodings_dic


def compute_csN_media(mtxfile, dataset_str, jitter_mtx_file=None, augment_media=False, save_media_ids=False, unit_normalize=True):
        E = None
        F = readbinary(mtxfile)
        if jitter_mtx_file is not None and os.path.isfile(jitter_mtx_file):
            print "Using test jitter mtx file", jitter_mtx_file
            E = readbinary(jitter_mtx_file)
            diff = np.linalg.norm(E - F, axis=1)
            no_jitter_indeces = np.where(diff == 0.0)[0]

        elif jitter_mtx_file is not None and not os.path.isfile(jitter_mtx_file):
            print "no such file", jitter_mtx_file, " not performing test time jittering"

        if augment_media and E is None:
            print "cannot augment media from jitter file ", jitter_mtx_file
            return None

        janus_data = os.environ.get('JANUS_DATA')
        current_protocols = Protocols(janus_data)
        S = current_protocols.all_sightings(dataset_str)
        sightingid_to_index = {im.attributes['SIGHTING_ID']: k for (k, im) in enumerate(S)}

        templates_dic = current_protocols.get_templates(dataset_str)
        unique_func = current_protocols.unique_funcs[dataset_str]
        sightingid_to_index = {unique_func(im): k for (k, im) in enumerate(S)}

        media_encodings_dic = {protocol_key: [] for protocol_key in templates_dic}

        for protocol_key in templates_dic:  # gallery as media
            T = templates_dic[protocol_key]
            all_encodings = []; all_categories = []; all_media_ids = []; all_template_ids = []
            for tmpl in T:  # templates
                curr_template = []; curr_category = []; curr_media_ids = []
                for k, m in enumerate(tmpl):  # media in templates
                    curr_media_og = []
                    curr_media_jit = []
                    for im in m:  # frames/images in media
                        key = sightingid_to_index[unique_func(im)]
                        curr_media_og.append(F[key, :])  # append feature

                        if E is not None and key not in no_jitter_indeces:
                            curr_media_jit.append(E[key, :])  # append jittered feature if not the same as original

                    curr_template.append(np.mean(np.array(curr_media_og), axis=0))  # pool images into media
                    curr_media_og_size = len(curr_media_og)
                    if len(m) != curr_media_og_size:
                        print "for media %s the len method is %s while the array len is %s" % (m.attributes['SIGHTING_ID'], len(m), len(curr_media_og))
                    curr_media_ids.append(m.attributes['SIGHTING_ID'])  # append media id; these are not unique!
                    if curr_media_jit:
                        # normalize by original media size so that the jitters don't dominate the original media
                        curr_media_jit_np = np.sum(np.array(curr_media_jit), axis=0) / curr_media_og_size
                        if augment_media:
                            #  Augment the current template with extra jittered media; No merging performed
                            curr_template.append(curr_media_jit_np)
                            curr_media_ids.append(m.attributes['SIGHTING_ID'] + '_jit')  # keep track of the media ids
                        else:
                            # absorb the jittered media into the original one and average it
                            curr_template[-1] = (curr_template[-1] + curr_media_jit_np) / 2

                all_encodings += curr_template
                all_media_ids += curr_media_ids
                all_template_ids += [tmpl.templateid()] * len(curr_template)
                all_categories += [tmpl.category()] * len(curr_template)

            X = np.array(all_encodings)
            if unit_normalize:
                X = row_normalized(X)
            if save_media_ids:
                media_encodings_dic[protocol_key] = zip(X, all_template_ids, all_categories, all_media_ids)
            else:
                media_encodings_dic[protocol_key] = zip(X, all_template_ids, all_categories)
            print "protocol", protocol_key, " has ", len(X), " media"

        return media_encodings_dic


def csN_pool_media_into_templates(media_dic, dataset_str):
    janus_data = os.environ.get('JANUS_DATA')
    current_protocols = Protocols(janus_data)
    templates_dic = current_protocols.get_templates(dataset_str)
    unique_func = current_protocols.unique_funcs[dataset_str]
    template_encodings_dic = {protocol_id: None for protocol_id in media_dic}
    for protocol_id in media_dic:
        X, Xid, Xc = zip(*media_dic[protocol_id])
        assert(len(X) == len(Xc))
        assert(len(Xid) == len(Xc))

        if protocol_id not in template_encodings_dic:
            print("protocol %s is not valid for dataset %s" % (protocol_id, dataset_str))
        template_encodings_dic[protocol_id] = map(lambda (tid, (feat, cat)): (feat, tid, cat),  # (tid, (feat, cat) ) --> (feat, tid, cat)
                                                  [(k, reduce(lambda x, y: (x[0] + y[0], x[1]),
                                                              [(feature, category) for (feature, tid, category) in list(v)]))  # ([(tid, (feat, category)), ..])
                                                   for (k, v) in itertools.groupby(media_dic[protocol_id], key=lambda md: md[1])])  # (tid: [(feat, category),..,])
        for (feat, tid, cat) in template_encodings_dic[protocol_id]:
            feat /= np.linalg.norm(feat)

        T, Tid, Tc = zip(*template_encodings_dic[protocol_id])
        assert(len(T) == len(templates_dic[protocol_id]))
        # the template cateogries from the pooled set has to be the same as the ones from the metadatas if pooling is correct
        assert(set(Tc) == set([t.category() for t in templates_dic[protocol_id]]))
    return template_encodings_dic


def csN_evaluation(mtxfile, templates_dic_path, dataset_str, redo_templates=False,
                   cmcFigure=3, detFigure=4, prependToLegend='', hold=False, output_splitfile='', splitmean=False,
                   detLegendSwap=False, cmcLegendSwap=False, cmcMinY=0.0, metrics=True):

    janus_data = os.environ.get('JANUS_DATA')
    current_protocols = Protocols(janus_data)
    (Y_all, Yhat_all) = ([], [])
    protocol_pairs = current_protocols.get_1N_protocol_ids(dataset_str)
    if os.path.isfile(templates_dic_path) and not redo_templates:
        print "Loading from file ", templates_dic_path
        import dill
        with open(templates_dic_path, 'rb') as f:
            templates_dic = dill.load(f)
    else:
        templates_dic = compute_csN_templates(mtxfile, dataset_str)
        if templates_dic is not None:
            if os.path.isfile(templates_dic_path):
                with open(templates_dic_path, 'wb') as f:
                    import dill
                    dill.dump(templates_dic, f)
        else:
            print "Invalid template features; Stopping 1:N evaluation"
            return None

    results_dic = {'%s--%s' % (tup[0], tup[1]): [] for tup in protocol_pairs}
    print protocol_pairs
    for protocol_index, (p_str, g_str) in enumerate(protocol_pairs):
        X, Pid, Pc = zip(*templates_dic[p_str])
        Y, Gid, Gc = zip(*templates_dic[g_str])
        yhat = - sqdist(X, Y)
        y = np.array([p_cat == g_cat
                      for (p_cat, g_cat) in itertools.product(Pc, Gc)]).astype(np.float32).reshape(len(Pc), len(Gc))
        results_dic['%s--%s' % (p_str, g_str)] = (y, yhat, Pid, Gc)
        Y_all.append(y)
        Yhat_all.append(yhat)

        if metrics and not splitmean:
            print "========= Results for protocol %s vs %s =========" % (p_str, g_str)
            janus.metrics.ijba1N(y, yhat,
                                 cmcFigure=cmcFigure, detFigure=detFigure, splitmean=False,
                                 prependToLegend='%s--%s' % (p_str, g_str), detLegendSwap=detLegendSwap,
                                 cmcLegendSwap=cmcLegendSwap, hold=hold, cmcMinY=cmcMinY)
    if splitmean:
        print "========= Results for dataset %s =========" % dataset_str
        janus.metrics.ijba1N(Y_all, Yhat_all,
                             cmcFigure=cmcFigure, detFigure=detFigure, splitmean=True,
                             prependToLegend='%s--%s' % (p_str, g_str), detLegendSwap=detLegendSwap,
                             cmcLegendSwap=cmcLegendSwap, hold=hold, cmcMinY=cmcMinY)

    return results_dic
