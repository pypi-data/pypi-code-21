from janus.net.encode_and_evaluate_all_models import DlibModels
import vggface
import argparse
import itertools
import os
parser = argparse.ArgumentParser(description="parse testing args")

parser.add_argument("input_names", help="name of the model + suffix", nargs='+')
parser.add_argument("--mat_dir", help="location of encodings",
                    default='/proj/janus3/octavian.biris/model_evaluations/')
parser.add_argument("--test_jittering", help="Type of test time jittering",
                    default='centercrop', nargs='+',
                    choices=['centercrop', 'randomcrop', 'tencrop', 'lr-reflection-only'])
parser.add_argument("--protocol", help="which testing protocol to use",
                    choices=['cs2', 'cs3'], default='cs2')
parser.add_argument("--split_base", help="export a specific split at an absolute path",
                    default='')

args = parser.parse_args()

tups_to_eval = [tup for tup in itertools.product(args.input_names, args.test_jittering)]

for tup in tups_to_eval:
    output_mat = args.mat_dir + '%s_%s.mtx' % (tup[0], tup[1])
    if os.path.isfile(output_mat):
        print "evaluation for encoding set :", output_mat
        if args.protocol == 'cs2':
            if args.split_base == '':
                vggface.cs2_evaluation(output_mat)
            else:
                vggface.cs2_evaluation(output_mat, args.split_base + '%s_%s' % (tup[0], tup[1]))
        elif args.protocol == 'cs3':
            print "Not implemented yet"
    else:
        print "Encoding file not found :", output_mat
