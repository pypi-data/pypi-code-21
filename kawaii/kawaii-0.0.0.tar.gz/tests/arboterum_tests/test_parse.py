from types import (ModuleType,
                   FunctionType)

from kawaii.arboretum import parse
from kawaii.types import SyntaxTreeType


def test_class(empty_class: FunctionType) -> None:
    tree = parse.from_sourceable(empty_class)

    assert isinstance(tree, SyntaxTreeType)
    assert len(tree.body) == 1


def test_function(empty_function: FunctionType) -> None:
    tree = parse.from_sourceable(empty_function)

    assert isinstance(tree, SyntaxTreeType)
    assert len(tree.body) == 1


def test_module(empty_module: ModuleType) -> None:
    tree = parse.from_sourceable(empty_module)

    assert isinstance(tree, SyntaxTreeType)
    assert not tree.body
