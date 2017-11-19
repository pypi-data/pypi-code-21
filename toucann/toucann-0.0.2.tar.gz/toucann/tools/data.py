import csv
import numpy as np
import re

LETTERS_RU = dict(zip(list("АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"), list(range(32))))


def get_from_csv(path):
    try:
        X_, d_ = [], []
        with open(path) as csvFile:
            reader = csv.reader(csvFile, delimiter=';', quotechar='|')
            for row in reader:
                X_.append([float(f) for f in row[:len(row)-1]])
                d_.append(float(row[len(row)-1]))
        return X_, d_
    except FileNotFoundError:
        print("Error 0. File is not found.")


def split_4_to_1(X_, d_):
    l = len(d_)
    X_learn = [X_[i] for i in range(4 * l // 5)]
    X_pract = [X_[i] for i in range(4 * l // 5, l)]
    d_learn = [d_[i] for i in range(4 * l // 5)]
    d_pract = [d_[i] for i in range(4 * l // 5, l)]
    return X_learn, d_learn, X_pract, d_pract


def read_pgm(filename, byteorder='>'):
    """Return image data from a raw PGM file as numpy array.

    Format specification: http://netpbm.sourceforge.net/doc/pgm.html

    """
    with open(filename, 'rb') as f:
        buffer = f.read()
    try:
        header, width, height, maxval = re.search(
            b"(^P5\s(?:\s*#.*[\r\n])*"
            b"(\d+)\s(?:\s*#.*[\r\n])*"
            b"(\d+)\s(?:\s*#.*[\r\n])*"
            b"(\d+)\s(?:\s*#.*[\r\n]\s)*)", buffer).groups()
    except AttributeError:
        raise ValueError("Not a raw PGM file: '%s'" % filename)
    return np.frombuffer(buffer,
                            dtype='u1' if int(maxval) < 256 else byteorder+'u2',
                            count=int(width)*int(height),
                            offset=len(header)
                            ).reshape((int(height), int(width)))


def normalize(img):
    return (255 - img) / 255


def pack(data, labels):
    """ Turns learning set into a list of dicts = [{'x': X_[0], 'd': d_[0]}, {'x': X_[1], 'd': d_[1]}, ...]
    :return: pack : dict (see above)
    """
    assert np.ndim(data) != len(labels), 'Wrong data-set! ERR: Count of learning input vectors'
    pack = []
    for i in range(len(labels)):
        pack.append({'x': np.array(data[i]), 'd': labels[i]})
    return pack

if __name__ == '__main__':
    print(LETTERS_RU)