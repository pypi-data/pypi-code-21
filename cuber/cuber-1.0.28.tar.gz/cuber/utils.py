import logging
import json
import numpy as np
import hashlib
import numbers
import pickle
logger = logging.getLogger(__name__)

override_default_hash_type = None

def get_hash(s, hash_type = None):
    assert isinstance(s, str)
    if hash_type is None:
        hash_type = override_default_hash_type if override_default_hash_type is not None else 'sha224'
    if hash_type == 'sha224':
        return hashlib.sha224(s).hexdigest()
    if hash_type in ['murmur1_32', 'fast']:
        import pyhash
        return str(pyhash.murmur1_32()(s))
    raise ValueError('Unknown hash type: {}'.format(hash_type))

def object_hash(obj, fields = None):
    if fields is not None:
        d = {key: value for key, value in obj.__dict__.iteritems() if key in fields}
    else:
        d = obj.__dict__
    return universal_hash(d)

def universal_hash(obj):
    if override_default_hash_type == 'pickle':
        return hashlib.md5(pickle.dumps(obj)).hexdigest()
        
    if isinstance(obj, str):
        return get_hash(obj)
    if isinstance(obj, unicode):
        return get_hash(obj.encode('utf-8'))
    if isinstance(obj, numbers.Number):
        return get_hash(repr(obj))
    if isinstance(obj, dict):
        return reduce(lambda x,y : universal_hash(x + y),
                sorted([universal_hash((universal_hash(key), universal_hash(value))) for key, value in obj.iteritems()]), 
                universal_hash('empty_dict_hash')
            )
    if isinstance(obj, tuple):
        return reduce(lambda x,y : universal_hash(x + y), list(universal_hash(item) for item in obj), universal_hash('empty_array_hash'))
    if isinstance(obj, list):
        return universal_hash(tuple(obj))
    if isinstance(obj, np.ndarray):
        return get_hash(obj.tostring())
    if obj is None:
        return get_hash('none' + 'salt123')
    logger.error('Unsupported type: {}'.format(type(obj))) 
    raise NotImplementedError('Unspported type for hashing: {}. Object: {}'.format(type(obj), obj))

def json_hash(obj):
    raise NotImplementedError('Do not use json hashing, beacuse it is not pure. The order of dict`s keys is not totally specified. You may simple replace json_hash to univrsal_hash')
    return sha224(json.dumps(obj))

def dict_to_string(d, full = False, brackets = False):
    res = '{\n' if brackets else ''
    for key, value in d.iteritems():
        if full or isinstance(value, basestring) or isinstance(value, numbers.Number):
            res += '\t' if brackets else ''
            res += '{}: {}\n'.format(key, value)
        else:
            res += '\t' if brackets else ''
            res += '{}: ...\n'.format(key)
    res += '}' if brackets else ''
    return res

def parse_bool(s):
    '''
    Converts s to bool. If fails, raises an error.
    '''
    if isinstance(s, bool):
        return s
    assert s in {'yes', 'y', '1', 1, '+', 'on', 'enable', 'true',
                 'no',  'n', '0', 0, '-', 'off','disable', 'false'}
    return s in {'yes', 'y', '1', 1, '+', 'on', 'enable', 'true'}

def parse_none(s):
    '''
    returns true if s is None, else false
    '''
    if s is None:
        return True
    return s in {'None', 'none', 'null', 'Null', 'NULL', 'nil'}
