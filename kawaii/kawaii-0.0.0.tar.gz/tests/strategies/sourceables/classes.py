import os
from importlib import import_module
from typing import (Any,
                    Type,
                    Callable)

from hypothesis import strategies
from hypothesis.searchstrategy import SearchStrategy

from .utils import (names,
                    modules_paths)

empty_class_template = ('class {name}:\n'
                        '    pass\n')


@strategies.composite
def empty_classes_factory(draw: Callable[[SearchStrategy], Any],
                          *,
                          classes_names: SearchStrategy,
                          classes_origins: SearchStrategy) -> Type:
    name = draw(classes_names)
    origin = draw(classes_origins)

    definition = (empty_class_template
                  .format(name=name))

    with open(origin, mode='w') as file:
        file.write(definition)

    module_file_name = os.path.basename(origin)
    module_name, _ = module_file_name.split(os.extsep)
    module = import_module(module_name)
    return getattr(module, name)


empty_classes = empty_classes_factory(classes_names=names,
                                      classes_origins=modules_paths)
