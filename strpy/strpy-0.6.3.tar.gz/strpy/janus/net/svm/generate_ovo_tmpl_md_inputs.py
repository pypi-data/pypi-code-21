from multiprocessing import Process, Lock
from multiprocessing.sharedctypes import Value, Array
from ctypes import Structure, c_double
import dill
import os
janus_root = os.environ.get('JANUS_ROOT')
janus_data = os.environ.get('JANUS_DATA')

experiments = [
        ['resnet101_msceleb1m_14APR17', 'cs3_GAovo_gNeg_nDual', 'centercrop', 'GA-centercrop'],
        ['resnet101_msceleb1m_14APR17', 'cs3_GAovo_gNeg_dual', 'centercrop_5-test-jitter', 'GA-centercrop'],
    ]


experiment = experiments[0]
augment_media = True if 'dual' in experiment[1] else False
media_suffix = 'media_dual' if augment_media else 'media'
gallery_adaptation = True

media_dic_path = os.path.join(janus_root, 'checkpoints/cs4/%s_cs4_%s_%s.pk' % (experiment[0], experiment[2], media_suffix))
template_dic_path = os.path.join(janus_root, 'checkpoints/cs4/%s_cs4_%s_templates.pk' % (experiment[0], experiment[2]))
with open(media_dic_path, 'rb') as f:
    media_dic = dill.load(f)

with open(template_dic_path, 'rb') as f:
    template_dic = dill.load(f)

if gallery_adaptation:

    output_dic_path = os.path.join(janus_root, 'checkpoints/cs4/%s_cs4_%s_Gmedia_Ptemplates.pk' % (experiment[0], experiment[2]))


    output_dic = {'P_mixed': template_dic['P_mixed'],
                   'G_S1': media_dic['G_S1'],
                   'G_S2': media_dic['G_S2']}
    with open(output_dic_path, 'wb') as f:
        dill.dump(output_dic, f)
else:

    output_dic_path = os.path.join(janus_root, 'checkpoints/cs4/%s_cs4_%s_Gtemplates_Pmedia.pk' % (experiment[0], experiment[2]))


    output_dic = {'P_mixed': media_dic['P_mixed'],
                   'G_S1': template_dic['G_S1'],
                   'G_S2': template_dic['G_S2']}
    with open(output_dic_path, 'wb') as f:
        dill.dump(output_dic, f)
