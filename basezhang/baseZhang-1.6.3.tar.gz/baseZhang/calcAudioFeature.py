import math
import os

import h5py
import numpy

import fromLibrosa
from baseZhang import wavread
from baseZhang import wavwrite, print_to_check
from calcMFCC import calcMFCC, calcMFCC_delta, calcMFCC_delta_delta
from calcSpectralFeatureLibrosa import calc_spectral_bandwidth, calc_spectral_contrast, calc_poly_features, \
    calc_spectral_rolloff, calc_spectral_centroid, calc_rmse, calc_zero_crossing_rate
from pymir import AudioFile


def get_dataset_X_Y(dataset='dataset.h5', dataX='X', dataY='Y'):
    h5file = h5py.File(dataset, 'r')
    X = h5file[dataX][:]
    Y = h5file[dataY][:]
    h5file.close()

    return X, Y


def substractFeat(trainX, trainY, subFeatList=['mfcc', 'chroma', 'lpcc']):
    subFeatTrainX = []
    subFeatTrainY = []
    # print numpy.shape(trainX)
    # print numpy.shape(trainY)
    # print type(trainX), type(trainY)
    for itemX, itemY in zip(trainX, trainY):
        featDict = {'mfcc': itemX[:26],
                    'chroma': itemX[26:38],
                    'zcr': itemX[38:39],
                    'rmse': itemX[39:40],
                    'centroid': itemX[40:41],
                    'rolloff': itemX[41:42],
                    'poly': itemX[42:44],
                    'contrast': itemX[44:51],
                    'bandwith': itemX[51:52],
                    'mfcc_delta_delta': itemX[52:91],
                    'mfcc_delta': itemX[91:117],
                    'lpcc': itemX[117:]}
        combine_item = featDict[subFeatList[0]]
        for item_feat in subFeatList[1:]:
            combine_item = numpy.hstack((combine_item, featDict[item_feat]))
        drop_flag = False
        for number in combine_item:
            if math.isinf(number) or math.isnan(number):
                drop_flag = True
                break
        if not drop_flag:
            subFeatTrainX.append(combine_item)
            subFeatTrainY.append(itemY)

    return numpy.array(subFeatTrainX), numpy.array(subFeatTrainY)


def substractFeatTimeStep(trainX, trainY, subFeatList=['mfcc', 'chroma', 'lpcc']):
    subFeatTrainX = []
    subFeatTrainY = []
    for trainX_step, trainY_step in zip(trainX, trainY):
        subFeatTrainX_step = []
        subFeatTrainY_step = []
        drop_flag = False
        for itemX in trainX_step:
            featDict = {'mfcc': itemX[:26],
                        'chroma': itemX[26:38],
                        'zcr': itemX[38:39],
                        'rmse': itemX[39:40],
                        'centroid': itemX[40:41],
                        'rolloff': itemX[41:42],
                        'poly': itemX[42:44],
                        'contrast': itemX[44:51],
                        'bandwith': itemX[51:52],
                        'mfcc_delta_delta': itemX[52:91],
                        'mfcc_delta': itemX[91:117],
                        'lpcc': itemX[117:]}
            combine_item = featDict[subFeatList[0]]
            for item_feat in subFeatList[1:]:
                combine_item = numpy.hstack((combine_item, featDict[item_feat]))

            for number in combine_item:
                if math.isinf(number) or math.isnan(number):
                    drop_flag = True

            subFeatTrainX_step.append(list(combine_item))
            subFeatTrainY_step.append(trainY_step)
        subFeatTrainX_step = numpy.array(subFeatTrainX_step)
        subFeatTrainY_step = numpy.array(subFeatTrainY_step)
        if not drop_flag:
            subFeatTrainX.append(subFeatTrainX_step)
            subFeatTrainY.append(subFeatTrainY_step[0])
    return numpy.array(subFeatTrainX), numpy.array(subFeatTrainY)


def test_substractFeat():
    '''['mfcc', 'lpcc', 'chroma', 'zcr', 'rmse', 'centroid', 'rolloff', 'poly', 'contrast', 'bandwith',
                   'mfcc_delta_delta', 'mfcc_delta']'''
    useDataset = '../data/sing_voice_detection/test_dataset_all_feat.h5'
    X, Y = get_dataset_X_Y(useDataset)
    subFeatList = ['mfcc', 'lpcc', 'chroma', 'zcr', 'rmse', 'centroid', 'rolloff', 'poly', 'contrast', 'bandwith'
                   ]
    subFeatTrainX, subFeatTrainY = substractFeat(X, Y, subFeatList)
    print numpy.shape(subFeatTrainY), numpy.shape(subFeatTrainX)
    print type(Y), type(subFeatTrainY)
    return 0


def get_audio_feature(test_wav='../test.wav', WIN_SIZE=0.025, HOP_LEN=0.025,
                      feat_list=['mfcc', 'lpcc', 'chroma', 'zcr', 'rmse', 'centroid', 'rolloff', 'poly', 'contrast',
                                 'bandwith', 'mfcc_delta_delta', 'mfcc_delta']):
    # WIN_SIZE need equls to HOP_LEN ie. no overlaps between frames.
    FEAT_shapes = []
    all_feat = []
    '''
    mfcc,chroma,zcr,rmse,centroid,rolloff,poly,contrast,bandwith,mfcc_delta_delta,mfcc_delta,lpcc

    '''

    audio_data, sample_rate = wavread(test_wav)
    # print sample_rate
    print 'mfcc'
    featMFCC = calcMFCC(audio_data, sample_rate, appendEnergy=False, cep_num=26, win_length=WIN_SIZE, win_step=HOP_LEN)
    FEAT_shapes.append(numpy.shape(featMFCC))
    if 'mfcc' in feat_list:
        all_feat.append(featMFCC)
    print 'chroma'
    featChroma = fromLibrosa.chroma_stft(y=audio_data, sr=sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                         n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featChroma))
    if 'chroma' in feat_list:
        all_feat.append(featChroma)
    print 'zcr'
    featZCR = calc_zero_crossing_rate(audio_data, hop_length=int(HOP_LEN * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featZCR))
    if 'zcr' in feat_list:
        all_feat.append(featZCR)
    print 'rmse'
    featRMSE = calc_rmse(audio_data, frame_length=int(WIN_SIZE * sample_rate), hop_length=int(HOP_LEN * sample_rate)).T[
               :-1]
    FEAT_shapes.append(numpy.shape(featRMSE))
    if 'rmse' in feat_list:
        all_feat.append(featRMSE)
    print 'centroid'
    featCentroid = calc_spectral_centroid(audio_data, sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                          n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featCentroid))
    if 'centroid' in feat_list:
        all_feat.append(featCentroid)
    print 'rolloff'
    featRolloff = calc_spectral_rolloff(audio_data, sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                        n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featRolloff))
    if 'rolloff' in feat_list:
        all_feat.append(featRolloff)
    print 'poly'
    featPoly = calc_poly_features(audio_data, sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                  n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featPoly))
    if 'poly' in feat_list:
        all_feat.append(featPoly)
    print 'contrast'
    featContrast = calc_spectral_contrast(audio_data, sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                          n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featContrast))
    if 'contrast' in feat_list:
        all_feat.append(featContrast)
    print 'bandwith'
    featBandwith = calc_spectral_bandwidth(audio_data, sample_rate, hop_length=int(HOP_LEN * sample_rate),
                                           n_fft=int(WIN_SIZE * sample_rate)).T
    FEAT_shapes.append(numpy.shape(featBandwith))
    if 'bandwith' in feat_list:
        all_feat.append(featBandwith)
    print 'mfcc_delta_delta'
    featMFCC_delta_delta = calcMFCC_delta_delta(audio_data, sample_rate, appendEnergy=False, cep_num=13,
                                                win_length=WIN_SIZE, win_step=HOP_LEN)
    FEAT_shapes.append(numpy.shape(featMFCC_delta_delta))
    if 'mfcc_delta_delta' in feat_list:
        all_feat.append(featMFCC_delta_delta)
    print 'mfcc_delta'
    featMFCC_delta = calcMFCC_delta(audio_data, sample_rate, appendEnergy=False, cep_num=13,
                                    win_length=WIN_SIZE, win_step=HOP_LEN)
    FEAT_shapes.append(numpy.shape(featMFCC_delta))
    if 'mfcc_delta' in feat_list:
        all_feat.append(featMFCC_delta)
    print 'lpcc'
    ## calc lpcc
    temp_wav = 'temp.wav'
    wavwrite(temp_wav, audio_data, sample_rate)
    audio_data = AudioFile.open(temp_wav)
    os.remove(temp_wav)
    lpcc_order = 12
    featLPCC = []
    # print audio_data[1]
    windowFunction = numpy.hamming
    fixedFrames = audio_data.frames(int(WIN_SIZE * sample_rate), windowFunction)
    for frame_item in fixedFrames:
        frame_lpcc_feature = frame_item.lpcc(lpcc_order)
        featLPCC.append(frame_lpcc_feature)
    featLPCC = numpy.array(featLPCC)
    ## calc lpcc end

    FEAT_shapes.append(numpy.shape(featLPCC))
    if 'lpcc' in feat_list:
        all_feat.append(featLPCC)
    min_shapes = FEAT_shapes[0][0]
    for shape_item in FEAT_shapes[1:]:
        if shape_item[0] < min_shapes:
            min_shapes = shape_item[0]

    print_to_check(FEAT_shapes)
    combineFeat = all_feat[0][:min_shapes]
    for feat_item in all_feat[1:]:
        combineFeat = numpy.hstack((combineFeat[:min_shapes], feat_item[:min_shapes]))
    print 'combine:', numpy.shape(combineFeat)
    # drop_flag = False
    # for number in frame_lpcc_feature:
    #     if math.isinf(number) or math.isnan(number):
    #         drop_flag = True
    #         break
    # if not drop_flag:
    #     featLPCC.append(frame_lpcc_feature)
    return combineFeat


if __name__ == '__main__':
    combineFeat = get_audio_feature()
