import janus.net.svm
import os
import itertools
from janus.net.svm.ovo import TournamentOvOSVM, ProbeOvOSvm
from janus.dataset.cs4 import CS4
from janus.dataset.strface import STRface
from janus.openbr import readbinary
import janus.metrics
import dill
import time
prb_normalize = 1.

def test_inputs(cs4, pids, cats, Y, Yh, split):
    Probe_t = cs4._cs4_1N_probe_mixed()
    dict = {t.templateid(): t.category() for t in Probe_t}
    gallery_t = cs4._cs4_1N_gallery_S1() if split == 'G_S1' else cs4._cs4_1N_gallery_S2()
    correct = True
    for i in xrange(Y.shape[0]):
        j = np.where(Y[i, :] == 1)[0]
        # import pdb

    # pdb.set_trace()
        if j:
            if dict[pids[i]] != cats[j[0]]:
                print " discrepancy found for pid %s and Y cat %s while true cat %s" % (pids[i], cats[j[0]], dict[pids[i]])



if __name__ == '__main__':

    janus_root = os.environ.get('JANUS_ROOT')
    janus_data = os.environ.get('JANUS_DATA')

    input_path = os.path.join(janus_root, 'results/cs4/ovo_partial/')
    output_path = os.path.join(janus_root, 'results/cs4')   #
    cs4 = CS4('/data/janus/')
    PA_string = None
#    GA_string = 'resnet101_msceleb1m_14APR17_cs4_GAovo_svm_B-_K11_A0.0mg_E3.0_tmpl_centercrop'
#    GA_string = 'resnet101_msceleb1m_14APR17_cs4_GAovo_svm_B-_K50_A0.0mg_E3.0_tmpl_centercrop'
#    GA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovo_svm_B-_K11_A0.0mg_E2.0_tmpl_centercrop'
#    PA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovo_svm_B-_K11_A0.0mg_E2.0_tmpl_centercrop'
#    PA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovo_svm_B-_K100_A1.0_tmpl_centercrop'
#    PA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovr_svm_B-_tmpl_centercrop'
    GA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovo_svm_B-_K11_A0.0mg_E2.0_tmpl_centercrop'
    GA_string = 'resnet101_msceleb1m_14APR17_cs4_PAovo_gNeg_nDual_B-_K11_A0.0mg_E2.0_tmpl_centercrop_P_mixed'
    if PA_string is not None:
        parts = PA_string.split('_');
        tourney_string = [part for part in parts if part[0] == 'K'][0][1:]
        output_string = GA_string.replace('GAovo', 'TAovo_N%s' % tourney_string)

    else:
        output_string = GA_string
    output_file = os.path.join(output_path, output_string + '_results.pk')
    print "Saving combined results in ", output_file
    results_dic = {}
    splits = ['G_S1', 'G_S2']
#    splits = ['G_S1']
    protocols = ['P_mixed']
#    probe_templates = cs4._cs4_1N_probe_mixed()
#    Pid2C = {t.templateid(): t.category() for t in probe_templates}
    protocol = protocols[0]
    for split in splits:
        if PA_string is not None:
            with (open(os.path.join(input_path, PA_string + '_%s_results.pk' % split), 'rb')) as f:
                pa_dic = dill.load(f)
        else:
            pa_dic = None
        with (open(os.path.join(input_path, GA_string + '_%s_results.pk' % split), 'rb')) as f:
            ga_dic = dill.load(f)
        Y_g, Yh_g, Pid_g, cats_g = ga_dic['%s--%s' % (protocol, split)]
        test_inputs(cs4, Pid_g, cats_g, Y_g, Yh_g, split)
        if len(Pid_g) != Yh_g.shape[0]:
            print "Wrong number of Pids compared to the columns of Yh"


        if pa_dic is not None:
            Y_p, Yh_p, Pid_p, cats_p = pa_dic['%s--%s' % (protocol, split)]
            test_inputs(cs4, Pid_p, cats_p, Y_p, Yh_p, split)
            if type(Yh_p) != np.ndarray:
                Yh_p = np.array(Yh_p)
            if type(Pid_p) != list:
                Pid_p = list(Pid_p)
                cats_p = list(cats_p)
                if len(Pid_p) != Yh_p.shape[0]:
                    print "Wrong number of Pids compared to the columns of Yh"
            assert(Y_g.shape == Y_p.shape)
            assert(Yh_g.shape == Yh_p.shape)
            probe_header_dic = {(p, g): (i,j) for i,p in enumerate(Pid_p) for j,g in enumerate(cats_p)}
            Yh_p /=prb_normalize

        method2 = True
        if not method2:
            temp_dic = {(pid, gc): 0 for (pid, gc) in itertools.product(Pid_g, cats_g)}
            for i in xrange(0, len(Pid_g)):
                for j in xrange(0, len(cats_g)):
                    pid_g = Pid_g[i]; cat_g = cats_g[j]; yh_g = Yh_g[i, j]
                    temp_dic[(pid_g, cat_g)] += yh_g  # gallery adaptation contribution
                    if pa_dic is not None:
                        pid_p = Pid_p[i]; cat_p = cats_p[j]; yh_p = Yh_p[i, j]
                        temp_dic[(pid_p, cat_p)] += yh_p  # probe adaptation contributiono
            Yh_combined = np.array([temp_dic[pid, cat] for pid in Pid_g for cat in cats_g]).reshape(len(Pid_g), len(cats_g))
        else:
            Yh_p_reordered = np.zeros(Yh_g.shape)
            if pa_dic is not None:
                for i in xrange(0, len(Pid_g)):
                    for j in xrange(0, len(cats_g)):
                        Yh_p_reordered[i, j] = Yh_p[probe_header_dic[Pid_g[i], cats_g[j]]]
            Yh_combined = (Yh_g + Yh_p_reordered) /2

        results_dic['%s--%s' % (protocol, split)] = (Y_g, Yh_combined, Pid_g, cats_g)
        print "GA results:"
        cur_res = janus.metrics.ijba1N(Y_g, Yh_g)
        print "TA results:"
        cur_res = janus.metrics.ijba1N(Y_g, Yh_combined)
        # if method2:
        #     cur_res = janus.metrics.ijba1N(Y_p, Yh_p)
        #     cur_res = janus.metrics.ijba1N(Y_g, Yh_p_reordered)
        if pa_dic is not None:
            bins = np.linspace(-0.75,0.75,100)
            xout_p, nb_p = np.histogram(Yh_p.flatten(), bins = bins)
            xout_g, nb_g = np.histogram(Yh_g.flatten(), bins = bins)
            xout_c, nb_c = np.histogram(Yh_combined.flatten(), bins = bins)
            fig1d=plt.figure()
            bwidth = min([nb_p[1] - nb_p[0], nb_g[1] - nb_g[0], nb_c[1] - nb_c[0]])
            plt.bar((nb_p[0: -1] + nb_p[1:]) / 2, xout_p / np.sum(xout_p).astype(np.float),
                    color='r', width=bwidth, alpha=0.5)
            plt.bar((nb_g[0: -1] + nb_g[1:]) / 2, xout_g / np.sum(xout_g).astype(np.float),
                    color='b', width=bwidth,alpha=0.5)
            # plt.bar((nb_c[0: -1] + nb_c[1:]) / 2, xout_c / np.sum(xout_c).astype(np.float),
            #         color='g', width=bwidth,alpha=0.5)


    with open(output_file, 'wb') as f:
        dill.dump(results_dic, f)
