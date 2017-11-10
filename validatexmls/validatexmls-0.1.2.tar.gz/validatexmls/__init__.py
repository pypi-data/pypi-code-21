import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    return os.path.join(_ROOT, 'data', path)


s = get_data('testfile.txt')
print(s, os.path.exists(s))

s = get_data('xsd/BC9.xsd')
print(s, os.path.exists(s))

s = get_data('input/35104616_49_30527.XML')
print(s, os.path.exists(s))
pass
