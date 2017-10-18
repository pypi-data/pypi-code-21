from pytest import raises
from emote_utils import SocialsFactory, NoMatchError


f = SocialsFactory()
boy = object()
girl = object()


# convert_emote_string tests


def simple_match(name, *args, **kwargs):
    assert not args
    assert not kwargs
    if name == 'boy':
        return boy
    elif name == 'girl':
        return girl
    else:
        return


def advanced_match(name, arg, hello=None, test=None):
    assert arg == 'test'
    assert hello == 'world'
    assert test == 'this'
    return simple_match(name)


def test_works():
    string, perspectives = f.convert_emote_string(
        '% looks at {girl}.', simple_match, [boy]
    )
    assert perspectives == [boy, girl]
    assert string == '% looks at %2.'


def test_fails():
    with raises(NoMatchError):
        f.convert_emote_string('% smiles at {jack}.', simple_match, [boy])


def test_with_args():
    f.convert_emote_string('', advanced_match, [])
