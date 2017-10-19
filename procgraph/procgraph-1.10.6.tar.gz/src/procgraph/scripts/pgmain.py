from ..core.constants import PATH_ENV_VAR
from ..core.exceptions import BadMethodCall, PGException, SemanticError
from ..core.model import Model
from ..core.model_loader import ModelSpec, model_from_string, pg_look_for_models
from ..core.registrar import Library, default_library
from ..core.visualization import error, info
from contracts import contract
from optparse import OptionParser
import os
import sys
import traceback
import yaml


usage_short = \
"""Usage:    
        
    pg [options]  <model>.pg   [param=value  param=value ... ]
    
Type "pg --help" for all the options and a few examples.

"""

usage_long = usage_short + \
"""Examples:

1) Execute a model that does not need parameters:
    
    $ pg  my_model.pg

2) Execute a model, reading the a directory for additional models:

    $ pg -d my_models/  my_model

   (Note that the current directory is not read by default).    
   There is also an environment variable that has the same effect:

    $ export {PATH_ENV_VAR}=my_models

3) Execute a model, but first load a module that might contain additional block
   definitions.

    $ pg -m my_blocks  my_model.pg      """.format(PATH_ENV_VAR=PATH_ENV_VAR)


def main():

    # TODO: use LenientOptionParser
    parser = OptionParser(usage=usage_long)
    parser.disable_interspersed_args()
    additional_modules = []

    def load_module(option, opt_str, value, parser):  # @UnusedVariable
        additional_modules.append(value)

    additional_directories = []

    def add_directory(option, opt_str, value, parser):  # @UnusedVariable
        additional_directories.append(value)

    parser.add_option("-m", dest="module",
                  action="callback", callback=load_module,
                  type="string", help='Loads the specified module.')

    parser.add_option("-d", dest='directory', type="string",
                      action="callback", callback=add_directory,
                      help='Additional directory to search for models.')

    parser.add_option("--debug", action="store_true", default=False,
                      help="Displays debug information on the model.")

    parser.add_option("--trace", action="store_true",
                      default=False, dest="trace",
                      help="If true, try to display raw stack trace in case  "
                           " of error, instead of the usual friendly message.")

    parser.add_option("--stats", action="store_true",
                      default=False, dest="stats",
                      help="Displays execution stats, including CPU usage.")

    parser.add_option("--nocache", action="store_true", default=False,
                      help="Ignores the parsing cache.")

    (options, args) = parser.parse_args()

    # TODO: make an option to display all the known models
    # if options.debug:
    #    print "Configuration: %s" % config
    if not args:
        print(usage_short)
        sys.exit(-1)

    filename = args.pop(0)

    if options.trace:
        look_for = RuntimeError
    else:
        look_for = PGException

    try:
        config = parse_cmdline_args(args)

        pg(filename, config,
           nocache=options.nocache,
           debug=options.debug,
           stats=options.stats,
           additional_directories=additional_directories,
           additional_modules=additional_modules)

        sys.exit(0)

    except look_for as e:
        error(e)
        if not options.trace:
            info('If you run "pg" with the "--trace" option, you can see the '
                 'python details for this error.')
        sys.exit(-2)


def parse_cmdline_args(args):
    ''' Parses the command-line arguments into a configuration dictionary. '''
    config = {}

    def found_pair(key, value_string):
        try:
            value = int(value_string)
        except:
            try:
                value = float(value_string)
            except:
                value = value_string

        # value = parse_value(value_string)
        config[key] = value

    while args:
        arg = args.pop(0)
        if '=' in arg:
            key, value_string = arg.split('=')
            found_pair(key, value_string)
        elif arg.startswith('--'):
            key = arg[2:]
            if not args:
                msg = 'Argument for %r missing.' % key
                raise Exception(msg)
            value_string = args.pop(0)
            found_pair(key, value_string)
        else:
            msg = "I don't know how to interpret %r" % arg
            raise Exception(msg)

    return config

@contract(filename='str',
          stats='bool',
          nocache='bool',
          stats_display_interval='None|int,>0',
          additional_directories='list(str)',
          additional_modules='list(str)',
          config='dict(str:*)',
          returns=Model)
def pg(filename, config,
       debug=False,
       nocache=False,
       stats=False,
       stats_display_interval=100,
       additional_directories=[],
       additional_modules=[]):
    ''' 
        Instantiate and run a model. 
    
        :param filename: either a file or a known model
        
        :param stats_display_interval: how many iterations to display stats.
    '''

    for module in additional_modules:
        info('Importing package %r...' % module)
        __import__(module)

    library = Library(default_library)

    pg_look_for_models(library,
                       ignore_cache=nocache,
                       additional_paths=additional_directories)

    # load standard components
    import procgraph.components  # @UnusedImport

    if library.exists(block_type=filename):
        # XXX w = Where('command line', filename, 0)
        # Check that it is a model, and not a block.
        generator = library.get_generator_for_block_type(filename)
        if not isinstance(generator, ModelSpec):
            # XXX nothing given
            msg = ('The name %r corresponds to a block, not a model. '
                   'You can only use "pg" with models. ' % filename)
            raise SemanticError(msg, None)

        if len(generator.input) > 0:
            inputs = ", ".join([x.name.__repr__()
                                for x in generator.input])
            msg = ('The model %r has %d input(s) (%s). "pg" can only '
                   'execute models without inputs.' % 
                  (filename, len(generator.input), inputs))
            # XXX nothing given
            raise SemanticError(msg, generator.input[0])

        if debug:
            print('Parsed model:\n\n%s' % generator.parsed_model)

        model = library.instance(filename,
                                 name='cmdline',
                                 config=config)

    else:
        # See if it exists
        if not os.path.exists(filename):
            # Maybe try with extension .pg
            filename_pg = "%s.pg" % filename
            if os.path.exists(filename_pg):
                filename = filename_pg
            else:
                # TODO: add where for command line
                msg = 'Unknown model or file %r.' % filename
                raise SemanticError(msg, None)  # XXX

        # Make sure we use absolute pathnames so that we know the exact 
        # directory
        filename = os.path.realpath(filename)
        model_spec = open(filename).read()
        model = model_from_string(model_spec, config=config,
                                  filename=filename, library=library)

    if debug:
        model.summary()
        return

    # This is the main loop; unimpressive?

    count = 0
    try:
        model.init()

        while model.has_more():
            try:
                model.update()            
            except BadMethodCall as e:
                e.blocks.insert(0, model)
                raise e

            if stats and stats_display_interval is not None:
                if count % stats_display_interval == 0:
                    s = model.stats_get_all()
                    y = yaml.dump(s)
                    with open('stats.yaml', 'w') as f:
                        f.write(y)
                    model.print_stats()

                count += 1

        # info('Execution of %s finished quietly.' % model)
        model.finish()

    except KeyboardInterrupt:
        where = traceback.format_exc()
        error('Execution of %s interrupted by user at %s:' % (model, where))
        error('I will attempt clean-up.')
        raise
    except Exception as e:
        error('Execution of %s failed: %s' % (model, e))
        error('I will attempt clean-up.')
        raise
    finally:
        # info('Cleaning up.')    
        model.cleanup()

    return model

