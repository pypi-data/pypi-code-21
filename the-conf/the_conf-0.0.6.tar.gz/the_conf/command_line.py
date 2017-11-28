from argparse import ArgumentParser

CONFIG_OPT_DEST = 'config_file_path'


def path_to_cmd_opt(path):
    return '--' + '-'.join(map(str.lower, path))


def path_to_dest(path):
    return '_'.join(path)


def get_parser(path_n_params, config_file_cmd_line):
    parser = ArgumentParser()
    parser.add_argument(*config_file_cmd_line, dest=CONFIG_OPT_DEST,
            help='set main conf file to load configuration from')
    for path, _, param in path_n_params:
        parser_kw = {}

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


def yield_values_from_cmd(path_val_params, opts, config_file_cmd_line):
    parser = get_parser(path_val_params, config_file_cmd_line)
    cmd_line_args, _ = parser.parse_known_args(opts)
    yield getattr(cmd_line_args, CONFIG_OPT_DEST)
    for path, _, _ in path_val_params:
        value = getattr(cmd_line_args, path_to_dest(path))
        if value is not None:
            yield path, value
