# coding=utf-8

from click import option, Choice


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


def scope_option(required=False):
    def decorator(f):
        return option('--scope', '-sc', type=Choice(['test', 'validation', 'train', 'experiment']), required=required,
                      default='experiment', help='Scope type.')(f)

    return decorator


def graph_type_option(required=False):
    def decorator(f):
        return option('--graphType', '-gt', type=Choice(['line']), required=required,
                      default='line', help='Graph type.')(f)

    return decorator


def graph_id_option(required=False):
    def decorator(f):
        return option('--graphId', '-g', metavar='<str>', required=required,
                      help='The id of the graph. The id is used in order to identify the graph against different '
                           'experiments and through the same experiment.')(f)

    return decorator


def graph_name_option(required=False):
    def decorator(f):
        return option('--graphName', '-gn', metavar='<str>', required=required,
                      help='The display name of the graph ')(f)

    return decorator


def graph_x_option(required=False):
    def decorator(f):
        return option('--graphX', '-gx', metavar='<str>', required=required,
                      help='Array of X axis points')(f)

    return decorator


def graph_y_option(required=False):
    def decorator(f):
        return option('--graphY', '-gy', metavar='<json_string>', required=required,
                      help='Array of Y axis poits')(f)

    return decorator


def graph_x_name_option(required=False):
    def decorator(f):
        return option('--graphXName', '-gxn', metavar='<json_string>', required=required, default='X',
                      help='The display name graphs X axis')(f)

    return decorator


def graph_y_name_option(required=False):
    def decorator(f):
        return option('--graphYName', '-gyn', metavar='<str>', required=required, default='Y',
                      help='The display name of the graph ')(f)

    return decorator


# def graph_data_option(required=False):
#     def decorator(f):
#         return option('--graph', '-g', metavar='<json_string>', required=required,
#                       help='An array of [x, y]  coordinates as jsonified string. The key should be the X '
#                            'axis value and the value the Y axis value. Both key and value should  be '
#                            'Integers or Floats.')(f)

#    return decorator


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
