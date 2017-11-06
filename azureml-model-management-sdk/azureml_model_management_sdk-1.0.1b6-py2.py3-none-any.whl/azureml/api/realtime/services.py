# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import inspect
import os
import json
from azureml.api.schema.schemaUtil import _generate_service_schema, _check_inout_item_schema_version

templates_directory = os.path.join(os.path.dirname(__file__), 'templates')


def _get_args(func):
    args = inspect.getargs(func.__code__)
    all_args = args.args
    if args.varargs is not None:
        all_args.append('*' + args.varargs)
    if hasattr(args, 'varkw') and args.varkw is not None:
        all_args.append('**' + args.varkw)
    if hasattr(args, 'keywords') and args.keywords is not None:
        all_args.append('**' + args.keywords)
    return all_args


def _get_args_defaults(func):
    args = inspect.getargspec(func)
    if args.defaults is not None:
        return dict(zip(args.args[-len(args.defaults):], args.defaults))
    else:
        return dict()


def _validate_run_func_args(run_func, input_schema):
    run_args = _get_args(run_func)
    default_values = _get_args_defaults(run_func)
    if len(run_args) > 0 and input_schema is None:
        raise ValueError("Provided run function has arguments, input schema needs to be provided")
    if input_schema is not None:
        if len(run_args) != len(input_schema):
            raise ValueError(
                "Argument mismatch: Provided run function has {0} arguments while {1} inputs "
                "were previously declared for it".format(len(run_args), len(input_schema)))
        for arg in run_args:
            # temporarily replacing the stars in front of arguments for comparison sake
            if "*" in arg:
                arg = arg.replace("*", "")
            if "**" in arg:
                arg = arg.replace("**", "")
            if arg not in input_schema:
                raise ValueError("Argument mismatch: Provided run function argument {0} is not "
                                "present in input types dictionary which contains: ({1})"
                                .format(arg, ", ".join(input_schema.keys())))
    return run_args, default_values


def generate_schema(run_func, inputs=None, outputs=None, filepath=None):
    """

    :param run_func: function object defining run function for service
    :param inputs: dict mapping str -> azureml.api.schema.sampleDefinition.SampleDefinition
    :param outputs: dict mapping str -> azureml.api.schema.sampleDefinition.SampleDefinition
    :param filepath: str path to file for writing schema file
    :raises IOError if filepath is invalid
    :raises ValueError if input/output are not dict or their values are not
        azureml.api.schema.sampleDefinition.SampleDefinition
    :return: dict mapping str -> dict. Possible keys: "input", "output"
    """
    schema = _generate_service_schema(inputs, outputs)
    _validate_run_func_args(run_func, schema['input'] if 'input' in schema else None)
    if filepath is not None:
        # Try to create the hosting folder if it does not exist
        root_folder = os.path.dirname(filepath)
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)
        with open(filepath, 'w') as schema_file:
            json.dump(schema, schema_file)
    return schema


def generate_main(user_file, schema_file, main_file_name):
    """

    :param user_file: str path to user file with init() and run()
    :param schema_file: str path to user schema file
    :param main_file_name: str full path of file to create
    :return: str filepath to generated file
    """

    # Validate the schema file if specified to ensure compatibility with publishing SDK
    if schema_file and os.path.exists(schema_file):
        _validate_schema_version(schema_file)

    main_template_path = os.path.join(templates_directory, 'main_template.txt')
    with open(main_template_path) as template_file:
        main_src = template_file.read()

    main_src = main_src.replace('<user_script>', user_file)\
        .replace('<schema_file>', schema_file)
    with open(main_file_name, 'w') as main_file:
        main_file.write(main_src)
    return main_file_name


def _validate_schema_version(schema_file):
    with open(schema_file, 'r') as outfile:
        schema_json = json.load(outfile)

    if "input" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["input"][key])
            break
    elif "output" in schema_json:
        for key in schema_json["input"]:
            _check_inout_item_schema_version(schema_json["output"][key])
            break
