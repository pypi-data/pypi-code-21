from pybindgen import *

def generate(file):
    mod = Module('inclose')
    mod.add_include('"In-Close4.h"')
    mod.add_function('run_search', retval('std::string'), [
        param('std::string', 'infile'),
        param('unsigned int', 'minimal_intent'),
        param('unsigned int', 'minimal_extent'),
    ])
    mod.generate(file)
