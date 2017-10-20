import os

_environ = {'models':os.environ.get('JANUS_MODELS'), 'data':os.environ.get('JANUS_DATA')}

def models(newdir=None):
    if newdir is not None:
        _environ['models'] = newdir
    if _environ['models'] is None:
        raise ValueError('Models directory not defined.  Set environment variable JANUS_MODELS or call this function with a models directory argument.')
    return _environ['models']

def data(newdir=None):
    if newdir is not None:
        _environ['data'] = newdir
    if _environ['data'] is None:
        raise ValueError('Data directory not defined.  Set environment variable JANUS_DATA or call this function with a data directory argument.')        
    return _environ['data']

def get(key=None):
    return _environ[key] if key is not None else _environ

    




