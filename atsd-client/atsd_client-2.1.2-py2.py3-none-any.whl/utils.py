import six


def print_tags(tags):
    return ';'.join(['%s=%s' % (k, v) for k, v in six.iteritems(tags)])


def print_str(label):
    return label if label else ''
