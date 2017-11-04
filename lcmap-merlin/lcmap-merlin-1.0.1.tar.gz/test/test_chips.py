from base64 import b64encode
from cytoolz import drop
from merlin import chips as mc
from merlin import chip_specs as mcs
from functools import partial
from functools import reduce
from itertools import product
from numpy.random import randint
import numpy as np


def test_difference():
    assert mc.difference(3456, 3000) == 456
    assert mc.difference(3456, 5000) == 3456


def test_near():
    assert mc.near(2999, 3000, 0) == 0
    assert mc.near(3000, 3000, 0) == 3000
    assert mc.near(-2999, -3000, 0) == 0
    assert mc.near(-3000, -3000, 0) == -3000


def test_point_to_chip():
    assert mc.point_to_chip(2999, -2999, 3000, -3000, 0, 0) == (0, 0)
    assert mc.point_to_chip(3000, -3000, 3000, -3000, 0, 0) == (3000, -3000)


def test_snap():
    spec = {'chip_x': 3000, 'chip_y': -3000, 'shift_x': 0, 'shift_y': 0}
    assert (0, 0) == mc.snap(2999, -2999, spec)
    assert (3000, 0) == mc.snap(3000, -2999, spec)
    assert (0, -3000) == mc.snap(2999, -3000, spec)
    assert (3000, -3000) == mc.snap(3000, -3000, spec)


def test_coordinates():
    spec   = {'chip_x': 3000, 'chip_y': -3000, 'shift_x': 0, 'shift_y': 0}
    coords = ((0, 0), (0, -3000), (3000, 0), (3000, -3000))
    assert coords == mc.coordinates(0, 0, 3000, -3000, spec)


def test_numpy():
    assert len("This is tested in test_aardvark:test_to_numpy()") > 0


def test_locations():
    spec = {'data_shape': (2, 2), 'pixel_x': 30, 'pixel_y': -30}
    locs = np.array([[[0, 0], [0, -30]], [[30, 0], [30, -30]]])
    assert np.array_equal(locs, mc.locations(0, 0, spec))
    

def test_dates():
    inputs = list()
    inputs.append({'acquired': '2015-04-01'})
    inputs.append({'acquired': '2017-04-01'})
    inputs.append({'acquired': '2017-01-01'})
    inputs.append({'acquired': '2016-04-01'})
    assert set(mc.dates(inputs)) == set(map(lambda d: d['acquired'], inputs))


def test_trim():
    inputs = list()
    inputs.append({'include': True, 'acquired': '2015-04-01'})
    inputs.append({'include': True, 'acquired': '2017-04-01'})
    inputs.append({'include': False, 'acquired': '2017-01-01'})
    inputs.append({'include': True, 'acquired': '2016-04-01'})
    included = mc.dates(filter(lambda d: d['include'] is True, inputs))
    trimmed = mc.trim(inputs, included)
    assert len(list(trimmed)) == len(included)
    assert set(included) == set(map(lambda x: x['acquired'], trimmed))


def test_to_numpy():
    """ Builds combos of shapes and numpy data types and tests
        aardvark.to_numpy() with all of them """

    def _ubid(dtype, shape):
        return dtype + str(shape)

    def _chip(dtype, shape, ubid):
        limits = np.iinfo(dtype)
        length = reduce(lambda accum, v: accum * v, shape)
        matrix = randint(limits.min, limits.max, length, dtype).reshape(shape)
        return {'ubid': ubid, 'data': b64encode(matrix)}

    def _spec(dtype, shape, ubid):
        return {'ubid': ubid, 'data_shape': shape, 'data_type': dtype.upper()}

    def _check(npchip, specs_byubid):
        spec = specs_byubid[npchip['ubid']]
        assert npchip['data'].dtype.name == spec['data_type'].lower()
        assert npchip['data'].shape == spec['data_shape']
        return True

    # Test combos of dtypes/shapes to ensure data shape and type are unaltered
    combos = tuple(product(('uint8', 'uint16', 'int8', 'int16'),
                           ((3, 3), (1, 1), (100, 100))))

    # generate the chip_specs and chips
    chips = [_chip(*c, _ubid(*c)) for c in combos]
    specs = [_spec(*c, _ubid(*c)) for c in combos]
    specs_byubid = mcs.byubid(specs)

    # run assertions
    checker = partial(_check, specs_byubid=specs_byubid)
    all(map(checker, mc.to_numpy(chips, specs_byubid)))


def test_identity():
    chip = {'x': 1, 'y': 2, 'acquired': '1980-01-01', 'ubid': 'a/b/c/d'}
    assert mc.identity(chip) == tuple([chip['x'], chip['y'],
                                       chip['ubid'], chip['acquired']])


def test_deduplicate():
    inputs = [{'x': 1, 'y': 2, 'acquired': '1980-01-01', 'ubid': 'a/b/c/d'},
              {'x': 1, 'y': 2, 'acquired': '1980-01-01', 'ubid': 'a/b/c/d'},
              {'x': 2, 'y': 2, 'acquired': '1980-01-01', 'ubid': 'a/b/c/d'},
              {'x': 1, 'y': 3, 'acquired': '1980-01-01', 'ubid': 'a/b/c/d'},
              {'x': 1, 'y': 2, 'acquired': '1980-01-02', 'ubid': 'a/b/c/d'},
              {'x': 1, 'y': 2, 'acquired': '1980-01-01', 'ubid': 'a/b/c'}]

    assert mc.deduplicate(inputs) == tuple(drop(1, inputs))
