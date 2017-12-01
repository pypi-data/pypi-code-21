from importlib import (machinery,
                       util)
from typing import (Any,
                    Callable)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from .utils import (names,
                    modules_paths)


@strategies.composite
def empty_modules_specs_factory(draw: Callable[[SearchStrategy], Any],
                                *,
                                modules_names: SearchStrategy,
                                modules_origins: SearchStrategy
                                ) -> machinery.ModuleSpec:
    name = draw(modules_names)
    loader = None
    origin = draw(modules_origins)
    pump_file(origin)
    result = machinery.ModuleSpec(name=name,
                                  loader=loader,
                                  origin=origin)
    result.has_location = True
    return result


def pump_file(path: str) -> None:
    with open(path, mode='w') as file:
        file.write('\n')


empty_modules_specs = empty_modules_specs_factory(modules_names=names,
                                                  modules_origins=modules_paths)
empty_modules = empty_modules_specs.map(util.module_from_spec)
