from argparse import ArgumentParser

CONFIG_OPT_DEST = 'config_file_path'


def path_to_cmd_opt(path):
    return '--' + '-'.join(map(str.lower, path))


def path_to_dest(path):
    return '_'.join(path)


def get_param(tc, path):
    if len(path) == 1:
        return tc._parameters[path[0]]
    return get_param(getattr(tc, path[0]), path[1:])


def get_parser(tc):
    parser = ArgumentParser()
    parser.add_argument('-C', '--config', dest=CONFIG_OPT_DEST,
            help='set main conf file to load configuration from')
    for path in tc._get_all_parameters_path():
        param, parser_kw = get_param(tc, path), {}

        if param.get('no_cmd'):
            continue
        flag = param['cmd_line_opt'] if param.get('cmd_line_opt') \
                else path_to_cmd_opt(path)

        if 'type' in param:
            parser_kw['type'] = param['type']
            if param['type'] is bool and param.get('default') is False:
                param['action'], param['default'] = 'store_true', False
            elif param['type'] is bool and param.get('default') is True:
                param['action'], param['default'] = 'store_false', True
        if 'among' in param:
            parser_kw['choices'] = param['among']
        if 'help_txt' in param:
            parser_kw['help'] = param['help_txt']

        parser.add_argument(flag, dest=path_to_dest(path), **parser_kw)
    return parser
