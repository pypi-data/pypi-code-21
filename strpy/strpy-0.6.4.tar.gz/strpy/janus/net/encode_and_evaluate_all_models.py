import os
import subprocess
import vggface
import argparse
import itertools
from multiprocessing import Pool
import sys
from test_model import RepresentsInt, generate_output_name, partition_base_and_index
from janus.openbr import readbinary, writebinary
import numpy as np


class DlibModels(object):

    def __init__(self):
        self.list = {
            'resnet34a': ['pose_jitter_unary_black_background_01AUG16',
                          'pose_jitter_unary_warped_background_20AUG16',
                          'pose_jitter_dual_warped_background_30AUG16',
                          'pose_jitter_unary_warped_background_13SEP16',
                          'pose_jitter_dual_warped_background_15SEP16',
                          '05JUN16'],
            'resnet101': ['pose_jitter_unary_warped_background_20AUG16',
                          'pose_jitter_unary_black_background_16AUG16',
                          '14APR17',
                          '25JUL17',
                          '28AUG17_E15',
                          '11JUN16'],
            'vggVD': ['pose_jitter_unary_warped_background_20AUG16',
                      'pose_jitter_unary_warped_background_21SEP16',
                      'pose_jitter_unary_warped_background_13SEP16',
                      'pose_jitter_dual_warped_background_13SEP16',
                      'pose_jitter_unary_black_background_10AUG16',
                      '05JUN16']}


def parallelize_ad_hoc(list, num_partitions):

    incr = len(list) / float(num_partitions)
    last = 0.0
    partitions = []
    while last < len(list):
        partitions.append(list[int(last):int(last + incr)])
        last += incr
    return partitions


class PartitionMerger(object):

    def __init__(self, base_path=None, purge_partitions=False):
        self.base_path = base_path
        self.purge_partitions = purge_partitions

    def __call__(self, partitions):
        encodings = []
        [base,tail] = os.path.split(partitions[0])
        [tail_without_index, start_index, ext] = partition_base_and_index(tail)
        if tail_without_index is None:
            print "Unable to determine the index of partition %s" % partitions[0]
            return

        if self.base_path is None:
            output_destination = base + tail_without_index + ext
        else:
            output_destination = os.path.join(self.base_path, tail_without_index + ext)


        print "combining %s partitions starting at %s and placing in %s " % (len(partitions),
                                                                             start_index,
                                                                             output_destination)
        for i,infile in enumerate(partitions):
            print "loading partition %s " % (infile)

            [curr_tail_without_index, curr_index, ext] = partition_base_and_index(infile)
            if curr_tail_without_index is None:
                print "Unable to determine the index of partition %s" % infile
                return

            if curr_index != start_index + i:
                print 'Warning: partition string from filename %s is not in order with the partition index!' % infile
            mtx = readbinary(infile)
            if mtx is None:
                return
            mtx = mtx / np.linalg.norm(mtx, axis=1).reshape((-1, 1))
            encodings.append(mtx)

        encodings = np.vstack(encodings)

        print 'Encodings size: ', encodings.shape
        writebinary(encodings, output_destination)
        if self.purge_partitions:
            for infile in partitions:
                os.remove(infile)


class ModelEncoder(object):

    def __init__(self, model, model_dir, output_dir, jitterfile="", jitter_num=0,
                 minibatch=32, printrate=100,
                 encode_set=None, force=False, dataset_id='vggface', legacy=False):
        self.model = model
        self.model_dir = model_dir
        self.output_dir = output_dir
        self.encode_set = encode_set
        self.force = force
        self.jitterfile = jitterfile
        self.jitter_num = jitter_num
        self.dataset_id = dataset_id
        self.legacy = legacy
        self.minibatch = minibatch
        self.printrate = printrate

    def __call__(self, item):
        gpuid = item[0]
        tups = item[1]
        rets = []

        for tup in tups:
            network_suffix = tup[0]
            jittering = tup[1]
            encode_set = tup[2]
            exec_args = ['python', exec_path, self.model, network_suffix,
                         '--model_dir', self.model_dir,
                         '--output_dir', self.output_dir,
                         '--encode', encode_set,
                         '--dataset_id', self.dataset_id,
                         '--test_jittering', jittering,
                         '--jitter_file', self.jitterfile,
                         '--jitter_num', str(self.jitter_num),
                         '--minibatch', str(self.minibatch),
                         '--printrate', str(self.printrate),
                         '--gpuid', str(gpuid)]
            if self.force:
                exec_args.append('--force')
            if self.legacy:
                exec_args.append('--legacy')

#            print ' '.join(exec_args)
            ret_code = subprocess.call(exec_args)
            rets.append(ret_code)
        return rets


janus_source = os.environ.get('JANUS_SOURCE')
janus_root = os.environ.get('JANUS_ROOT')
exec_path = janus_source + '/python/janus/net/test_model.py'
model_path = os.path.join(janus_root, 'models', 'dlib-dnn')



if __name__ == '__main__':
    models = DlibModels()
    parser = argparse.ArgumentParser(description="parse testing args")

    test_jitter_suffixes = ['centercrop', 'tencrop', 'randomcrop', 'lr-reflection-only']

    parser.add_argument("model", help="name of the model to test",
                        choices=models.list.keys())
    parser.add_argument("--suffix",
                        help="suffix to be appended to the model to test", nargs='+')
    parser.add_argument("--gpu_num", help="how many gpus to use", default=1, type=int)
    parser.add_argument("--gpuid", help="index of first gpu", default=0, type=int)
    parser.add_argument("--minibatch", help="minibatch size", default=32, type=int)
    parser.add_argument("--printrate", help="how often to print encoding status", default=100, type=int)
    parser.add_argument("--test_jittering",
                        help="kinds of test jittering", default=test_jitter_suffixes,
                        choices=test_jitter_suffixes, nargs='+')
    parser.add_argument("--force", help="force overwrite in case encoded matrix exists",
                        default=False, action='store_true')
    parser.add_argument("--model_dir", help=" location of the input model ",
                        default=model_path)
    parser.add_argument("--output_dir", help="destination of the output matrix",
                        default='/proj/janus3/octavian.biris/model_evaluations/')
    parser.add_argument("--dataset_id", help="ID of the trained dataset",
                        default='msceleb1m')
    parser.add_argument("--jitter_file", help="Path to the file with pose jitters", default="")
    parser.add_argument("--jitter_num", help="Number of images to jitter", default=0, type=int)
    parser.add_argument("--encode", help="path to test data csv to be encoded",
                        default='/proj/janus3/vsi/cs2.csv')
    parser.add_argument("--encode_multi_file", help="Number of partition csvs. Pass the first partition to the --encode argument",
                        default=0, type=int)
    parser.add_argument("--legacy", help="Fill the minibatch with the current test jittering augmentation",
                        default=False, action='store_true')

    args = parser.parse_args()

    curr_test_jittering = args.test_jittering

    model_suffixes = []
    partitions_to_combine = []
    if args.suffix:
        for suff in args.suffix:
            if suff not in models.list[args.model]:
                print 'Model ', args.model, 'does not have suffix ', suff, ' possible values are : ', models.list[args.model]
                sys.exit()  # Enforce ALL passed suffixes are correct
            else:
                model_suffixes.append(suff)
    else:
        model_suffixes = models.list[args.model]


    if args.encode_multi_file > 0:  # handle multi chunk encoding and merging
        [base_without_index, start_chunk, ext] = partition_base_and_index(args.encode)
        if base_without_index is None:
            print " expected last suffix of ", args.encode, " to have a numeral that represents the first partition. Quitting!"
            sys.exit()

        if start_chunk >= args.encode_multi_file:
            print "Number of chunks = ", args.encode_multi_file," but start index is ",start_chunk," .Quitting!"
            sys.exit()
        encode_list = [base_without_index + '_%d' % i + ext for i in xrange(start_chunk,start_chunk + args.encode_multi_file)]

        partitions_to_combine = [ [os.path.join(args.output_dir, generate_output_name(args.model, args.dataset_id,
                                                                          tup[0],encode_csv , tup[1],
                                                                          args.jitter_file, args.jitter_num)
                                   + '.mtx')
                                   for encode_csv in encode_list]
                                  for tup in itertools.product(model_suffixes, curr_test_jittering)]
    else:
        encode_list = [args.encode]

    tups = [tup for tup in itertools.product(model_suffixes, curr_test_jittering, encode_list)]
    partitions = parallelize_ad_hoc(tups, args.gpu_num)
    gpus = range(args.gpuid, args.gpuid + args.gpu_num)
    gpu_process_list = zip(gpus, partitions)

    print gpu_process_list

    peons = Pool(args.gpu_num)  # work work!
    results = peons.map(ModelEncoder(args.model, args.model_dir, args.output_dir,
                                     jitterfile=args.jitter_file, dataset_id=args.dataset_id, minibatch=args.minibatch, printrate=args.printrate,
                                     jitter_num=str(args.jitter_num), force=args.force, legacy=args.legacy), gpu_process_list)

    peons.close()
    peons.join()

    if args.encode_multi_file > 0:
        merge_workers = Pool(8)
        results = merge_workers.map(PartitionMerger(base_path = args.output_dir, purge_partitions=False) ,
                                    partitions_to_combine)
