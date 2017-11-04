import pytest
from .. import ApptList


@pytest.fixture
def a():
    return ApptList()


def test_creating_new_object(a):
    a.add('cmplx', 'hs', 100500, spam='ham')
    assert a['cmplx']['hs'][100500]['spam'] == 'ham'


def test_existing_complex(a):
    a['cmplx'] = dict(test={'2': 2})
    a.add('cmplx', 'hs', 100500, spam='ham')
    assert a['cmplx']['hs'][100500]['spam'] == 'ham'
    assert 'test' in a['cmplx'].keys()


def test_existing_house(a):
    a['cmplx'] = dict(
        hs=dict(
            someid={
                'spam': 'EGGS',
            },
        ),
    )

    a.add('cmplx', 'hs', 100501, spam='HAM')
    assert a['cmplx']['hs']['someid']['spam'] == 'EGGS'
    assert a['cmplx']['hs'][100501]['spam'] == 'HAM'
