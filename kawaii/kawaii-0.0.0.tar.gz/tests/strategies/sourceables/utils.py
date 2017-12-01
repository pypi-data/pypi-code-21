import operator
import string
import sys
import tempfile
from importlib.machinery import SOURCE_SUFFIXES

from hypothesis import strategies

names_characters = strategies.sampled_from(string.ascii_letters + '_')
names = strategies.text(names_characters,
                        min_size=1)


def to_python_module(path: str,
                     *,
                     module_suffix: str = SOURCE_SUFFIXES[0]) -> str:
    return path + module_suffix


modules_paths = (strategies.builds(tempfile.mkstemp)
                 .map(operator.itemgetter(1))
                 .map(to_python_module))

# make modules importable
sys.path.append(tempfile.gettempdir())
