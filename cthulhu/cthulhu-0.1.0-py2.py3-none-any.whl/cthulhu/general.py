def progress_bar(*args, **kwargs):
    """
    Shamelessly taken from https://github.com/tqdm/tqdm/blob/master/examples/include_no_requirements.py
    Makes tqdm available without enforcing it as a dependency
    """
    try:
        from tqdm import tqdm
    except ImportError:
        def tqdm(*args, **kwargs):
            if args:
                return args[0]
            return kwargs.get('iterable', None)
