import json
# from azure.cli.command_modules.ml.service import batch
from ._batch_sdk_utilities import prepare_publish_setup
from ._batch_sdk_utilities import generate_create_command
from azureml.api.schema import schemaUtil


def _batch_parse_service_input(parsed_args, service_schema, aml_service_inputs, defaults):
    """
    Call to this method is injected into the user driver program. Parses provided input files
    into the desired objects and validates all provided inputs against previously defined schema.
    :param parsed_args: The parsed command line arguments
    :param service_schema: Schemafile generated at prepare/publish time
    :param aml_service_inputs: A dictionary of name to bool defining the input file names and if they have a header
    :param defaults: Any defaults that the user's run function has
    :return: A dictionary of argument name to parsed argument value
    """

    args = {}
    non_input_args = {}
    input_schema = service_schema.input

    for arg, value in parsed_args.items():
        if arg not in aml_service_inputs:
            non_input_args[arg] = value
        else:
            args[arg] = schemaUtil.parse_batch_input(value, input_schema[arg], aml_service_inputs[arg])

    non_input_args = schemaUtil.parse_service_input(json.dumps(non_input_args), input_schema)

    args.update(non_input_args)

    return args


def prepare(run_func, inputs, outputs, parameters, dependencies, service_name):
    """
    Used to prepare the driver file to be used for a Batch webservice.
    :param run_func: The function to operationalize
    :param inputs: A dictionary for any input files that the service expects. The dictionary is name to tuple of 
    SampleDefinition, bool
    :param outputs: A dictionary for any output files that the service will produce. The dictionary is name to
    SampleDefinition
    :param parameters: A dictionary for any parameters that the service expects. The dictionary is name to
    SampleDefinition
    :param dependencies: A list of any dependencies that the service requires 
    :param service_name: The name of the service to create
    :return: None
    """

    run_func_defaults = prepare_publish_setup(run_func, inputs, outputs, parameters, dependencies)

    print(generate_create_command(service_name, inputs, outputs, parameters, dependencies, run_func_defaults))


# def publish(run_func, inputs, outputs, parameters, dependencies, service_name, service_title='a_title', verb=False):
#     default_dict = prepare_publish_setup(run_func, inputs, outputs, parameters, dependencies)
#
#     args = []
#     publish_inputs = []
#     publish_outputs = []
#     publish_parameters = []
#     publish_dependencies = []
#
#     args.extend([(publish_inputs, arg) for arg in inputs])
#     args.extend([(publish_outputs, arg) for arg in outputs])
#     args.extend([(publish_parameters, arg) for arg in parameters])
#
#     for arg_list, arg in args:
#         if arg in default_dict:
#             arg_list.append('--{}:{}'.format(arg.replace('_', '-'), default_dict[arg]))
#         else:
#             arg_list.append('--{}'.format(arg.replace('_', '-')))
#
#     for dependency in dependencies:
#         publish_dependencies.append(dependency)
#
#     batch.batch_service_create(driver_file=BATCH_DRIVER_FILE,
#                                service_name=service_name,
#                                title=service_title,
#                                verb=verb,
#                                inputs=publish_inputs,
#                                outputs=publish_outputs,
#                                parameters=publish_parameters,
#                                dependencies=publish_dependencies)
#
#
# def run(service_name, inputs, outputs, parameters, job_name=None, wait=False, verb=False):
#     batch.batch_service_run(service_name=service_name,
#                             inputs=inputs,
#                             outputs=outputs,
#                             parameters=parameters,
#                             job_name=job_name,
#                             wait_for_completion=wait,
#                             verb=verb)
#
#
# def list():
#     batch.batch_service_list()
#
#
# def view(service_name, verb=False):
#     batch.batch_service_view(service_name, verb)
#
#
# def delete(service_name, verb=False):
#     batch.batch_service_delete(service_name, verb)
#
#
# def list_jobs(service_name):
#     batch.batch_list_jobs(service_name)
#
#
# def view_job(service_name, job_name, verb=False):
#     batch.batch_view_job(service_name, job_name, verb)
#
#
# def cancel_job(service_name, job_name, verb=False):
#     batch.batch_cancel_job(service_name, job_name, verb)
