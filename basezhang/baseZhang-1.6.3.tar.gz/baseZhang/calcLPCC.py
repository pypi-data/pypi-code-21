# Opening an audio file (AudioFile class)
import math

import numpy

from pymir import AudioFile


def calcLPCC(wav_path, frame_size=1024, lpcc_order=12):
    wavData = AudioFile.open(wav_path)
    lpcc_feature = []
    # Decomposing into frames
    # Fixed frame size
    windowFunction = numpy.hamming
    fixedFrames = wavData.frames(frame_size, windowFunction)
    for frame_item in fixedFrames:
        frame_lpcc_feature = frame_item.lpcc(lpcc_order)
        drop_flag = False
        for number in frame_lpcc_feature:
            if math.isinf(number) or math.isnan(number):
                drop_flag = True
                break
        if not drop_flag:
            lpcc_feature.append(frame_lpcc_feature)
    # print lpcc_feature
    # print len(lpcc_feature)
    lpcc_feature = numpy.array(lpcc_feature)

    return lpcc_feature

# calcLPCC('reading5-m-yxx.wav')
