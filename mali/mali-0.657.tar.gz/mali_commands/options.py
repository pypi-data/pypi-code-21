# coding=utf-8

from click import option


def project_id_option(required=False):
    def decorator(f):
        return option('--projectId', '-p', type=int, metavar='<int>', required=required,
                      help='The project ID to find experiments. Use `mali projects list` to find your project IDs')(f)
    return decorator


def experiment_id_option(required=False):
    def decorator(f):
        return option('--experimentId', '-e', type=int, metavar='<int>', required=required,
                      help='The experiment ID. Use `mali experiments list` to find your experiment IDs')(f)
    return decorator


def metrics_option(required=False):
    def decorator(f):
        return option('--metrics', '-m', metavar='<json_string>', required=required,
                      help='The metrics of the experiment as a jsonified string. The key should be the metric '
                           'name with "ex" prefix e.g. "ex_cost". The value is the metric value in String, Float, '
                           'Integer or Boolean.')(f)
    return decorator


def model_weights_hash_option(required=False):
    def decorator(f):
        return option('--weightsHash', '-wh', metavar='<sha1_hex>', required=required,
                      help="The hexadecimal sha1 hash of the model's weights")(f)

    return decorator
