from collections import Iterable, OrderedDict
from typing import List, Dict


class CssClasses:
    def __init__(self, *args, underscore_as_dash: bool=True, **kwargs):
        """
        :param underscore_as_dash: replace underscore with dash in kwargs
        """
        self._underscore_as_dash = underscore_as_dash
        self._args = args
        self._kwargs = kwargs

    @classmethod
    def _dict_to_classes(cls, item: Dict[str, bool],
                         underscore_as_dash: bool=False) -> List[str]:
        classes = []
        for k, v in item.items():
            if k and v:
                if isinstance(k, str):
                    if underscore_as_dash:
                        k = k.replace('_', '-')
                    classes.append(k)
                elif isinstance(k, Iterable):
                    classes.extend(cls._iterable_to_classes(k))
        return classes

    @classmethod
    def _iterable_to_classes(cls, iterable) -> List[str]:
        classes = []
        for item in iterable:
            if isinstance(item, str):
                classes.append(item)
            elif isinstance(item, dict):
                classes.extend(cls._dict_to_classes(item))
            elif isinstance(item, Iterable):
                classes.extend(cls._iterable_to_classes(item))
            else:
                raise ValueError(f'CSS class "{item!s}" should be a string')
        return classes

    def _args_to_classes(self):
        return self._iterable_to_classes(self._args)

    def _kwargs_to_classes(self):
        return self._dict_to_classes(
            item=self._kwargs,
            underscore_as_dash=self._underscore_as_dash,
        )

    def __str__(self):
        classes = *self._args_to_classes(), *self._kwargs_to_classes()
        unique_ever_seen = OrderedDict.fromkeys(' '.join(classes).split(' '))
        return ' '.join(unique_ever_seen.keys())


def css_classes(*args, **kwargs) -> str:
    return str(CssClasses(*args, **kwargs))
