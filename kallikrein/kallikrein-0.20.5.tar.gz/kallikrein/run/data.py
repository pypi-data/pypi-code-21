import inspect
from typing import Any
from types import FunctionType

from amino import Maybe, Either, L, _, Right, Empty, List, Boolean, Path, Try
from amino.list import Lists
from amino.util.string import snake_case
from amino.instances.std.datetime import TimedeltaInstances  # NOQA
from amino.either import ImportFailure, InvalidLocator


def infer_path(obj: Any) -> Maybe[Path]:
    return Try(inspect.getfile, obj) // L(Try)(Path, _)


class Selector:

    @property
    def specific(self) -> Boolean:
        return Boolean(isinstance(self, (MethodSelector, FileMethodSelector)))


class ModuleSelector(Selector):

    def __init__(self, mod: str) -> None:
        self.mod = mod


class ClassSelector(Selector):

    def __init__(self, mod: str, cls: str) -> None:
        self.mod = mod
        self.cls = cls


class MethodSelector(Selector):

    def __init__(self, mod: str, cls: str, method: str) -> None:
        self.mod = mod
        self.cls = cls
        self.method = method


class DirSelector(Selector):

    def __init__(self, path: Path) -> None:
        self.path = path


class FileSelector(Selector):

    def __init__(self, path: Path) -> None:
        self.path = path


class FileClassSelector(Selector):

    def __init__(self, path: Path, cls: str) -> None:
        self.path = path
        self.cls = cls


class FileMethodSelector(Selector):

    def __init__(self, path: Path, cls: str, method: str) -> None:
        self.path = path
        self.cls = cls
        self.method = method


class LineSelector(Selector):

    def __init__(self, path: str, lnum: int) -> None:
        self.path = path
        self.lnum = lnum


def convert_underscores(data: str) -> str:
    return data.replace('_', ' ')


invalid_spec_names = List('setup', 'teardown')


class SpecLocation:
    no_docstring_msg = 'spec class `{}` has no docstring'

    @staticmethod
    def create(file: Maybe[Path], mod: str, cls: str, meth: Maybe[str], selector: Selector, allow_empty: bool
               ) -> Either[ImportFailure, 'SpecLocation']:
        return (
            Either.import_name(mod, cls)
            .filter_with(inspect.isclass, lambda a: InvalidLocator(f'not a class: {a}')) /
            L(SpecLocation)(file, mod, _, meth, selector, allow_empty)
        )

    @staticmethod
    def from_path(path: str) -> Either[List[ImportFailure], 'SpecLocation']:
        parts = Lists.split(path, '.')
        def create(mod: str, cls: type, meth: Maybe[str]) -> SpecLocation:
            selector = (
                meth /
                L(MethodSelector)(mod, cls.__name__, _) |
                ClassSelector(mod, cls.__name__)
            )
            return SpecLocation(infer_path(cls), mod, cls, meth, selector, False)
        def or_method(pre: Either[List[ImportFailure], SpecLocation]) -> Either[List[ImportFailure], SpecLocation]:
            return (
                pre
                if len(parts) < 2 else
                pre
                .accum_error(
                    Right(parts.drop_right(2).join_dot)
                    .product2(Either.import_path(parts.drop_right(1).join_dot), Right(parts.last))
                    .lmap(List)
                )
            )
        cls_only = (
            Right(parts.drop_right(1).join_dot)
            .product2(Either.import_path(path), Right(Empty()))
            .lmap(List)
        )
        return or_method(cls_only).map3(create)

    def __init__(self, file: Maybe[Path], mod: str, cls: type, meth: Maybe[str], selector: Selector, allow_empty: bool
                 ) -> None:
        self.file = file
        self.mod = mod
        self.cls = cls
        self.meth = meth
        self.selector = selector
        self.allow_empty = Boolean(allow_empty)

    def __str__(self) -> str:
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__, self.mod, self.cls, self.meth, self.allow_empty)

    def __repr__(self) -> str:
        return str(self)

    @property
    def use_all_specs(self) -> Boolean:
        return Boolean(hasattr(self.cls, '__all_specs__'))

    @property
    def need_no_doc(self) -> Boolean:
        return self.selector.specific | self.use_all_specs

    @property
    def cls_methods(self) -> List[str]:
        def filt(member: Any) -> bool:
            return (
                isinstance(member, FunctionType) and
                not member.__name__.startswith('_') and
                member.__name__ not in invalid_spec_names
            )
        valid = inspect.getmembers(self.cls, predicate=filt)
        return Lists.wrap(valid) / Lists.wrap // _.head

    @property
    def fallback_doc(self) -> Maybe[str]:
        meth = lambda name: '{} ${}'.format(convert_underscores(name), name)
        def synthetic() -> List[str]:
            meths = (self.meth / meth / List) | (self.cls_methods / meth)
            cls = convert_underscores(snake_case(self.cls.__name__))
            return meths.cons(cls).join_lines
        return self.need_no_doc.m(synthetic)

    @property
    def doc(self) -> Either[str, str]:
        return (
            Maybe(self.cls.__doc__)
            .o(lambda: self.fallback_doc)
            .to_either(SpecLocation.no_docstring_msg.format(self.cls.__name__))
        )

__all__ = ('SpecLocation',)
