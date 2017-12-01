import ast
import inspect

from kawaii.types import (SourceableType,
                          SyntaxTreeType)


def from_sourceable(sourceable: SourceableType) -> SyntaxTreeType:
    return from_source(inspect.getsource(sourceable))


def from_source(source: str) -> SyntaxTreeType:
    return ast.parse(source)
