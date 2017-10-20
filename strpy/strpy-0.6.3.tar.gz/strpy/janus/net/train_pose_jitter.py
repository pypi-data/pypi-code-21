import os
import subprocess
import argparse
import datetime


def form_suffix(jitterfile, jitter_num, suffix_og):

    td = datetime.date.today()
    time_suffix = td.strftime('%d%b%y').upper()
    jitter_string_array = ['unary', 'dual', 'tertiary', 'quadric']

    jitter_count_suffix = jitter_string_array[jitter_num] if jitter_num < 3 else '%s-way' % jitter_num
    jitter_suffix = '_'.join(os.path.split(jitterfile)[1].split('_')[1:-1])

    if suffix_og != '':
        return '%s_%s_%s_%s' % (jitter_count_suffix, jitter_suffix, suffix_og, time_suffix)
    else:
        return '%s_%s_%s' % (jitter_count_suffix, jitter_suffix, time_suffix)

# TODO add argument for passing dataset type in the model identifier; currently hardcoded to vggface;
# ideally it should be <net name>_<training dataset>_<suffix>.dlib
parser = argparse.ArgumentParser(description="parse training args")
parser.add_argument("net", help="name of the model to train; executable name and model output name derived from this")
parser.add_argument("--suffix", help="unique model identifier", default="")
parser.add_argument("--output_dir", help="destination of output model",
                    default='/proj/janus3/octavian.biris/trained_models/')
parser.add_argument("--train_data", help="path to training data csv",
                    default='/proj/janus3/octavian.biris/dataset_csvs/trainset_from_imdb.csv')
parser.add_argument("--dataset_id", help="id of the training dataset",
                    default='vggface')
parser.add_argument("--jitter_data", help="path to pose jittered data csv",
                    default='/proj/janus3/octavian.biris/dataset_csvs/vggface_pose_jitter_warped_background_13SEP16.csv')
parser.add_argument("--gpuid", help="id of the first gpu to use", default=0, type=int)
parser.add_argument("--gpu_num", help="number of gpus to use", default=4, type=int)
parser.add_argument("--epoch", help="epoch at which to resume", default=1, type=int)
parser.add_argument("--jitter_num",
                    help="how many pose jittered instances to use; passing 0 will do a random flip between original and pose jittered",
                    default=0, type=int)
parser.add_argument("--jitter_chance", help="In case of unary jittering, what's the chance that a jittered file will be used instead of the original", default=0.5, type=float)
parser.add_argument("--log",  help="log this in the output dir", default=False, action='store_true')


args = parser.parse_args()
janus_source = os.environ.get('JANUS_SOURCE')
janus_release = os.environ.get('JANUS_RELEASE')
exec_path = janus_release + '/bin/'
output_path = args.output_dir
curr_data = args.train_data
curr_jittered_data = args.jitter_data
model_id = args.net
model_suffix = args.suffix

curr_exec = exec_path + 'TRAIN_%s_%s_pose_jitter' % (model_id, args.dataset_id)
curr_model_base = output_path + '/' + '%s_%s_%s' % (model_id, args.dataset_id,
                                                    form_suffix(curr_jittered_data, args.jitter_num, model_suffix))

command_args = [curr_exec, '--jitterp=', curr_jittered_data, '--model=', curr_model_base + '.dlib', '--train=', curr_data, "--gpuid", str(args.gpuid),
                '--epoch', str(args.epoch), '--jitter_num', str(args.jitter_num),
                '--jitter_chance', str(args.jitter_chance),
                '--gpu', str(args.gpu_num)]
print ' '.join(command_args)

if args.log:
    logfile = curr_model_base + '.log'
    with open(logfile, 'w') as output_log:
        subprocess.call(command_args, stdout=output_log)


else:
    ret_code = subprocess.call(command_args)
