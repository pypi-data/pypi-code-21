import inspect
import os
import datetime
from azureml.api.schema import schemaUtil

BATCH_DRIVER_FILE = 'service_driver.py'


def prepare_publish_setup(run_func, inputs, outputs, parameters, dependencies):
    """
    Provides initial setup for the SDK handling of prepare and publish commands
    :param run_func: User's run function that they want to operationalize
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param dependencies: A list of any dependencies that the service requires 
    :return: Dictionary of parameter name to default value of the user's run function
    """

    schema_file = "batch_schema_{0}.json".format(datetime.datetime.today().strftime('%Y%m%d%H%M%S'))
    dependencies.append(schema_file)

    run_func_defaults = parse_func_defaults(run_func)
    generate_schema_file(inputs, outputs, parameters, schema_file)
    generate_driver_file(run_func, inputs, outputs, parameters, run_func_defaults, schema_file)

    return run_func_defaults


def generate_schema_file(inputs, outputs, parameters, schema_file):
    """
    Generate the schema file for the service
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param schema_file: File to write the schema to
    :return: None
    """
    schema_inputs = {}
    run_func_args = {}

    for name, input_info in inputs.items():
        if type(input_info) is tuple:
            schema_inputs[name] = input_info[0]
        else:
            schema_inputs[name] = input_info

    run_func_args.update(schema_inputs)
    run_func_args.update(outputs)
    run_func_args.update(parameters)

    schemaUtil.save_service_schema(schema_file, run_func_args)


def generate_driver_file(run_func, inputs, outputs, parameters, run_func_defaults, schema_file):
    """
    Generate the driver file that will be used for the batch service
    :param run_func: User's 'run' function that they want to operationalize
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param run_func_defaults: A dictionary of parameter name to default value of the user's run function
    :param schema_file: The file containing the schema for the service
    :return: None
    """
    frame = inspect.currentframe()

    try:
        frames = inspect.getouterframes(frame)
        sdk_frame = frames[1]

        run_code = inspect.getsourcelines(run_func)

        try:  # Python 3+
            sdk_location = os.path.dirname(os.path.dirname(sdk_frame.filename))
        except AttributeError:  # Python 2.7
            sdk_location = os.path.dirname(os.path.dirname(sdk_frame[1]))

        run_func_name = run_func.__name__
        main_function = generate_main(run_func_name, inputs, outputs, parameters, run_func_defaults, schema_file)

        with open(BATCH_DRIVER_FILE, 'w') as service_result_file:
            # These lines are a standin until the sdk is native in the base image
            service_result_file.write('import sys\n')
            service_result_file.write('if not "{0}" in sys.path:\n\tsys.path.append("{0}")\n'.format(sdk_location))
            service_result_file.write('from batch import batch_handler\n')
            service_result_file.write('from schema import schemaUtil\n\n')
            for line in run_code[0]:
                service_result_file.write(line)
            service_result_file.write('\n\nif __name__ == "__main__":\n')
            for line in main_function:
                service_result_file.write('\t{}\n'.format(line))
    except IOError as e:
        print(e)
        return
    finally:
        del frame


def parse_func_defaults(run_func):
    """
    Generate a dictionary pairing function parameters to their specified defaults
    :param run_func: The function to extract defaults from
    :return: A dictionary of parameter name to corresponding default
    """
    try:  # Python 3+
        argspec = inspect.getfullargspec(run_func)
    except AttributeError:  # Python 2.7
        argspec = inspect.getargspec(run_func)

    if argspec.defaults is not None:
        return dict(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
    else:
        return dict()


def generate_main(run_func_name, inputs, outputs, parameters, run_func_defaults, schema_file):
    """
    Generate the 'main' function that will be in the driver file
    :param run_func_name: The name of the user's 'run' function
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param run_func_defaults: A dictionary of parameter name to default value of the user's run function
    :param schema_file: The file containing the schema for the service
    :return: 
    """
    main_function = _add_argument_parser_to_main(inputs, outputs, parameters)
    main_function.extend(_add_schema_handling_to_main(inputs, run_func_defaults, schema_file))
    main_function.append('{}(**arguments)'.format(run_func_name))

    return main_function


def _add_argument_parser_to_main(inputs, outputs, parameters):
    """
    Function to add argument parsing to the generated main function
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :return: A list of strings to include in the main function
    """
    main_function = ['import argparse', 'parser = argparse.ArgumentParser()']

    args = {}
    args.update(inputs)
    args.update(outputs)

    for name in args:
        main_function.append('parser.add_argument("--{}", dest="{}")'.format(name.replace('_', '-'), name))
    for name, param_type in parameters.items():
        parser_type = type(param_type.schema.swagger['example']).__name__
        main_function.append('parser.add_argument("--{}", dest="{}", type={})'.format(name.replace('_', '-'), name, parser_type))

    main_function.append('parsed_args = vars(parser.parse_args())')

    return main_function


def _add_schema_handling_to_main(inputs, run_func_defaults, schema_file):
    """
    Function to add schema handling to the generated main function
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param run_func_defaults: A dictionary of parameter name to default value of the user's run function
    :param schema_file: The file containing the schema for the service
    :return: A list of strings to include in the main function
    """
    service_inputs = {}
    main_function = []

    for name, sample in inputs.items():
        if type(sample) is tuple:
            service_inputs[name] = sample[1]
        else:
            service_inputs[name] = False

    main_function.append('service_schema = schemaUtil.load_service_schema("{}")'.format(schema_file))
    main_function.append('aml_service_inputs = {}'.format(service_inputs))
    main_function.append('defaults = {}'.format(run_func_defaults))
    main_function.append('arguments = batch_handler._batch_parse_service_input(parsed_args, service_schema, aml_service_inputs, defaults)')

    return main_function


def generate_create_command(service_name, inputs, outputs, parameters, dependencies, run_func_defaults):
    """
    Generate the command that the user will need to publish a service generated with 'prepare' through the CLI
    :param service_name: The name of the service the user wants to publish
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param dependencies: A list of any dependencies that the service requires 
    :param run_func_defaults: A dictionary of parameter name to default value of the user's run function
    :return: A string that is the 'create' command that a user needs to publish the specified service through the CLI
    """
    command = 'az ml service create batch -f {} -n {} '.format(BATCH_DRIVER_FILE, service_name)

    args = []
    args.extend([('in', arg) for arg in inputs])
    args.extend([('out', arg) for arg in outputs])
    args.extend([('param', arg) for arg in parameters])

    for flag, arg in args:
        command += '--{}=--{}'.format(flag, arg.replace('_', '-'))
        if arg in run_func_defaults:
            command += ':{} '.format(run_func_defaults[arg])
        else:
            command += ' '

    for dependency in dependencies:
        command += '-d {} '.format(dependency)

    return command.strip()
