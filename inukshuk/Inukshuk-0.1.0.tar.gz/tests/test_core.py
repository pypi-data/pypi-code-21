import os.path
from inukshuk.engine import Engine
from inukshuk.loader import StringsLoader
from inukshuk.template import Template


class SimpleIterator:
    def __init__(self, items):
        self._items = list(items)
        self._locked = False

    def skip(self, num):
        self._ensureUnlocked()
        self._items = self._items[num:]
        return self

    def limit(self, num):
        self._ensureUnlocked()
        self._items = self._items[:num]
        return self

    def __iter__(self):
        self._locked = True
        return iter(self._items)

    def __len__(self):
        self._locked = True
        return len(self._items)

    def _ensureUnlocked(self):
        if self._locked:
            raise Exception("The iterator is locked.")


def test_for1():
    tpl = Template('{%for i in it.skip(4).limit(3)%}{{i}} {%endfor%}')
    out = tpl.render({'it': SimpleIterator(range(10))})
    assert out == '4 5 6 '


def test_for1_compiled():
    loader = StringsLoader({
        'foo': '{%for i in it.skip(4).limit(3)%}{{i}} {%endfor%}'})
    cache_dir = os.path.join(os.path.dirname(__file__), '__inukcache__')
    engine = Engine(loader=loader,
                    compile_templates=True,
                    compile_cache_dir=cache_dir)
    tpl = engine.getTemplate('foo')
    out = tpl.render({'it': SimpleIterator(range(10))})
    assert out == '4 5 6 '
