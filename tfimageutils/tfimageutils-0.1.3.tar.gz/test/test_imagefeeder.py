import numpy as np

from tfimageutils import ImageFeeder

INPUT_FEATURE_SHAPE = (7, 10, 4)
INPUT_FEATURE_AMOUNT = 7 * 10 * 4  # (height, width, depth)
OUTPUT_CLASSES_AMOUNT = 500  # (0 - 499)


def test_inner_variables():
    imf = ImageFeeder('testdata', lambda fn: fn[-7:-4])

    fq_tr = imf.file_queue['train']
    fq_te = imf.file_queue['test']
    fq_va = imf.file_queue['validation']

    assert imf.split == [0.7, 0.15, 0.15]
    assert len(fq_tr) == int(500 * 0.7)
    assert len(fq_te) == len(fq_va) == int(500 * 0.15)
    assert len(fq_tr) + len(fq_te) + len(fq_va) == 500

    assert len(imf.classes) == OUTPUT_CLASSES_AMOUNT


def test_defaultconfiguration():
    imf = ImageFeeder('testdata', lambda fn: fn[-7:-4])

    for i in range(1, 600, 75):
        X, Y = imf.get_batch('train', i)
        assert X.shape == (INPUT_FEATURE_AMOUNT, i)
        assert Y.shape == (OUTPUT_CLASSES_AMOUNT, i)


def test_iterating():
    imf = ImageFeeder('testdata', lambda fn: fn[-7:-4])

    X1, Y1 = imf.get_batch('train', 20)
    X2, Y2 = imf.get_batch('train', 20)

    assert not np.array_equal(X1, Y1) and not np.array_equal(Y1, Y2)


def test_rowstacking():
    imf = ImageFeeder('testdata', lambda fn: fn[-7:-4], stack_direction='row')

    for i in range(1, 600, 75):
        X, Y = imf.get_batch('train', i)
        assert X.shape == (i, INPUT_FEATURE_AMOUNT)
        assert Y.shape == (i, OUTPUT_CLASSES_AMOUNT)


def test_otherconfigs():
    imf = ImageFeeder('testdata', lambda fn: fn[-6:-4])
    assert len(imf.classes) == 100
    imf_10 = ImageFeeder('testdata', lambda fn: fn[-5:-4])
    assert len(imf_10.classes) == 10
    imf_idx = ImageFeeder('testdata', lambda fn: fn[-5])
    assert len(imf_idx.classes) == 10
    assert imf_10.classes == imf_idx.classes


def test_nonrandomized():
    imf = ImageFeeder('testdata', lambda fn: fn[-7:-4], shuffle=False)

    b1, _ = imf.get_batch('train', 100)

    imf.refresh_iterators()
    b2, _ = imf.get_batch('train', 100)

    assert b1.shape == b2.shape
    assert np.array_equal(b1, b2)

    b3, _ = imf.get_batch('train', 100)
    assert not np.array_equal(b2, b3)


def test_onehotting():
    imf_noh = ImageFeeder('testdata', lambda fn: fn[-7:-4], shuffle=False, use_one_hot=False)
    imf_oh = ImageFeeder('testdata', lambda fn: fn[-7:-4], shuffle=False, use_one_hot=True)

    for i in range(1, 5):
        ohx, ohy = imf_oh.get_batch('train', i)
        nohx, nohy = imf_noh.get_batch('train', i)

        reverted, prob = imf_noh.get_text_label_and_prob(ohy, apply_softmax=True)
        assert np.array_equiv([nohy], reverted)


def test_onehotting_row():
    imf_noh = ImageFeeder('testdata', lambda fn: fn[-7:-4], shuffle=False, use_one_hot=False, stack_direction='row')
    imf_oh = ImageFeeder('testdata', lambda fn: fn[-7:-4], shuffle=False, use_one_hot=True, stack_direction='row')

    for i in range(1, 5):
        ohx, ohy = imf_oh.get_batch('train', i)
        nohx, nohy = imf_noh.get_batch('train', i)
        reverted, prob = imf_noh.get_text_label_and_prob(ohy, apply_softmax=True)
        assert np.array_equiv([nohy], np.array(reverted).reshape(i, 1))

# def test_nonflattened():
#     imf = ImageFeeder('testdata', lambda fn: fn[-7:-4], flatten_input=False)
#     X, Y = imf.get_batch('train', 20)
#     assert X.shape == INPUT_FEATURE_SHAPE + (20,)
