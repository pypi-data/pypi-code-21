import ast
from types import (CodeType,
                   ModuleType,
                   MethodType,
                   FunctionType,
                   TracebackType,
                   FrameType)
from typing import (Union,
                    Type)

SyntaxTreeType = ast.AST
SourceableType = Union[CodeType, ModuleType,
                       Type, MethodType, FunctionType,
                       TracebackType, FrameType]
