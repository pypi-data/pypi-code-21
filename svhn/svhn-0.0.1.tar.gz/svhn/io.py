import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from os.path import expanduser, exists, join
import os
import sys
import shutil
import h5py
import pdb
import time
import pickle
from collections import namedtuple

# TODO improve performance of converting

if sys.version_info.major == 2:
    import urllib
else:
    import urllib.request

TRAINING = 0
TEST = 1
EXTRA = 2

_ranges = [(1, 33402, "train"),(1, 13068, "test"), (1, 202353, "extra")]

_URL = "http://ufldl.stanford.edu/housenumbers/"

_datafiles = [
    (_URL + "train.tar.gz", "train", 404141560),
    (_URL + "test.tar.gz", "test", 276555967),
    (_URL + "extra.tar.gz", "extra", 1955489752),
    (_URL + "train_32x32.mat", "", 182040794),
    (_URL + "test_32x32.mat", "", 64275384),
    (_URL + "extra_32x32.mat", "", 1329278602)
]

def _target_dir():
    return join(expanduser("~"), ".svhn")

def _target_filename(url):
    return join(_target_dir(), _filename(url))

def _init_dir():
    p = _target_dir()
    if not exists(p):
        os.mkdir(p)

def _open_url(url):
    if sys.version_info.major == 2:
        return urllib.urlopen(url)
    else:
        return urllib.request.urlopen(url)

def _filename(url):
    return url[url.rfind("/")+1:]

def _download_file(url, target_filename, size):
    f = _open_url(url)
    p = _filename(url)
    d = open(target_filename, "wb")
    n = 0
    while True:
        k = f.read(1024 * 1024)
        if k is None or k == "" or len(k) == 0:
            break
        n += len(k)
        d.write(k)
        sys.stderr.write(" loading file: {}, {:6.2f}%  \r".format(p, n / size * 100))
        sys.stderr.flush()
    sys.stderr.write("\n")

def _uncompress(filename):
    sys.stderr.write("uncompressing " + filename + " ...\n")
    sys.stderr.flush()
    os.system("tar -C " + _target_dir() + " -xzf" + filename)

def _get_box_data(index, hdf5_data):
    meta_data = dict()
    meta_data['height'] = []
    meta_data['label'] = []
    meta_data['left'] = []
    meta_data['top'] = []
    meta_data['width'] = []

    def print_attrs(name, obj):
        vals = []
        if obj.shape[0] == 1:
            vals.append(obj[0][0])
        else:
            for k in range(obj.shape[0]):
                vals.append(int(hdf5_data[obj[k][0]][0][0]))
        meta_data[name] = vals

    hdf5_data[hdf5_data['/digitStruct/bbox'][index][0]].visititems(print_attrs)
    return meta_data

def _pickle_data(path):
    mat = join(_target_dir(), path, "digitStruct.mat")
    pck = join(_target_dir(), path, "pickle.dat")
    with h5py.File(mat, 'r') as f:
        n = f["/digitStruct/bbox"].shape[0]
        data = []
        c = 0
        for i in range(n):
            data.append(BoundingBoxes(_get_box_data(i, f)))
            c += 1
            if c % 100 == 0 or c == n:
                sys.stderr.write(" converting data: {}, {:6.2f}%  \r".format(mat, c / n * 100))
                sys.stderr.flush()
        sys.stderr.write("\n")
        pickle.dump(data, open(pck, "wb"))

Box = namedtuple("Box", ['height', 'label', 'left', 'top', 'width'])

class BoundingBoxes:
    def __init__(self, boxes):
        self.boxes = []
        n = len(boxes['label'])
        for i in range(n):
            b = Box(int(boxes['height'][i]), int(boxes['label'][i]), int(boxes['left'][i]), int(boxes['top'][i]), int(boxes['width'][i]))
            self.boxes.append(b)

    def size(self):
        return len(self.boxes)

    def box(self, idx):
        return self.boxes[idx]

    def boxes(self):
        return self.boxes

    def __repr__(self):
        return "BoundingBoxes[" + ",".join(self._as_str(i) for i in self.boxes) + "]"

    def _as_str(self, b):
        return "Box[label={},height={},left={},top={},width={}]".format(b.label, b.height, b.left, b.top, b.width)


def initialize(force=False):
    if force:
        shutil.rmtree(_target_dir())
    _init_dir()

    for url, path, siz in _datafiles:
        t = _target_filename(url)
        if not os.path.exists(t) or os.stat(t).st_size < siz:
            _download_file(url, t, siz)
        d = join(_target_dir(), path)
        if not os.path.exists(d):
            _uncompress(t)
        if path != "":
            d = join(_target_dir(), path, "pickle.dat")
            if not os.path.exists(d):
                _pickle_data(path)



class SVHN:
    def __init__(self):
        initialize()
        self.cropped = [None, None, None]
        self.bboxes = self._load_bounding_boxes()

    def _load_bounding_boxes(self):
        r = []
        for _nmin, _nmax, path in _ranges:
            fname = join(_target_dir(), path, "pickle.dat")
            r.append(pickle.load(open(fname, "rb")))
        return r

    def bounding_boxes(self, dataset, idx):
        assert dataset >= 0 and dataset < 3
        return self.bboxes[dataset][idx]

    def load_cropped(self, train=True, test=True, extra=False):
        if train:
            self.cropped[0] = sio.loadmat(join(_target_dir(), "train_32x32.mat"))
        if test:
            self.cropped[1] = sio.loadmat(join(_target_dir(), "test_32x32.mat"))
        if extra:
            self.cropped[2] = sio.loadmat(join(_target_dir(), "extra_32x32.mat"))
        return self

    def _check_cropped(self, dataset):
        assert dataset >= 0 and dataset < 3
        d = self.cropped[dataset]
        if d is None:
            raise Exception("Requested cropped dataset has not been initialized.")
        return d

    def get_cropped_dataset(self, dataset):
        d = self._check_cropped(dataset)
        return (d["X"], d["y"])

    def get_cropped_image(self, dataset, idx):
        X, y = self.get_cropped_dataset(dataset)
        return (X[:, :, :, idx], y[idx])

    def size_full(self, dataset):
        assert dataset >= 0 and dataset < 3
        return _ranges[dataset][1]

    def show_full_image(self, dataset, idx):
        plt.imshow(self.get_full_image(dataset, idx))
        plt.show()

    def get_full_image(self, dataset, idx):
        assert dataset >= 0 and dataset < 3
        assert idx >= 0 and idx < _ranges[dataset][1]
        i = Image.open(join(_target_dir(), _ranges[dataset][2], "{}.png".format(idx + 1)))
        i = np.asarray(i)
        return i

    def size_cropped(self, dataset):
        d = self._check_cropped(dataset)
        return len(d["y"])

if __name__ == "__main__":
    initialize()

    s = SVHN()

    # size of dataset
    assert s.size_full(TRAINING) == 33402
    assert s.size_full(TEST) == 13068
    assert s.size_full(EXTRA) == 202353

    # Get a full image.
    X = s.get_full_image(TRAINING, 0)

    # To display a full image of the "format 1" dataset.
    s.show_full_image(TRAINING, 0)

    # Load cropped training and test dataset. Use parameter extra=True
    # to also load the extra dataset.
    s.load_cropped(extra=True)

    # size of dataset
    assert s.size_cropped(TRAINING) == 73257
    assert s.size_cropped(TEST) == 26032
    assert s.size_cropped(EXTRA) == 531131

    # Get image data and label.
    X, y = s.get_cropped_image(TRAINING, 0)
    plt.imshow(X)
    plt.show()

    # Get bounding boxes for first training example.
    b = s.bounding_boxes(TRAINING, 0)
    n = b.size()           # number of bounding boxes
    for i in range(n):
        x = b.box(i)
        print("bounding box {}: label={}, top={}, height={}, left={}, width={}".format(i, x.label, x.top, x.height, x.left, x.width))

