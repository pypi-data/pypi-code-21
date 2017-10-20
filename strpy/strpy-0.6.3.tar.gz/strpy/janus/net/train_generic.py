import os
import subprocess
import argparse
import datetime


def form_suffix(suffix_og=''):

    td = datetime.date.today()
    time_suffix = td.strftime('%d%b%y').upper()
    if suffix_og != '':
        return '%s_%s' % (suffix_og, time_suffix)
    else:
        return '%s' % (time_suffix)

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
parser.add_argument("--debug_dir", help="debug dir for debugging enabling",
                    default="")
parser.add_argument("--gpuid", help="id of the first gpu to use", default=0, type=int)
parser.add_argument("--gpu_num", help="number of gpus to use", default=4, type=int)
parser.add_argument("--microbatch", help="microbatch to be multiplied by the number of gpus", default=32, type=int)
parser.add_argument("--epoch", help="epoch at which to resume", default=1, type=int)
parser.add_argument("--log",  help="log this in the output dir", default=False, action='store_true')


args = parser.parse_args()
janus_source = os.environ.get('JANUS_SOURCE')
janus_release = os.environ.get('JANUS_RELEASE')
exec_path = janus_release + '/bin/'
output_path = args.output_dir
curr_data = args.train_data
curr_jittered_data = args.jitter_data
model_suffix = args.suffix

curr_exec = exec_path + 'TRAIN_%s_%s' % (args.net, args.dataset_id)
curr_model_base = output_path + '/' + '%s_%s_%s' % (args.net, args.dataset_id,
                                                    form_suffix(model_suffix))

command_args = [curr_exec, '--model=', curr_model_base + '.dlib', '--train=', curr_data, "--gpuid", str(args.gpuid),
                '--epoch', str(args.epoch),
                '--microbatch', str(args.microbatch),
                '--gpu', str(args.gpu_num),
                '--debug_dir', args.debug_dir]
print ' '.join(command_args)

if args.log:
    logfile = curr_model_base + '.log'
    with open(logfile, 'w') as output_log:
        subprocess.call(command_args, stdout=output_log)


else:
    ret_code = subprocess.call(command_args)
