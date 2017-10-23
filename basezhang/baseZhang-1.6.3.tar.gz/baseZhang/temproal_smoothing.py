import pycrfsuite, joblib, numpy, os
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import numpy as np
from hmmlearn import hmm
from baseZhang import get_acc
numpy.random.seed(1007)
STEPS=20
NUN=200


def hmm_smoothing(predictY_prob):
    np.random.seed(1007)
    model = hmm.GMMHMM(n_components=2, n_iter=40, n_mix=45)
    model.fit(predictY_prob,)
    predictY = model.predict(predictY_prob)  # 0.871955719557 #0.841328413284
    return predictY

def ndarray2charList(ndarray):
    charlist = []
    for item in ndarray:
        charlist.append(str(item[0]))

    return charlist


def numlist2charList(ndarray):
    charlist = []
    for item in ndarray:
        charlist.append(str(item))

    return charlist


def format2steps(charList, step=STEPS):
    stepList = []
    for item in range(0, len(charList)-step,step):
        stepList.append(charList[item:item + step])
    return stepList

def extend_list(preTestY):
    crf_pre = []
    for preYseq in preTestY:
        crf_pre.extend(preYseq)
    final=[int(item) for item in crf_pre]
    print final

    return final

def crf_smth(preValidY=[['no', 'yes'], ['no', 'no', 'yes']], validY=[['yes', 'yes'], ['no', 'no', 'yes']],
             preTestY=[['no', 'yes'], ['no', 'no', 'yes']], retrain=1):
    print preValidY
    print validY
    crf_model = 'crf.modle'
    if retrain == 1 or not os.path.isfile(crf_model):
        trainer = pycrfsuite.Trainer(verbose=False)
        for pr,va in zip(preValidY, validY):
            trainer.append(pr,va)
        trainer.set_params({'c1': 0.1, 'c2': 0.01, 'max_iterations': 2000, 'feature.possible_transitions': True})
        trainer.train(crf_model)
    tagger = pycrfsuite.Tagger()
    tagger.open('crf.model')
    crf_pre = []
    for preYseq in preTestY:
        yseq = tagger.tag(preYseq)
        crf_pre.extend(yseq)
    final = [int(item) for item in crf_pre]
    print final
    return final


def main():
    preY = joblib.load('preY.data')
    tesY = joblib.load('testY.data')
    preY = ndarray2charList(preY)
    tesY = numlist2charList(tesY)
    print 'preY:', preY
    print 'tesY:', tesY
    preY = format2steps(preY)
    tesY = format2steps(tesY)
    print 'preY:', preY
    print 'tesY:', tesY
    print 'preY:', len(preY)
    print 'tesY:', len(tesY)
    X_train, X_test, y_train, y_test = train_test_split(preY, tesY, test_size=0.6)
    smth_y_pre = crf_smth(X_train, y_train, X_test, retrain=1)
    X_test=extend_list(X_test)
    y_test=extend_list(y_test)

    print classification_report(y_test, smth_y_pre)
    print classification_report(y_test, X_test)

    print '     x:', X_test
    print '   crf:', smth_y_pre
    print 'ground:', y_test
    plt.subplot(311, title='ground truth ')
    plt.plot(y_test[:NUN])
    plt.subplot(312, title='predict res %s' % (get_acc(y_test, X_test)))
    plt.plot(X_test[:NUN])
    plt.subplot(313, title='predict after crf %s' % (get_acc(y_test, smth_y_pre)))
    plt.plot(smth_y_pre[:NUN])
    plt.show()

    return 0


if __name__ == '__main__':
    main()
