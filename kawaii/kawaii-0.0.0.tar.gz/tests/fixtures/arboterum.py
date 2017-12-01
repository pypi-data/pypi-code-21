from types import (ModuleType,
                   FunctionType)

import pytest

from tests import strategies
from tests.utils import example


@pytest.fixture(scope='function')
def empty_class() -> type:
    return example(strategies.empty_classes)


@pytest.fixture(scope='function')
def empty_function() -> FunctionType:
    return example(strategies.empty_functions)


@pytest.fixture(scope='function')
def empty_module() -> ModuleType:
    return example(strategies.empty_modules)
