import scipy.io as sio
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

def load():
    home = expanduser("~")
    p = join(home, ".mnistdb")
    if not exists(p):
        os.mkdir(p)
    p = join(home, ".mnistdb", "mnist.mat")
    if not exists(p):
        if "MNIST_VERBOSE" not in os.environ or os.environ["MNIST_VERBOSE"] != "0":
            sys.stderr.write("mnistdb: Loading MNIST data set...\n")
            sys.stderr.write("mnistdb: This has to be done only for the first time.\n")
            sys.stderr.write("mnistdb: Set environment variable MNIST_VERBOSE=0 to suppress this message.\n")
        data = None
        if sys.version_info.major == 2:
            data = urllib.urlopen(data_url).read()
        else:
            data = urllib.request.urlopen(data_url).read()
        open(p, "wb").write(data)
    r = sio.loadmat(p)
    return MNIST(trainX=r["trainX"], trainY=r["trainY"], testX=r["testX"], testY=r["testY"])

if __name__ == "__main__":
    x = load()
    assert x.trainX.shape == (60000, 784)
    assert x.trainY.shape == (1, 60000)
    assert x.testX.shape == (10000, 784)
    assert x.testY.shape == (1, 10000)
