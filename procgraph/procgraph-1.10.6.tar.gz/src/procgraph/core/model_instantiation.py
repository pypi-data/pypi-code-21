from copy import deepcopy
import os
import re
import sys

from pyparsing import ParseResults

from .block_config import resolve_config
from .block_meta import VARIABLE, DEFINED_AT_RUNTIME
from .constants import STRICT
from .exceptions import BadMethodCall, PGException, SemanticError, x_not_found, aslist
from .model import Model
from .model_io import ModelInput
from .parsing_elements import (ParsedSignalList, VariableReference,
                               ParsedBlock, ParsedModel, ParsedSignal)
from .registrar import default_library
from .visualization import debug as debug_main, semantic_warning, info


def check_link_compatibility_input(previous_block, previous_link):
    assert isinstance(previous_link, ParsedSignalList)

    num_required = len(previous_link.signals)
    num_found = previous_block.num_output_signals()

    if num_required > num_found:
        msg = ('Required at least %d, found only %d.'
               % (num_required, num_found))
        raise SemanticError(msg, previous_link)
    # XXX, still something not quite right

    # We check that we have good matches for the previous                    
    for i, s in enumerate(previous_link.signals):
        assert isinstance(s, ParsedSignal)

        if s.block_name is not None:
            msg = ('Could not give the block a name when the connection is '
                   'between two blocks.')
            raise SemanticError(msg, s)

        if s.local_input is None:
            s.local_input = i

        if not previous_block.is_valid_output_name(s.local_input):
            msg = ('Could not find output name "%s"(%s) in %s' % 
                    (s.local_input, type(s.local_input), previous_block))
            raise SemanticError(msg, s)

        s.local_input = previous_block.canonicalize_output(s.local_input)


def check_link_compatibility_output(block, previous_link):
    assert isinstance(previous_link, ParsedSignalList)

    # we check that we have good matches for the next    
    for i, s in enumerate(previous_link.signals):
        assert isinstance(s, ParsedSignal)

        if s.local_output is  None:
            s.local_output = i

        if not block.is_valid_input_name(s.local_output):
            msg = 'Could not find input name %r in %s' % (s.local_output,
                                                          block)
            raise SemanticError(msg, s)

        s.local_output = block.canonicalize_input(s.local_output)


def expand_references_in_string(s, function):
    ''' Expands references of the kind ${var} in the string s.
        ``function``(var) translates from var -> value '''
    while True:
        m = re.match('(.*)\$\{(\w+)\}(.*)', s)
        if not m:
            return s
        before = m.group(1)
        var = m.group(2)
        after = m.group(3)
        sub = function(var)
        s = before + str(sub) + after


def create_from_parsing_results(parsed_model, name=None, config={},
                                library=None):
    assert isinstance(parsed_model, ParsedModel)

    def debug(s):
        if False:
            debug_main('Creating %s:%s | %s' % (name, parsed_model.name, s))

    # debug_main('config: %s' % config)

    if library is None:
        library = default_library

    model = Model(name=name, model_name=parsed_model.name)
    model.define_input_signals_new([x.name for x in parsed_model.input])
    model.define_output_signals_new([x.name for x in parsed_model.output])

    # first we divide the config in normal, and recursive config
    normal_config = {}
    recursive_config = {}
    for key, value in config.items():
        if '.' in key:
            recursive_config[key] = value
        else:
            normal_config[key] = value

    # We mix the normal config with the defaults
    # FIXME: None -> no where information
    #        In fact, parsed_model is the one we are instancing, NOT 
    #        where the error is made.
    resolved = resolve_config(parsed_model.config, normal_config, None)
    # we give none so that it can be filled in by the caller

    # Remember config statement
    key2element = {}
    for c in parsed_model.config:
        key2element[c.variable] = c

    # We collect here all the properties, to use in initialization.
    all_config = []  # tuple (key, value, parsing_element)

    # 1. We put the resolved configuration 
    for key, value in resolved.items():
        all_config.append((key, value, key2element.get(key, None)))

    # 2. We also put the recursive conf
    for key, value in recursive_config.items():
        all_config.append((key, value, key2element.get(key, None)))

    # 3. We process the assignments
    for assignment in parsed_model.assignments:
        # We make sure we are not overwriting configuration    
        if assignment.key in resolved:
            msg = ('Assignment to %r overwrites a config variable. '
                   'Perhaps you want to change the default instead?' % 
                    assignment.key)
            raise SemanticError(msg, assignment)

        all_config.append((assignment.key, assignment.value, assignment))

    # Next, define the properties hash, and populate it intelligentily
    # from the tuples in all_config.
    properties = {}
    # We keep track of what properties we use
    used_properties = set()  # of strings
    # This instead collects the block_properties
    block_properties = {}  # {str: {str: *}}

    def expand_value(value, element=None):
        ''' Function that looks for VariableReference and does the 
            substitution. 
        '''
        if isinstance(value, VariableReference):
            variable = value.variable
            if variable in os.environ:
                return os.environ[variable]
            if not variable in properties:
                msg = x_not_found('variable', variable, properties)
                raise SemanticError(msg, element)
            used_properties.add(variable)
            return expand_value(properties[variable], element=element)

        elif isinstance(value, str):
            return expand_references_in_string(value,
                    lambda s: expand_value(VariableReference(s),
                                           element=element))

        elif isinstance(value, dict):
            h = {}
            for key in value:
                h[key] = expand_value(value[key], element=element)
            return h

        # XXX: we shouldn't have here ParseResults
        elif isinstance(value, list) or isinstance(value, ParseResults):
            return [expand_value(s, element) for s in value]
        else:
            return value

    # We keep track of the blocks we reference so we can check it later
    referenced_blocks = []  # list of tuples (block name, parsed_element)
    for key, value, element in all_config:
        # if it is of the form  object.property = value
        if '.' in key:
            # TODO: put this in syntax
            object_, property_ = key.split('.', 1)
            if not object_ in block_properties:
                block_properties[object_] = {}
            # else:    
                # # XXX probably should be better
                # if not isinstance(properties[object], dict):
                #     msg = ('Error while processing "%s=%s": I already know'
                #            ' the key.' % (key, value)) 
                #     raise SemanticError(msg, element)
            referenced_blocks.append((object_, element))
            block_properties[object_][property_] = value  # XX or expand?
        else:
            properties[key] = expand_value(value, element=element)

    # Make sure we can access python modules in the same directory as the
    # filename; we add the directory to the sys.path

    old_sys_path = list(sys.path)
    if parsed_model.where.filename is not None:
        dirname = os.path.dirname(parsed_model.where.filename)
        if dirname is not None:
            sys.path.append(dirname)

    try:
        for x in parsed_model.imports:
            package = x.package
            if not package in sys.modules:
                info("Importing package %r..." % package)

                try:
                    __import__(package)
                except Exception as e:
                    msg = 'Could not import package %r: %s' % (package, e)
                    raise SemanticError(msg, x)
    finally:
        sys.path = old_sys_path

    # Then we instantiate all the blocks

    # Iterate over connections 
    for connection in parsed_model.connections:
        previous_block = None
        previous_link = None

        # print "Looking at connection %s" % connection.elements
        for i, element in enumerate(connection.elements):
            if isinstance(element, ParsedSignalList):
                # We make a copy, because later we modify (for convenience)
                # its fields, in the check_compatibility_* functions
                # For example, we assign names to input/output.
                element = deepcopy(element)

                # if this is not the last one, just save it, it will be
                # processed together with the next block
                if i != len(connection.elements) - 1:
                    previous_link = element
                else:
                    assert previous_block is not None
                    # This is the last one, we should process it with the 
                    # previous_block
                    previous_link = element
                    check_link_compatibility_input(previous_block,
                                                   previous_link)

                    for s in (previous_link.signals):
                        # We cannot have a local output
                        if s.local_output is not None:
                            msg = ('Terminator connection %s cannot have a '
                                   'local output' % s)
                            raise SemanticError(msg, s)

                        if s.name in model.public_signal_names():
                            msg = ('Public signal name %r already taken.' % 
                                   s.name)
                            raise SemanticError(msg, s)

                        model.connect(block1=previous_block,
                                      block1_signal=s.local_input,
                                      block2=None, block2_signal=None,
                                      public_name=s.name)

            if isinstance(element, ParsedBlock):

                # before processing this block, let's create a phantom
                # signal list
                if previous_block is not None and previous_link is None:
                    previous_link = fill_anonymous_link(previous_block)

                # also we can check right now a common error
                if (previous_block is not None and
                    previous_block.num_output_signals() == 0):
                    msg = ('This block does not define outputs; yet it is not '
                           'the last in the sequence.')
                    raise SemanticError(msg, previous_block)

                block_type = expand_value(element.operation, element=element)

                # give a name if anonymous
                if element.name is None:
                    # give it, if possible the name of its type
                    if not  block_type in model.name2block:
                        element.name = block_type
                    else:
                        i = 2
                        while True:
                            element.name = "%s%d" % (block_type, i)
                            i += 1
                            if not element.name in model.name2block:
                                break

                # update the configuration if given
                block_config = {}
                block_config.update(element.config)
                if element.name in block_properties:
                    more_config_for_block = block_properties[element.name]
                    # For example:
                    #   wait = 10       ->  { wait: 10 }
                    #   wait.time  = 3  ->  { wait: {time: 3} }
                    block_config.update(more_config_for_block)

                for key, value in list(block_config.items()):
                    block_config[key] = expand_value(value, element=element)

                if not library.exists(block_type):
                    msg = x_not_found('block type', block_type,
                                      library.get_known_blocks())
                    raise SemanticError(msg, element)

                debug('instancing %s:%s config: %s' % 
                      (element.name, element.operation, block_config))

                try:
                    block = library.instance(block_type=block_type,
                                             name=element.name,
                                             config=block_config)
                    block.where = element.where
                except SemanticError as e:
                    # For config (see FIXME)
                    if e.element is None:
                        e.element = element
                    raise

                # now define input and output
                generator = library.get_generator_for_block_type(block_type)

                define_input_signals(generator.input, block,
                                     previous_link, previous_block, model)
                
                define_output_signals(generator.output, block)
                
                # at this point input/output should be defined
                assert block.are_input_signals_defined()
                assert block.are_output_signals_defined()

                block = model.add_block(name=element.name, block=block)

                previous_link = None
                previous_block = block
            # end if 

    # Check if any of the config referenced a nonexistent block
    # (before we warn it as just an unused variable in the next paragraph) 
    for block_name, element in referenced_blocks:
        if not block_name in model.name2block:
            msg = x_not_found('block', block_name, model.name2block)
            raise SemanticError(msg, element)

    unused_properties = set(properties.keys()).difference(used_properties)
    if unused_properties:
        msg = ('Unused properties: %s. (Used: %s.)' % 
               (aslist(unused_properties), aslist(used_properties)))
        if STRICT:
            raise SemanticError(msg, element=parsed_model)
        else:
            semantic_warning(msg, parsed_model)

    # One last thing: define dummy blocks for inputs without |input| blocks
    for signal in model.get_input_signals_names():
        if not signal in model.model_input_ports:
            block_type = 'input'
            block_name = 'dummy_input_%s' % signal
            block_config = {'name': signal}
            dummy_block = library.instance(block_type, block_name,
                                           block_config)
            generator = library.get_generator_for_block_type(block_type)
            define_input_signals(generator.input, dummy_block,
                                 None, None, model)
            define_output_signals(generator.output, dummy_block)
            model.add_block(block_name, dummy_block)
            # TODO: warn

    # TODO: warn if no output block was defined

    return model


def define_output_signals(output, block):
    # this is a special case, in which the signal name
    # is not known before parsing the configuration
    if isinstance(block, ModelInput):
        block.define_output_signals_new([block.config.name])
        return

    output_is_defined_at_runtime = (len(output) == 1 and
                                    output[0].type == DEFINED_AT_RUNTIME)

    if output_is_defined_at_runtime:
        try:
            names = block.get_output_signals()
        except PGException:
            raise
        except Exception as user_exception:
            raise BadMethodCall('get_output_signals', block, user_exception)
        
        if len(set(names)) != len(names):
            msg = ('Repeated signal names in %s.' % names)
            raise SemanticError(msg, block)

        block.define_output_signals_new(names)
        return

    output_is_variable = len(output) == 1 and output[0].type == VARIABLE

    if output_is_variable:
        # define output signals with the same name as the input signals
        
        try:
            names = block.get_input_signals_names()
        except PGException:
            raise
        except Exception as user_exception:
            raise BadMethodCall('get_input_signals_names', block, user_exception)

# TODO: maybe add a suffix someday
        # names = [name + suffix for name in names]

        block.define_output_signals_new(names)

    else:
        # simply define the output signals
        names = [x.name for x in output]
        block.define_output_signals_new(names)


def define_input_signals(input, block,  # @ReservedAssignment
                         previous_link, previous_block, model):
    # there are two cases: either we define named signals,
    # or we have a generic number of signals
    input_is_arbitrary = len(input) == 1 and input[0].type == VARIABLE

    if input_is_arbitrary:
        # in this case, we have a minimum and maximum 
        # number of signals that we can accept
        min_expected = input[0].min
        max_expected = input[0].max

        if not min_expected:
            min_expected = 0
        if not max_expected:
            max_expected = 10000

        # if we don't have a previous block, then
        # we just define no input signals
        # (if we expect something, then we throw an error)
        if previous_link is None:
            if min_expected > 0:
                msg = ('I expected at least %d input signal(s) but the block '
                       'is not connected to anything.' % min_expected)
                raise SemanticError(msg, block)
            else:
                # no inputs for this block
                block.define_input_signals_new([])
        else:
            # We have a previous link, we check that the number
            # of signals is compatible.
            num_given = len(previous_link.signals)
            ok = (min_expected <= num_given <= max_expected)
            if not ok:
                msg = ('I expected between %d and %d input signals, and I got '
                       '%d.' % (min_expected, max_expected, num_given))
                raise SemanticError(msg, block)
            # Define input signals given the names
            names = []
            for i in range(num_given):
                # --> [local_input] name [local_output] -->    
                if previous_link.signals[i].local_output is not None:
                    name = previous_link.signals[i].local_output
                elif previous_link.signals[i].name is not None:
                    name = previous_link.signals[i].name
                elif previous_link.signals[i].local_input is not None:
                    name = previous_link.signals[i].local_input
                else:
                    assert False

                # just in case the thing is repeated
                # TODO: warn?  if name in names: ...
                name = find_unique_name(name, names)                
                names.append(name)
            block.define_input_signals_new(names)
    else:  # the input is not arbitrary
        # define right away the names, it does not depend 
        # on anything else
        names = [x.name for x in input]
        block.define_input_signals_new(names)

        # now check we were given the right input
        num_expected = len(names)

        # if we expect something and it is not given,
        # raise an exception
        if previous_link is None:
            if (num_expected > 0):
                msg = ('The block expected at least %d input signals'
                      ' but none were given.' % num_expected)
                raise SemanticError(msg, block)
        else:
            # we have a previous block, the number of signals
            # should match
            num_given = len(previous_link.signals)

            if num_expected != num_given:
                msg = ('The block expected %d input signals, got %d.' % 
                      (num_expected, num_given))
                raise SemanticError(msg, block)

    # print "Defined block %s = %s " % (element.name , block)
    if previous_link is not None:
        check_link_compatibility_output(block, previous_link)

        if previous_block is not None:
            # normal connection between two blocks with named signals

            # Here we have to make sure that, if the blocks defined
            #  signals input/outputs, then the signals given by the user
            #  are coherent.

            check_link_compatibility_input(previous_block, previous_link)

            # Finally we create the connection
            for s in (previous_link.signals):
                if s.name is None:
                    s.name = "input_%s_for_%s" % (s.local_output, block)
                s_name = find_unique_name(s.name, model.public_signal_names())
                model.connect(previous_block, s.local_input,
                                     block, s.local_output, s_name)
        else:
            # this is the first block with previous signals
            # this time we need to be careful, because
            # links can refer to other parts
            for s in previous_link.signals:
                # Cannot use local_input here
                if s.local_input is not None:
                    msg = 'Link %s uses local input without antecedent. ' % s
                    raise SemanticError(msg, s)
                # Check if it is using an explicit block name
                if s.block_name is not None:
                    if not s.block_name in model.name2block:
                        msg = ('Link %s refers to an unknown block %r.'
                               'Valid blocks: %s.' % 
                               (s, s.block_name, aslist(model.name2block)))
                        raise SemanticError(msg, s)

                    input_block = model.name2block[s.block_name]
                    if not input_block.is_valid_output_name(s.name):
                        # TODO: make other friendly messages like this
                        msg = ("This link refers to an unknown output %r. " % 
                               s.name)
                        msg += ("The known outputs are: %s." % 
                                input_block.get_output_signals_names())
                        # msg += "  link: %s \n" % s
                        # msg += " block: %s \n" % input_block  
                        raise SemanticError(msg, element=s)
                    s.local_input = input_block.canonicalize_output(s.name)
                else:
                    if not s.name in model.name2block_connection:
                        # throw out the autogenerated (XXX: make a flag)
                        valid = [x for x in model.name2block_connection
                                 if not ':' in x]
                        msg = ('This link refers to an unknown signal %r.\n'
                               'Valid signals: %s.' % (s.name, aslist(valid)))
                        raise SemanticError(msg, element=s)
                    defined_signal = model.name2block_connection[s.name]
                    input_block = defined_signal.block1
                    s.local_input = defined_signal.block1_signal

                # make up a unique name   
                name = "%s:%s:%s" % (input_block.name, s.local_output, block.name)
                name = find_unique_name(name, model.public_signal_names())

                model.connect(input_block, s.local_input,
                              block, s.local_output, name)

def find_unique_name(prefix, existing):
    name = prefix
    count = 1
    while name in existing:
        count += 1
        name = '%s%d' % (prefix, count)
    return name
        
         
def fill_anonymous_link(previous_block):
    # --> [local_input] name [local_output] -->
    names = previous_block.get_output_signals_names()
    signals = []
    for name in names:
        signal = ParsedSignal(name=None, block_name=None,
                              local_input=name,
                              local_output=None)
        signals.append(signal)
    return ParsedSignalList(signals)
