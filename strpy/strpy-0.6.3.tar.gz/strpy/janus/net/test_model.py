import os
import subprocess
import janus.net.vggface
import argparse
import matplotlib.pyplot as plt
import bobo.util
from janus.net.csN_evaluation_utils import csN_evaluation, compute_csN_templates, compute_csN_media, csN_pool_media_into_templates
from janus.dataset.csN import Protocols
import numpy as np
import dill


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def partition_base_and_index(filename):
    [root, ext] = os.path.splitext(filename)
    parts = root.split('_')
    if len(parts) < 2:  # need at least two parts for a partition filename
        print " Warning couldn't find partition base and index from filename ", filename
        return [None, None, ext]
    if RepresentsInt(parts[-1]):
        partition_index = int(parts[-1])
        base_without_index = "_".join(parts[:-1])
        return[base_without_index, partition_index, ext]
    else:
        return[None, None,ext]


def generate_output_name(net, dataset_id, suffix, encode_path, test_jittering, jitter_file="", jitter_num=0):
    # generate output name from a path to a csv file representing an encoding partition
    [head, tail] = os.path.split(encode_path)
    [eval_name, ext] = tail.split(".")
    output_str = '%s_%s_%s_%s_%s' % (net, dataset_id, suffix, eval_name, test_jittering)
    #  append suffix if there's test time pose_jittering
    if jitter_file != "" and jitter_num > 0:
        output_str += "_%d-test-jitter" % jitter_num


    # handle multiple chunks
    [eval_name_without_index, partition_index, ext] = partition_base_and_index(eval_name)

    if eval_name_without_index is not None:  # if the input csv had a number at the end, remove it and return the resulting string. separators are asummed to be underscores
        output_parts = output_str.split('_')
        output_parts_np = np.array(output_parts)
        index_of_dataset = np.where(output_parts_np == eval_name_without_index)[0][0]
        if not index_of_dataset:
            print "could not find index of the partition from parts ", output_parts
        output_parts[index_of_dataset] = eval_name_without_index
        del output_parts[index_of_dataset + 1]
        output_parts += [str(partition_index)]
        output_str = "_".join(output_parts)

    return output_str


def generate_result_dic_output_name(net, dataset_id, suffix, dataset_name, test_jittering, csv_suffix="", jitter_file="", jitter_num=0):
    jitter_string = test_jittering
    if csv_suffix != "":
        jitter_string = "%s_%s" % (csv_suffix, test_jittering)  # preprend jittering ID with the extra suffixes from the csv input
    output_str = '%s_%s_%s_%s_L2_%s' % (net, dataset_id, suffix, dataset_name, jitter_string)
    if jitter_file != "" and jitter_num > 0:
        output_str += "_%d-test-jitter" % jitter_num
    #  append suffix if there's test time pose_jittering
    if jitter_file != "" and jitter_num > 0:
        output_str += "_%d-test-jitter" % jitter_num
    return output_str

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="parse testing args")
    parser.add_argument("net", help="name of the model to train; executable name and model output name derived from this")
    parser.add_argument("suffix", help="unique model identifier; usually the date in the format of DDMMMYY or some other string")
    parser.add_argument("--model_dir", help=" location of the input model ",
                        default='/proj/janus3/octavian.biris/trained_models/')
    parser.add_argument("--output_dir", help="destination of the output matrix",
                        default='')
    parser.add_argument("--encode", help="path to test data csv to be encoded",
                        default='/proj/janus3/vsi/cs2.csv')
    parser.add_argument("--dataset_id", help="ID of the trained dataset",
                        default='vggface')
    parser.add_argument("--jitter_file", help="Path to the file with pose jitters", default="")
    parser.add_argument("--jitter_num", help="Number of images to jitter", default=0, type=int)
    parser.add_argument("--debug_dir", help="Path to the debugging dir", default="")
    parser.add_argument("--test_jittering", help="Type of test time jittering",
                        default='centercrop',
                        choices=['centercrop', 'randomcrop', 'tencrop', 'lr-reflection-only'])
    parser.add_argument("--gpuid", help="id of the first gpu to use", default=0, type=int)
    parser.add_argument("--jobs", help="number of threads to use while loading data queue", default=4, type=int)
    parser.add_argument("--minibatch", help="minibatch size", default=32, type=int)
    parser.add_argument("--printrate", help="how often to print encoding status", default=100, type=int)
    parser.add_argument("--force", help="force the rewriting of the mtx file", default=False, action='store_true')
    parser.add_argument("--legacy", help="Fill the minibatch with the current test jittering augmentation",
                        default=False, action='store_true')

    parser.add_argument("--templates", help="Create media and templates for the encoded file and save them to disk",
                        default=False, action='store_true')
    parser.add_argument("--eval", help="Perform a csN evaluation on the templates.",
                        default=False, action='store_true')

    parser.add_argument("--validate", help="Path to validation set", default="")

    args = parser.parse_args()
    janus_source = os.environ.get('JANUS_SOURCE')
    if janus_source is None:
        raise Exception('Please set JANUS_SOURCE environment variable')
    janus_release = os.environ.get('JANUS_RELEASE')
    if janus_release is None:
        raise Exception('Please set JANUS_RELEASE environment variable')
    # optional environs
    janus_data = os.environ.get('JANUS_DATA')
    janus_root = os.environ.get('JANUS_ROOT')

    exec_path = janus_release + '/bin/'

    model_id = args.net
    valset = args.validate
    [head, tail] = os.path.split(args.encode)
    [eval_name, ext] = tail.split(".")

    curr_exec = os.path.join(exec_path, 'TEST_%s_%s' % (args.net, args.dataset_id))
    if os.path.isfile(args.jitter_file) and 'coeffs' in args.jitter_file:
        curr_exec = os.path.join(exec_path, 'TEST_%s_%s_pose_jitter' % (args.net, args.dataset_id))
    input_model = os.path.join(args.model_dir, '%s_%s_%s.dlib' % (args.net, args.dataset_id, args.suffix))
    output_mat_suffix = generate_output_name(args.net, args.dataset_id, args.suffix,
                                             args.encode, args.test_jittering,
                                             args.jitter_file, args.jitter_num)
    output_mat = os.path.join(args.output_dir, output_mat_suffix + '.mtx')
    command_args = [curr_exec, '--model=', input_model, '--encode=', args.encode, '--mtx=', output_mat, "--gpuid=", str(args.gpuid),
                    '--%s' % args.test_jittering, '--jitterp', args.jitter_file,
                    '--minibatch', str(args.minibatch), '--printrate', str(args.printrate),
                    '--jobs', str(args.jobs),
                    '--jitter_num', str(args.jitter_num),
                    '--debug_dir', args.debug_dir,
                    ]
    if args.legacy:
        command_args.append('--legacy')
    #                '--validate', valset]
    print ' '.join(command_args)
    if os.path.isfile(output_mat) and not args.force:
        print "Output file", output_mat, " with encodings already exists! Use --force option to overwrite "
    else:
        ret_code = subprocess.call(command_args)

    # create templates and media and do an L2 evaluation if this matrix represents sightings from one of the canonical CSs

    if os.path.isfile(output_mat) and os.path.isdir(janus_data) and os.path.isdir(janus_root):
        eval_name_parts = eval_name.split('_')
        dataset_name = eval_name_parts[0]
        dataset_extras = '_'.join(eval_name_parts[1:]) if len(eval_name_parts) > 1 else ""
        current_protocols = Protocols(janus_data)
        if dataset_name in current_protocols._datasets:

            template_dir = os.path.join(janus_root, 'checkpoints', dataset_name)
            results_dir = os.path.join(janus_root, 'results', dataset_name)
            bobo.util.remkdir(template_dir)
            bobo.util.remkdir(results_dir)

            templates_dic_path = os.path.join(template_dir, '%s_templates.pk' % (output_mat_suffix)) if args.templates else ''
            media_dic_path = os.path.join(template_dir, '%s_media.pk' % (output_mat_suffix)) if args.templates else ''
            results_output_name = generate_result_dic_output_name(args.net, args.dataset_id, args.suffix,
                                                                  dataset_name, args.test_jittering, dataset_extras,
                                                                  args.jitter_file, args.jitter_num)
            results_dic_path = os.path.join(results_dir, '%s_results.pk' % results_output_name)
            if args.templates:
                templates_dic = compute_csN_templates(output_mat, dataset_name)
                if templates_dic is not None:
                    with open(templates_dic_path, 'wb') as f:
                        dill.dump(templates_dic, f)
                    if not os.path.isfile(templates_dic_path):
                        print "Could not write templates to ", templates_dic_path

            if args.eval:
                print "evaluating and saving results into ",results_dic_path
                splitmean = False
                if dataset_name == 'cs2' or dataset_name == 'ijba':
                    splitmean = True
                print "csN evaluation for encoding set :", output_mat
                results_dic = csN_evaluation(output_mat, templates_dic_path, dataset_name, redo_templates=False,
                                             cmcFigure=3, detFigure=4, prependToLegend='',
                                             hold=False, output_splitfile='', splitmean=splitmean,
                                             detLegendSwap=False, cmcLegendSwap=False, cmcMinY=0.0, metrics=True)
                if results_dic is not None:
                    with open(results_dic_path, 'wb') as f:
                        dill.dump(results_dic, f)
                    if not os.path.isfile(results_dic_path):
                        print "Could not write results to ", results_dic_path
                else:
                    print "Could not compute results for experiment", output_mat_suffix
