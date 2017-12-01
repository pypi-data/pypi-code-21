def marshal_dict_to_bash_env(var, value):
    out = ""

    if isinstance(value, str) or isinstance(value, int) or isinstance(value, float) or isinstance(value, bool):
        out = "{}={}".format(var.upper(), value)

    elif isinstance(value, list):
        out = '{}=( {} )'.format(var.upper(), ' '.join(["'{}'".format(v) for v in value]))

    elif isinstance(value, dict):
        for k, v in value.iteritems():
            prefix = '{}_{}'.format(var, k)
            out += marshal_dict_to_bash_env(prefix, v) + '\n'

    return out.strip()
