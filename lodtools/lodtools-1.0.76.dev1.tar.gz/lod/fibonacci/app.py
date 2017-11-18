import os

from lod import lod


# A TOY EXAMPLE: Fibonacci
# This file exists to demonstrate how to use the lod library.

# this program implements the fibonacci sequence.
# It takes up to two files as input, which should contain a number each.
# It creates a new file and writes the next number in the sequence to it.
# Then, this program asks the Execution Environment to call this program again on the newly generated file and the last previous one.

##############################################################################################################
# The manager: wrapping your code around this enables logging of log messages and exceptions/errors
# (the parameters here are shown with their default values)
##############################################################################################################

with lod.manager(suppress_exceptions_after_logging_them=False, redirect_stdout_to_log=True) as col:

    # these log statements are written to a file that is available via the lod website for inspection,
    # but that is not available to other programs running in lod.
    # they are therefore useful for debugging and gathering information about the program's performance.
    col.log("example log message")

    # if the parameter redirect_stdout_to_log in the manager is set to True, print() and other functions that use stdout get redirected to the logger
    print("test log statement from console 123")

    ##############################################################################################################
    # input: reading files and understanding the context
    ##############################################################################################################

    # get an integer indicating what step in the current execution environment this is

    step = lod.get_current_step()

    # get the identifier of this currently running program

    this_program_id, this_program_name, this_program_version = lod.get_own_program_details()

    # get a dictionary of input arguments that were given to this program

    inputs = lod.get_inputs()

    if len(inputs) > 2:
        # if something goes wrong and an exception is thrown, the error and its stacktrace are automatically written to an error log file.
        # just like the log file, this file can be inspected on the website, but is not available to other programs running in lod.
        raise IOError("this program takes up to two files as input, which must contain a number each")
    input_numbers = {}
    identifier_of_last_input_object = None

    for argument_name, input_object in inputs.items():

        # investigate them more closely

        input_file = input_object.file
        input_object_identifier = input_object.identifier # this identifier is what is used by Tags to reference objects
        if argument_name == 'last':
            identifier_of_last_input_object = input_object_identifier

        # use the input file to see what this program has received as its input

        with open(input_file, 'r') as f:
            inpt = f.read()
            num = int(inpt)
            input_numbers[argument_name] = num

    # find out why this program was triggered

    event_of_this_execution = lod.get_event_of_this_execution()
    trigger_of_this_execution = event_of_this_execution.trigger
    triggering_step_of_this_execution = event_of_this_execution.triggering_step

    # get an ObjectManager, which contains a history of everything that has happened so far

    object_manager = lod.get_object_manager()

    # get a list of tags that have been made at earlier stages of the execution

    tags = object_manager.get_all_objects(object_type='tag')

    # look at the tags more specifically

    for example_tag in tags:
        sym_name = example_tag.symbol_name
        sym_identifier = example_tag.symbol_identifier
        for obj_identifier in example_tag.argument_identifiers: # this can refer to one of a number of things, but usually it's an object or another tag.
            pass

    ##############################################################################################################

    # at this point, all inputs have been read and the context of this program's execution has been understood.
    # the actual operations of your program should go here.
    # for this simple example program, we implement the logic of the Fibonacci sequence.

    if len(input_numbers) != 2:
        next_number = 1
    else:
        next_number = input_numbers['last'] + input_numbers['second_to_last']

    ##############################################################################################################

    # create an output, to make the results of this program available to other programs and to the Execution Environment.
    # you can create multiple outputs, and they will be added in the order in which they were created with this function.

    output_file_name = "the next Fibonacci number"
    output_object = lod.add_output_file(output_file_name)
    output_file = output_object.file
    output_object_identifier = output_object.identifier # this identifier is what is used by Tags to reference objects

    # write to the output file whatever you want to communicate to the outside
    # in this example, that's just the number we read incremented by one

    with open(output_file, 'w') as f:
        f.write(str(next_number))

    # create a new global tag using a preexisting lod Symbol (global Tags are just Tags without arguments).
    # the only required argument here is the name of the symbol, which is given in create_tag().

    lod.create_tag("continue-executing-fibonacci-sequence").weight(10).comment('this is a comment')

    # create a new tag to mark a relation between one of the input files and the new output file.
    # this can be used to tell other programs about the relationship between these files.
    # (you can use either the identifier of an object, or the object itself as an argument)
    # TODO: the above description is no longer accurate since I changed what Fibonacci does for a testcase

    lod.create_tag("last-in-fibonacci-sequence").arguments([output_object])
    if identifier_of_last_input_object is not None:
        lod.create_tag("second-to-last-in-fibonacci-sequence").arguments([identifier_of_last_input_object])

    # request the Execution Environment to display a message to the user
    # Note that this function works differently depending on the type of the request.
    # and that requests are processed in the order in which they are received.
    lod.request_to_display_message().add_text("generated next Fibonacci number: %d" % next_number).add_text(
        'second part, first line\nsecond part, second line')

    # create a hidden message that is only visible in development-mode
    lod.request_to_display_message().add_text("this is a hidden message that's only visible in development mode.").is_only_for_developers()

    # request the Execution Environment to call this program again.
    # using the file we just created and the second of the current input arguments as its new inputs.
    # (if we don't do this, the Execution Environment will use all existing Tags in this Execution Environment
    # and all Execution Rules in the database of the server to determine what to do next)
    # the request_program_execution function expects a program as its first argument, and files to use as parameters as the rest.
    # The program may be identified as a String displaying the name of the program (in which case the latest version is picked),
    # as a String of <name>#<version> (which identifies the version directly),
    # or as an integer that is the program's ID (which is unambiguous and includes the version)
    # The arguments may be identified either as FileObjects or as the Identifiers of FileObjects

    #if identifier_of_last_input_object is None:
    #    lod.request_program_execution(this_program_id, last=output_object_identifier)
    #else:
    #    lod.request_program_execution(this_program_id, second_to_last=identifier_of_last_input_object, last=output_object)

    # if this is the first time this program is called
    # (check this by looking at the number of its arguments, create a repeating Option to run keep executing it)
    if len(inputs) == 0:
        trigger_rule = {
            "arguments" : [
                {
                    "name" : "last",
                    "optional" : False,
                    "search" : "last_match",
                    "filter" : {
                        "type" : "tag",
                        "symbol" : "last-in-fibonacci-sequence",
                    }
                },
                {
                    "name" : "second_to_last",
                    "optional" : True,
                    "search" : "last_match",
                    "filter" : {
                        "type" : "tag",
                        "symbol" : "second-to-last-in-fibonacci-sequence",
                    }
                },
            ]
        }
        display = {
            'type' : 'error',
        }
        actions = [
            {
                "type" : "conditional",
                "condition" : {
                    "type" : "reference_exists",
                    "reference" : "second_to_last"
                },
                "then_actions" : [{
                    "type" : "execute_program",
                    "program" : "fibonaccilocal",
                    "arguments" : {
                        "second_to_last" : {
                            "nullable" : True,
                            "of" : {
                                "reference" : "second_to_last",
                                "nullable" : True,
                            },
                            "index" : 0,
                        },
                        "last" : {
                            "of" : {
                                "reference" : "last"
                            },
                            "index" : 0,
                        },
                    }
                }],
                "else_actions" : [{
                    "type" : "execute_program",
                    "program" : "fibonaccilocal",
                    "arguments" : {
                        "last" : {
                            "of" : {
                                "reference" : "last"
                            },
                            "index" : 0,
                        },
                    }
                }],
            }
        ]
        option = lod.create_option(trigger_rule, display, actions, description=None)
        lod.create_tag('!set_option_weight').arguments([option]).weight(1.0)

    # This function is called automatically when the manager closes, but it is possible to call it earlier, too,
    # if you are unsure if the program might time out later, so that you can at least output some preliminary results.
    # (calling it here would be unnecessary, so this is only mentioned for later reference)
    
    #lod.finalize_output()







