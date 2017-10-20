from pyspark import SparkContext
import os.path
import dill
from janus.net.cs4_evaluation_utils import compute_cs4_media, compute_cs4_templates
from janus.net.cs3_evaluation_utils import compute_cs3_media, compute_cs3_templates
import itertools
from janus.dataset.cs2 import CS2, uniq_cs2_id
from janus.dataset.cs3 import CS3, uniq_cs3_id
from janus.dataset.cs4 import CS4, uniq_cs4_id
from janus.dataset.IJB_A import IJBA_1N, uniq_ijba_id
from janus.dataset.IJB_B import IJBB, uniq_ijbb_id
from janus.dataset.strface import STRface, uniq_strface_id
janus_root = os.environ.get('JANUS_ROOT')
janus_data = os.environ.get('JANUS_DATA')
from bobo.util import setverbosity
setverbosity(3)

class Protocols():
    def __init__(self, dataset_root):
        self.cs2 = CS2(dataset_root)
        self.cs3 = CS3(dataset_root)
        self.cs4 = CS4(dataset_root)
        self.ijba = IJBA_1N(dataset_root)
        self.ijbb = IJBB(dataset_root)
        self.str = STRface(dataset_root)
        self.dataset_root = dataset_root
        self._cs3_templates = {'P_img': [], 'P_mixed': [], 'G_S1': [], 'G_S2': []}
        self._cs4_templates = {'P_mixed': [], 'G_S1': [], 'G_S2': []}
        self._ijbb_templates = {'P_img': [], 'P_mixed': [], 'G_S1': [], 'G_S2': []}
        self._str_templates = {'N': []}
        self._cs2_templates = {protocol_or_split:
                               [] for protocol_or_split in ['P_S%s' % split for split in range(1, 11)] + ['G_S%s' % split for split in range(1, 11)]}
        self._ijba_templates = dict(self._cs2_templates)

        self._datasets = {'cs2': self.cs2, 'cs3': self.cs3, 'cs4': self.cs4,
                          'ijba': self.ijba, 'ijbb': self.ijbb, 'strface': self.str}
        self.unique_funcs = {'cs2': uniq_cs2_id, 'cs3': uniq_cs2_id, 'cs4': uniq_cs4_id,
                             'ijba': uniq_ijba_id, 'ijbb': uniq_ijbb_id, 'strface': uniq_strface_id}
        self._templates = {'cs2': self._cs2_templates, 'cs3': self._cs3_templates,
                           'cs4': self._cs4_templates,
                           'ijba': self._ijba_templates, 'ijbb': self._ijbb_templates, 'strface': uniq_strface_id}
        self._loaded = {'cs2': False, 'cs3': False, 'cs4': False,
                        'ijba': False, 'ijbb': False, 'strface': False}


    def _load_templates(self, dataset_str):
        if dataset_str not in self._datasets.keys():
            print dataset_str, " is not in available datasets ", self._datasets
            return None
        if dataset_str == 'cs2' or dataset_str == 'ijba':
            probe_string = 'probe' if dataset_str == 'cs2' else 'search_probe'
            gallery_string = 'gallery'if dataset_str == 'cs2' else 'search_gallery'
            cs2_like = self.cs2 if dataset_str == 'cs2' else self.ijba
            template_dic = self._cs2_templates if dataset_str == 'cs2' else self._ijba_templates
            for s in xrange(1, 11):
                P = cs2_like.as_templates(probe_string, s)
                G = cs2_like.as_templates(gallery_string, s)
                template_dic['P_S%s' % s] = P
                template_dic['G_S%s' % s] = G
        elif dataset_str == 'cs3':
            self._cs3_templates['P_img'] = self.cs3._cs3_1N_probe_img()
            self._cs3_templates['P_mixed'] = self.cs3._cs3_1N_probe_mixed()
            self._cs3_templates['G_S1'] = self.cs3._cs3_1N_gallery_S1()
            self._cs3_templates['G_S2'] = self.cs3._cs3_1N_gallery_S2()
        elif dataset_str == 'ijbb':
            self._ijbb_templates['P_img'] = self.ijbb._ijbb_1N_probe_img()
            self._ijbb_templates['P_mixed'] = self.ijbb._ijbb_1N_probe_mixed()
            self._ijbb_templates['G_S1'] = self.ijbb._ijbb_1N_gallery_S1()
            self._ijbb_templates['G_S2'] = self.ijbb._ijbb_1N_gallery_S2()
        elif dataset_str == 'cs4':
            self._cs4_templates['P_mixed'] = self.cs4._cs4_1N_probe_mixed()
            self._cs4_templates['G_S1'] = self.cs4._cs4_1N_gallery_S1()
            self._cs4_templates['G_S2'] = self.cs4._cs4_1N_gallery_S2()
        elif dataset_str == 'strface':
            self._str_templates = self.str.all_templates()

    def get_1N_protocol_ids(self, dataset_str):
        if dataset_str not in self._datasets.keys():
            print dataset_str, " is not in available datasets ", self._datasets.keys()
            return None

        if dataset_str == 'cs2' or dataset_str == 'ijba':
            return [('P_S%i' % s, 'G_S%i' % s) for s in xrange(1, 11)]
        elif dataset_str == 'cs3' or dataset_str == 'ijbb':
            return [(p, s) for (p, s) in itertools.product(['P_img', 'P_mixed'], ['G_S1', 'G_S2'])]
        elif dataset_str == 'cs4':
            return [(p, s) for (p, s) in itertools.product(['P_mixed'], ['G_S1', 'G_S2'])]

    def get_templates(self, dataset_str):
        if dataset_str not in self._datasets:
            print dataset_str, " is not in available datasets ", self._datasets.keys()
            return None
        if not self._loaded[dataset_str]:
            self._load_templates(dataset_str)
            self._loaded[dataset_str] = True
        return self._templates[dataset_str]

    def get_subject_names(self, dataset_str):
        if dataset_str not in self._datasets:
            print dataset_str, " is not in available datasets ", self._datasets.keys()
            return None
        if dataset_str == 'cs2':
            subj_dic = self._datasets[dataset_str].subject_id()
            return subj_dic
        elif dataset_str == 'cs3':
            subject_name_csv = os.path.join(self._datasets[dataset_str].datadir, '%s_subject_names.txt' % dataset_str)
        elif dataset_str == 'ijbb':
            subject_name_csv = os.path.join(self._datasets[dataset_str].datadir, 'protocol', '%s_subject_names.csv' % dataset_str)
        elif dataset_str == 'cs4':
            subject_name_csv = os.path.join(self._datasets[dataset_str].datadir, '%s_subject_names.csv' % dataset_str)
        else:
            print "Subject dictionary not supported for ", dataset_str
            return None
        if not os.path.isfile(subject_name_csv):
            print "Could not open", subject_name_csv
            return None
        subj_dic = None
        with open(subject_name_csv, 'r') as f:
            subj_dic = {'%04d' % int(row.split(',')[0]): (row.split(',')[1].strip()).decode('utf-8') for row in f.readlines()[1:]}
        return subj_dic


    def all_sightings(self, dataset_str):
        if dataset_str not in self._datasets:
            print dataset_str, " is not in available datasets ", self._datasets.keys()
            return None
        sightings = self._datasets[dataset_str].all_sightings()
        sightings.sort(key=lambda im: self.unique_funcs[dataset_str](im))
        return sightings
