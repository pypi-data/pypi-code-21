from collections import OrderedDict
from itertools import chain
from typing import Dict, Iterable, Iterator, Union, Optional


_Iterable = Iterable[Optional[Union[str, Dict, Iterable]]]
_Dict = Dict[Optional[Union[str, Iterable[str]]], bool]


class CssClasses:
    def __init__(self, *args, underscore_as_dash: bool=True, **kwargs):
        """
        :param underscore_as_dash: replace underscore with dash in kwargs
        """
        self._underscore_as_dash = underscore_as_dash
        self._args = args
        self._kwargs = kwargs

    @classmethod
    def _dict_to_classes(cls, item: _Dict,
                         underscore_as_dash: bool=False) -> Iterator[str]:
        for k, v in item.items():
            if k and v:
                if isinstance(k, str):
                    if underscore_as_dash:
                        k = k.replace('_', '-')
                    yield k
                elif isinstance(k, Iterable):
                    yield from cls._iterable_to_classes(k)

    @classmethod
    def _iterable_to_classes(cls, iterable: _Iterable) -> Iterator[str]:
        for item in iterable:
            if not item:
                continue
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                yield from cls._dict_to_classes(item)
            elif isinstance(item, Iterable):
                yield from cls._iterable_to_classes(item)
            else:
                raise ValueError(f'CSS class "{item!s}" should be a string')

    def __str__(self):
        classes = chain(
            self._iterable_to_classes(self._args),
            self._dict_to_classes(
                item=self._kwargs,
                underscore_as_dash=self._underscore_as_dash,
            ),
        )
        unique_ever_seen = OrderedDict.fromkeys(' '.join(classes).split(' '))
        return ' '.join(unique_ever_seen.keys())


def css_classes(*args, **kwargs) -> str:
    return str(CssClasses(*args, **kwargs))
