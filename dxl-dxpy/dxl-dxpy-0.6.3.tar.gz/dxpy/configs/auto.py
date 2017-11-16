def parse_configs(func, *args, configs_filename=None, **kwargs):
    """ Analysic func args and inputs/JSON file.

    Inputs:

        * args: tuple of positional arguments,                
        * configs_filename: filename or list of filenames of JSON file(s), *which may
          or may not present in original function's argument list*.
        * kwargs: dict of keyword arugments.

    Returns:
        1. a tuple, positional arguments,        
        2. a dict, keyword arugments.

    Raises:

    """
    # TODO: refine doc, add test.
    if isinstance(configs_filename, str):
        configs_filename = [configs_filename]
    if configs_filename is None:
        configs_filename = []
    json_dicts = []
    for fn in configs_filename:
        with open(fn, 'r') as fin:
            json_dicts.append(json.load(fin))
    sig = inspect.signature(func)
    kwargs['configs_filename'] = configs_filename
    kwargs = ChainMap(*([kwargs] + json_dicts))
    func_arg_keys = [k for k in sig.parameters]
    poped_keys = []
    func_arg_keys_tmp = list(func_arg_keys)
    for a, k in zip(args, func_arg_keys_tmp):
        poped_keys.append(func_arg_keys.pop(func_arg_keys.index(k)))
    kwargs_fine = {k: kwargs.get(k)
                   for k in func_arg_keys if kwargs.get(k) is not None}
    ba = sig.bind(*args, **kwargs_fine)
    ba.apply_defaults()
    return ba.args, ba.kwargs, poped_keys
