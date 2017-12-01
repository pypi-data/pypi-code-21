from astmonkey import visitors

from kawaii.types import (SyntaxTreeType,
                          SourceableType)


def to_sourcable(source: str) -> SourceableType:
    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = {}
    exec(source, namespace)
    return


def to_source(tree: SyntaxTreeType) -> str:
    return visitors.to_source(tree)
