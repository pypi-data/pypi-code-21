from janus.net.preproc_utils import chip_split
from janus.net.csN_evaluation_utils import Protocols
from pyspark import SparkContext
import os
janus_data = os.environ.get('JANUS_DATA')

csv_dir_dict = {
    'cs2': os.path.join(janus_data, 'Janus_CS2', 'CS2_chips',),
    'cs3': os.path.join(janus_data, 'Janus_CS3', 'CS3_chips'),
    'cs4': os.path.join(janus_data, 'Janus_CS4', 'CS4_chips'),
    'strface': os.path.join(janus_data, 'strface', 'strface_chips'),
    'ijbb': os.path.join(janus_data, 'IJB-B', 'IJB-B_chips'),
    'ijba': os.path.join(janus_data, 'IJB-A', 'IJB-A_chips'),
    }

if __name__ == '__main__':

    dataset_str = 'ijbb'
    prots = Protocols(janus_data)
    sightings = prots.all_sightings(dataset_str)
    sc = SparkContext()
    dilate = 1.5
    outdir = os.path.join(csv_dir_dict[dataset_str], 'chips')
    test_set = sc.parallelize(sightings)
    uniq_func = prots.unique_funcs[dataset_str]
    chip_split(test_set, outdir=outdir, dilate=1.5, name_func=uniq_func)
