from pytest import raises
from attr import attrs, attrib
from emote_utils import SocialsFactory, NoSuffixError, NoObjectError, \
     NoNamesError, Suffix


@attrs
class PretendObject:
    """Test emotes with this object."""

    name = attrib()
    gender = attrib()


boy = PretendObject('Bill', 'his')
girl = PretendObject('Jane', 'her')
f = SocialsFactory()


@f.suffix('name', 'n')
def name(obj, suffix):
    return ('you', obj.name)


@f.suffix('his', 'her')
def gender(obj, suffix):
    return ('your', obj.gender)


def test_defaults():
    assert SocialsFactory().suffixes == {}
    assert f.default_index == 0
    assert f.default_suffix == 'n'


# get_strings tests.

def test_one():
    expected = ['you', boy.name]
    strings = f.get_strings('%1n', [boy])
    assert strings == expected
    strings = f.get_strings('%1', [boy])
    assert strings == expected
    strings = f.get_strings('%', [boy])
    assert strings == expected


def test_multiple():
    expected = [
        f'you {girl.name}', f'{boy.name} you', f'{boy.name} {girl.name}'
    ]
    strings = f.get_strings('%1n %2n', [boy, girl])
    assert strings == expected
    strings = f.get_strings('%1n %2', [boy, girl])
    assert strings == expected
    strings = f.get_strings('% %2', [boy, girl])
    assert strings == expected


def test_title():
    strings = f.get_strings('%N smiles.', [boy])
    assert strings == ['You smiles.', 'Bill smiles.']


def test_nameless_suffix():
    with raises(NoNamesError):
        f.suffix()


def test_suffix_error():
    suffix = 'wontwork'
    with raises(NoSuffixError):
        f.get_strings(f'%1{suffix}', [boy])


def test_object_error():
    with raises(NoObjectError):
        f.get_strings('%2n', [boy])


def test_get_suffixes():
    r = f.get_suffixes()
    assert len(r) == 2
    assert isinstance(r[0], Suffix)
    assert isinstance(r[1], Suffix)
    assert r[0].func in [name, gender]
    assert r[0].func in [name, gender]
    if r[0].func is name:
        assert r[0].names == ['n', 'name']
    else:
        assert r[0].names == ['his', 'her']
