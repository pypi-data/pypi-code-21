# !usr/bin/env python
# coding=gbk

import os
import subprocess

import pandas
import scipy.io.wavfile as wav
from pydub import AudioSegment

from calcMFCC import calcMFCC

SEP = os.sep


def wav2MFCC(dataset_dir='../data/test/dataset', datasetName='dataset'):
    for parent, dirnames, filenames in os.walk(dataset_dir):
        for filename in filenames:
            if '.DS_Store' not in filename and '.doc' not in filename:
                file_path = os.path.join(parent, filename)
                (rate, sig) = wav.read(file_path)
                mfcc_feat = calcMFCC(sig, rate)
                mfcc_feat_path = os.path.dirname(file_path) + SEP + os.path.basename(file_path).split('.')[0] + '.mfcc'
                mfcc_feat_path = mfcc_feat_path.replace(datasetName, datasetName + '_mfcc')
                if os.path.isdir(mfcc_feat_path):
                    pass
                else:
                    os.makedirs(os.path.dirname(mfcc_feat_path))
                pandas.to_pickle(mfcc_feat, mfcc_feat_path)
    return 0


def mp32Wav(path_to_process='../data/test/dataset', datasetName='dataset', sample_rate=16000):
    count = 0
    for parent, dirnames, filenames in os.walk(path_to_process):
        for filename in filenames:
            if '.mp3' in filename or '.MP3' in filename:
                file_path = os.path.join(parent, filename)
                rate = sample_rate
                count += 1

                print 'processing...NO.%d ' % count + file_path
                file_fromat = file_path[-3:]
                out_path = os.path.dirname(file_path) + SEP + os.path.basename(file_path).split('.')[0] + '.wav'
                out_path = out_path.replace(datasetName, 'mono_wav' + str(rate / 1000.0))
                sound = AudioSegment.from_file(file_path, file_fromat)
                new = sound.set_channels(1)
                new = new.set_frame_rate(rate)
                if not os.path.exists(os.path.dirname(out_path)):
                    os.makedirs(os.path.dirname(out_path))
                new.export(out_path, 'wav')
    return 0


def mpeg2wav(mvs_dir='MV'):
    # readme mv title should not have space like that "I Love pytho.mpeg" u can change space to _
    for parent, dirnames, filenames in os.walk(mvs_dir):
        for filename in filenames:
            mv_dir = os.path.join(parent, filename)

            audio_dir = 'audio/' + os.path.splitext(mv_dir)[0] + '.wav'
            if not os.path.exists(os.path.split(audio_dir)[0]):
                os.makedirs(os.path.split(audio_dir)[0])
            command = 'ffmpeg -i ' + mv_dir + ' -ab 160k -ac 2 -ar 44100 -vn ' + audio_dir
            subprocess.call(command, shell=True)

            mono_sound_dir = 'mono/' + audio_dir
            if not os.path.exists(os.path.split(mono_sound_dir)[0]):
                os.makedirs(os.path.split(mono_sound_dir)[0])
            left_audio_dir = 'left_right/' + os.path.splitext(mono_sound_dir)[0] + '_left.wav'
            if not os.path.exists(os.path.split(left_audio_dir)[0]):
                os.makedirs(os.path.split(left_audio_dir)[0])
            right_audio_dir = 'left_right/' + os.path.splitext(mono_sound_dir)[0] + '_right.wav'
            if not os.path.exists(os.path.split(right_audio_dir)[0]):
                os.makedirs(os.path.split(right_audio_dir)[0])
            sound = AudioSegment.from_wav(audio_dir)
            mono = sound.set_channels(1)
            left, right = sound.split_to_mono()
            mono.export(mono_sound_dir, format='wav')
            left.export(left_audio_dir, format='wav')
            right.export(right_audio_dir, format='wav')
    return 0


def video2mp4(video_dir):
    for parent, dirnames, filenames in os.walk(video_dir):
        for filename in filenames:
            video_in = os.path.join(parent, filename)
            video_ext = os.path.basename(video_in).split('.')[-1]
            os.rename(video_in, 'temp.' + video_ext)
            cmd = 'ffmpeg -i temp.' + video_ext + ' -y temp.mp4'
            print cmd
            os.system(cmd)
            os.rename('temp.mp4', video_in.replace(video_ext, 'mp4'))
            os.remove('temp.' + video_ext)
    return 0
