from pybindgen import *


MODULE_INCLOSE = 'inclose_package/inclose-binding.cpp'


def generate(file):
    mod = Module('inclose')
    mod.add_include('"In-Close4.h"')
    mod.add_function('run_search', retval('std::string'), [
        param('std::string', 'infile'),
        param('unsigned int', 'minimal_intent'),
        param('unsigned int', 'minimal_extent'),
    ])
    mod.generate(file)


if __name__ == '__main__':
    with open(MODULE_INCLOSE, 'w') as fd:
        print('Generating file {}'.format(MODULE_INCLOSE))
        generate(fd)
