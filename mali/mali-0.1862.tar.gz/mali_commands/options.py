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


def chart_scope_option(required=False):
    def decorator(f):
        return option('--chartScope', '-cs', type=Choice(['test', 'validation', 'train']), required=required,
                      default='test', help='Scope type.')(f)

    return decorator


def chart_type_option(required=False):
    def decorator(f):
        return option('--chartType', '-ct', type=Choice(['line']), required=required,
                      default='line', help='Graph type.')(f)

    return decorator


def chart_name_option(required=False):
    def decorator(f):
        return option('--chartName', '-c', metavar='<str>', required=required,
                      help='The name of the chart. The name is used in order to identify the chart against different '
                           'experiments and through the same experiment.')(f)

    return decorator


def chart_x_option(required=False):
    def decorator(f):
        return option('--chartX', '-cx', metavar='<json_string>', required=required,
                      help='Array of m data points (X axis), Can be Strings, Integers or Floats.')(f)

    return decorator


def chart_y_option(required=False):
    def decorator(f):
        return option('--chartY', '-cy', metavar='<json_string>', required=required,
                      help='Array/Matrix of m data values. Can be either array m of Integers/Floats or a matrix (m arrays having n Ints/Floats each),  a full matrix describing the values of every chart in every data point')(f)

    return decorator


def chart_y_name_option(required=False):
    def decorator(f):
        return option('--chartYName', '-cyn', metavar='<json_str>', required=required, default='Y',
                      help='Display name for chart(s) Y axis')(f)

    return decorator


def chart_x_name_option(required=False):
    def decorator(f):
        return option('--chartXName', '-cxn', metavar='<str>', required=required, default='X',
                      help='Display name for charts X axis')(f)

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
