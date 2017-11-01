import scipy.io as sio
import numpy as np
from collections import namedtuple
from os.path import expanduser, exists, join
import os
import sys

if sys.version_info.major == 2:
    import urllib
else:
    import urllib.request

MNIST = namedtuple("MNIST", ["trainX", "trainY", "testX", "testY"])

data_url = "https://github.com/daniel-e/mnistdb/raw/master/mnist.mat"

def _scale_x(data):
    return MNIST(
        trainX=data.trainX.astype(np.float32) / 255,
        trainY=data.trainY,
        testX=data.testX.astype(np.float32) / 255,
        testY=data.testY
    )

def load(scaled=False):
    home = expanduser("~")
    p = join(home, ".mnistdb")
    if not exists(p):
        os.mkdir(p)
    p = join(home, ".mnistdb", "mnist.mat")
    if not exists(p):
        if "MNIST_VERBOSE" not in os.environ or os.environ["MNIST_VERBOSE"] != "0":
            sys.stderr.write("mnistdb: Loading MNIST data set...\n")
            sys.stderr.write("mnistdb: This has to be done only for the first time.\n")
            sys.stderr.write("mnistdb: Once the data has been loaded this message will not be shown again.\n")
            sys.stderr.write("mnistdb: Set env variable MNIST_VERBOSE=0 to suppress this message completely.\n")
        data = None
        if sys.version_info.major == 2:
            data = urllib.urlopen(data_url).read()
        else:
            data = urllib.request.urlopen(data_url).read()
        open(p, "wb").write(data)
    r = sio.loadmat(p)
    r = MNIST(trainX=r["trainX"], trainY=np.reshape(r["trainY"], (60000,)), testX=r["testX"], testY=np.reshape(r["testY"], (10000,)))
    if scaled:
        r = _scale_x(r)
    return r

if __name__ == "__main__":
    x = load()
    assert x.trainX.shape == (60000, 784)
    assert x.trainY.shape == (60000,)
    assert x.testX.shape == (10000, 784)
    assert x.testY.shape == (10000,)
