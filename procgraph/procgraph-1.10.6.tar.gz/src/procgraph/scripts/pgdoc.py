from collections import namedtuple
from optparse import OptionParser
import os
import sys

from ..core.block import Block
from ..core.block_meta import (split_docstring, FIXED, VARIABLE,
                              DEFINED_AT_RUNTIME)
from ..core.import_magic import get_module_info
from ..core.model_loader import  ModelSpec
from ..core.registrar import default_library


# TODO: make it possible to document simple functions 
type_block = 'block'
type_model = 'model'
type_simple_block = 'simple_block'

ModelDoc = namedtuple('ModelDoc',
                      'name source module type implementation input '
                      'output config desc desc_rest')

# module : reference to actual module instance
ModuleDoc = namedtuple('ModuleDoc',
                       'name blocks desc desc_rest module procgraph_info')


def get_module_name_with_doc(original_module_name):
    assert isinstance(original_module_name, str)

    module_name = original_module_name

    while True:
        module = __import__(module_name, fromlist=['x'])
        if module.__doc__:
            return module.__name__

        parent_name = '.'.join(module.__name__.split('.')[:-1])

        # Empty!!
        if not parent_name or parent_name == 'procgraph':
            return original_module_name

        module_name = parent_name


def collect_info(block_type, block_generator):

    if isinstance(block_generator, ModelSpec):
        parsed_model = block_generator.parsed_model
        type = type_model #@ReservedAssignment
        implementation = None
        assert isinstance(block_generator.defined_in, str)
        module = get_module_name_with_doc(block_generator.defined_in)

        source = parsed_model.where.filename
        desc, desc_rest = split_docstring(parsed_model.docstring)

        config = parsed_model.config
        input = parsed_model.input #@ReservedAssignment
        output = parsed_model.output

    elif issubclass(block_generator, Block):
        type = type_block #@ReservedAssignment
        implementation = block_generator

        if block_generator.defined_in:
            original_module_name = block_generator.defined_in
            assert isinstance(block_generator.defined_in, str)
        else:
            original_module_name = block_generator.__module__

        assert isinstance(original_module_name, str)

        original_module = __import__(original_module_name, fromlist=['x'])

        source = original_module.__file__
        module = get_module_name_with_doc(original_module_name)

        desc, desc_rest = split_docstring(block_generator.__doc__)

        config = block_generator.config
        input = block_generator.input #@ReservedAssignment
        output = block_generator.output

    else:
        assert False

    #  print block_type, module

    if source.endswith('.pyc'):
        source = source[:-1]

    if not isinstance(module, str):
        print block_type, 'has it wrong'

    return ModelDoc(name=block_type, source=source, type=type,
                    module=module, implementation=implementation,
                    desc=desc, desc_rest=desc_rest,
                    input=input, output=output, config=config)


def get_all_info(library):

    blocks = []
    for block_type, generator in library.name2block.items():
        blocks.append(collect_info(block_type, generator))

    # get all modules
    module_names = set(map(lambda x: x.module, blocks))
    # create module -> list of blocks

    modules = {}

    for name in module_names:
        module_blocks = dict(map(lambda block: (block.name, block),
                         filter(lambda block: block.module == name, blocks)))

        actual = __import__(name, fromlist=['ceremony'])

        desc, desc_rest = split_docstring(actual.__doc__)

        try:
            procgraph_info = get_module_info(name)
        except Exception as e:
            print("Warning: procgraph_info missing for %r: %s" % (name, e))
            procgraph_info = {}

        modules[name] = ModuleDoc(name=name, blocks=module_blocks,
                                  desc=desc, desc_rest=desc_rest,
                                  module=actual, procgraph_info=procgraph_info)

    return modules


def main():
    parser = OptionParser()

    parser.add_option("--output", default='pgdoc.rst', help="RST output file.")
    parser.add_option("--translate", action='append', default=[],
                      help="directory=url")

    (options, args) = parser.parse_args()

    translate = {}
    for couple in options.translate:
        root, reference = couple.split('=', 1)
        root = os.path.realpath(root)
        translate[root] = reference

    if not args:
        print("Give at least one module.")
        sys.exit(-1)

    given_modules = args

    for module in given_modules:
        __import__(module, fromlist=['ceremony'])

    library = default_library

    all_modules = get_all_info(library)

    # check they were not empty
    for module in given_modules:
        if not module in all_modules:
            print('Warning: I found no blocks defined *directly* in %r. '
                  'No documentation will be generated.' % module)

    # only retain the ones that we have to document 
    modules = {}
    for module in all_modules:
        for arg in args:
            if module.startswith(arg):
                modules[module] = all_modules[module]

    f = open(options.output, 'w')

    f.write('.. |towrite| replace:: **to write** \n\n')

    # first write a summary
    for module_name in sorted(modules):
        module = modules[module_name]

        #f.write('%s\n' % module_reference(module.name))
        f.write('\nPackage ``%s``\n' % module.name)
        f.write('-' * 60 + '\n\n')

        d = getstr(module.desc, '%s description' % module.name)
        f.write(d + '\n\n')

        rows = []
        for block_name in sorted(module.blocks):
            block = module.blocks[block_name]
            desc = getstr(block.desc, '%s:%s desc' % (module_name, block_name))
            name = block_reference(block.name)
            rows.append((name, desc))
        write_rst_table(f, rows, widths=[30, 70])

    for module_name in sorted(modules):
        module = modules[module_name]

        f.write(module_anchor(module.name))
        f.write(rst_class('procgraph:module'))
        f.write('Package ``%s``\n' % module.name)
        f.write('=' * 60 + '\n\n\n')

        f.write(rst_class('procgraph:desc'))
        f.write(getstr(module.desc, module_name) + '\n\n')

        if module.desc_rest:
            f.write(rst_class('procgraph:desc_rest'))
            f.write(module.desc_rest + '\n\n')

        for block_name in sorted(module.blocks):
            block = module.blocks[block_name]

            f.write(block_anchor(block.name))
            f.write(rst_class('procgraph:block'))
            f.write('Block ``%s``\n' % block.name)
            f.write('-' * 66 + '\n')

            d = getstr(block.desc, '%s:%s' % (module_name, block_name))
            f.write(d + '\n\n')

            if block.desc_rest:
                f.write(block.desc_rest + '\n\n')

            if block.config:
                f.write(rst_class('procgraph:config'))
                f.write('Configuration\n')
                f.write('^' * 60 + '\n\n')
                for c in block.config:
                    d = getstr(c.desc, '%s:%s config %s' %
                                        (module_name, block_name, c.variable))
                    if c.has_default:
                        f.write('- ``%s`` (default: %s): %s\n\n' %
                                (c.variable, c.default, d))
                    else:
                        f.write('- ``%s``: %s\n\n' % (c.variable, d))
                        # TODO: add desc_rest

            if block.input:
                f.write(rst_class('procgraph:input'))
                f.write('Input\n')
                f.write('^' * 60 + '\n\n')
                for i in block.input:
                    d = getstr(i.desc, '%s:%s input %s' %
                                        (module_name, block_name, i.name))

                    if i.type == FIXED:
                        f.write('- ``%s``: %s\n\n' %
                                (i.name, d))
                    elif i.type == VARIABLE:

                        if i.max is None and i.min is None:
                            condition = ""
                        elif i.max is None:
                            condition = ": n >= %d" % (i.min)
                        elif i.min is None:
                            condition = ": n <= %d" % (i.max)
                        else:
                            condition = ": %d <= n <= %d" % (i.min, i.max)
                        f.write('- %s (variable number%s)\n\n'
                                % (d, condition))
                    else:
                        raise Exception(i.type)

            if block.output:
                f.write(rst_class('procgraph:output'))
                f.write('Output\n')
                f.write('^' * 60 + '\n\n')
                for o in block.output:
                    d = getstr(o.desc, '%s:%s output %s' %
                                        (module_name, block_name, o.name))

                    if o.type == FIXED:
                        f.write('- ``%s``: %s\n\n' % (o.name, d))
                    elif o.type == VARIABLE:
                        f.write('- %s (variable number)\n\n' % d)
                    elif o.type == DEFINED_AT_RUNTIME:
                        f.write('- %s (signals are defined at runtime)\n\n'
                                % d)
                    else:
                        raise Exception(o.type)

            url = get_source_ref(block.source, translate)
            f.write(rst_class('procgraph:source'))
            f.write('Implemented in %s. \n\n\n' % url)


def getstr(s, what):
    if s is None:
        print('Missing documentation: %s' % what)
        return "|towrite|"
    else:
        return s


def get_source_ref(source, translation):
    source = os.path.realpath(source)
    for prefix, ref   in translation.items():
        if source.startswith(prefix):
            rest = source[len(prefix):]
            url = ref + '/' + rest
            return '`%s <%s>`_' % (rest, url)
    return source


def rst_class(c):
    return '\n.. rst-class:: %s\n\n' % c


def module_anchor(name):
    return ".. _`module:%s`:\n\n" % name


def block_anchor(name):
    return ".. _`block:%s`:\n\n" % name


def block_reference(name):
    #return ":ref:`block:%s`" % name
    return ":ref:`%s <block:%s>`" % (name, name)


def module_reference(name):
    return ":ref:`module:%s`" % name

"""    
.. list-table:: Frozen Delights!
   :widths: 15 10 30
   :header-rows: 1

   * - Treat
     - Quantity
     - Description
   * - Albatross
     - 2.99
     - On a stick!
   * - Crunchy Frog
     - 1.49
     - If we took the bones out, it wouldn't be
       crunchy, now would it?
   * - Gannet Ripple
     - 1.99
     - On a stick!
"""


def write_rst_table(f, rows, widths=[30, 70]):
    # XXX: does not work with multiline
    f.write('.. list-table::\n')
    f.write('   :widths: %s\n' % " ".join([str(w) for w in widths]))
    f.write('\n')

    for row in rows:
        for i, item in enumerate(row):
            if '\n' in item:
                print('Warning: malformed cell %r.' % item)
            if i == 0:
                f.write('   * - %s\n' % item)
            else:
                f.write('     - %s\n' % item)
    f.write('\n')


