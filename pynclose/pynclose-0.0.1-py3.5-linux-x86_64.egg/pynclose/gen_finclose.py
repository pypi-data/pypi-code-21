import pybindgen


def generate(file_):
    mod = pybindgen.Module('finclose')
    mod.add_include('"my-module.h"')
    mod.add_function('MyModuleDoAction', None, [])
    mod.generate(file_)
