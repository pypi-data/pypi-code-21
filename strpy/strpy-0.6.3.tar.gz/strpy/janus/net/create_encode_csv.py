from janus.net.preproc_utils import split_encodefile
from janus.net.csN_evaluation_utils import Protocols
import os
janus_data = os.environ.get('JANUS_DATA')
csv_dir_dict = {
    'cs2': os.path.join(janus_data, 'Janus_CS2', 'partitioning'),
    'cs3': os.path.join(janus_data, 'Janus_CS3', 'partitioning'),
    'cs4': os.path.join(janus_data, 'Janus_CS4', 'partitioning'),
    'strface': os.path.join(janus_data, 'strface', 'partitioning'),
    'ijbb': os.path.join(janus_data, 'IJB-B', 'partitioning'),
    'ijba': os.path.join(janus_data, 'IJB-A', 'partitioning')
    }
if __name__ == '__main__':

    dataset_str = 'strface'
    prots = Protocols(janus_data)
    sightings = prots.all_sightings(dataset_str)
    uniq_func = prots.unique_funcs[dataset_str]
    n_split = 1
    outdir = os.path.join(csv_dir_dict[dataset_str], '%s-split' % n_split)
    dilate = 1.1
    split_encodefile(sightings, n_split, outdir, dataset_str, uniq_func, dilate=dilate)
