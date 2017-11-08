import copy
from datetime import datetime

from .constants import STRING, PY2
from batchcompute.core.exceptions import (
    FieldError, ValidationError, JsonError
)
from batchcompute.utils import (
    partial, CamelCasedClass, import_json, add_metaclass,
)

json = import_json()
JsonEncoder = json.encoder.JSONEncoder

class Jsonizable(object):
    '''
    An abstraction class of job, task and instance status.

    A dict-like class with lower camel case method, beyond that,
    in descriptor_map.
    '''
    descriptor_type = 'non data descriptor'
    descriptor_map = {}
    required = []

    def __init__(self, properties={}):
        self._d = {}
        if isinstance(properties, STRING):
            self.load(properties)
        elif isinstance(properties, dict):
            self.update(properties)
        elif isinstance(properties, self.__class__):
            self.update(properties.detail())
        else:
            error = (type(properties), self.__class__.__name__)
            raise TypeError('''Invalid type '%s' for '%s' ''' % error)

    def validate(self):
        if self.required:
            for key in self.required:
                if isinstance(key, STRING) and key in self._d:
                    # `key` is a string, check the required property named 
                    # `key` is assigned.
                    if isinstance(self._d[key], Jsonizable):
                        self._d[key].validate()
                elif isinstance(key, list):
                    # `key` is a list, one of the property must be assigned.
                    found = [field for field in key if field in self._d]
                    if len(found) == 1:
                        property_name = found[0]
                        if isinstance(self._d[property_name], Jsonizable):
                            self._d[property_name].validate()
                    elif len(found) > 1:
                        msg = "Only one property in %s should be assigned." % key
                        raise ValidationError(msg)
                    else:
                        msg = "One of the property in %s should be assigned." % key
                        raise ValidationError(msg)
                else:
                    msg = "Property '%s' must be assigned." % key
                    raise ValidationError(key)

    def detail(self):
        return copy.deepcopy(self._d)

    def update(self, d):
        self._update(d)

    def setproperty(self, key, value):
        if key in self.descriptor_map:
            valid_type = self.descriptor_map[key]
            if isinstance(value, valid_type):
                if valid_type == STRING and not value and key in self._d:
                    # Empty string value will result in key deletion from
                    # `self._d`.
                    del self._d[key]
                elif isinstance(valid_type, tuple):
                    default_type = self._get_default_type(valid_type)
                    if isinstance(value, dict) and issubclass(default_type, Jsonizable):
                        self._d[key] = self._init_valid_type(default_type, value)
                    else:
                        self._d[key] = copy.deepcopy(value)
                else:
                    self._d[key] = copy.deepcopy(value)
            else:
                raise TypeError('Property %s must be type of %s'%(key,
                                str(self.descriptor_map[key])))
        else:
            # If the key is not in `self.descriptor_map`, the key-value pair
            # will be discarded.
            error = (key, self.__class__.__name__)

    def getproperty(self, key):
        if key in self.descriptor_map:
            if key not in self._d:
                valid_type = self.descriptor_map[key]
                if valid_type is dict:
                    self._d[key] = {}
                elif isinstance(valid_type, tuple):
                   default_type = self._get_default_type(valid_type) 
                   if default_type is None:
                       raise TypeError('\'%s\'' % key)
                   self._d[key] = self._init_valid_type(default_type)
            return self._d.get(key, None)
        else:
            raise KeyError('\'%s\'' % key)

    def _get_default_type(self, cls_tuple):
        for valid_type in cls_tuple:
            if issubclass(valid_type, Jsonizable):
                return valid_type
        return cls_tuple[0] 

    def _init_valid_type(self, valid_type, value={}):
        if valid_type is None:
            return None
        elif valid_type is datetime and isinstance(value, datetime):
            return value
        elif issubclass(valid_type, Jsonizable):
            return valid_type(value)
        else:
            return copy.deepcopy(value) 

    def _update(self, d):
        for key, value in d.items():
            self.setproperty(key, value)

    def dump(self, indent=4):
        return json.dumps(self._d, indent=indent, cls=BatchEncoder)

    def load(self, json_str):
        try:
            d = json.loads(json_str)
        except ValueError:
            raise JsonError('Bad json format string')
        self._update(d)

    if PY2:
        __str__ = dump
    else:
        __bytes__ = dump
    __repr__ = dump

    def __getattr__(self, attr):
        try:
            return getattr(self._d, attr)
        except AttributeError:
            e = (self.__class__.__name__, attr)
            raise AttributeError(''''%s' object has no attribute '%s' '''%e)

    def __getitem__(self, key):
        return self.getproperty(key)

    def __setitem__(self, key, value):
        if key in self.descriptor_map:
            self.setproperty(key, value)
        else:
            raise FieldError(key)

    def __delitem__(self, key):
        try:
            del self._d[key]
        except KeyError:
            pass

    def __iter__(self):
        return iter(self._d)

    def __contain__(self, key):
        return key in self._d

    def __copy__(self):
        return type(self)(self._d)

    def __deepcopy__(self, memo):
        return type(self)(copy.deepcopy(self._d, memo))

    @classmethod
    def __instancehook__(cls, obj):
        d = obj
        if isinstance(d, STRING):
            try: 
                d = json.loads(obj)
            except:
                return False
        elif isinstance(d, dict):
            d = obj

        if hasattr(cls, "required") and isinstance(cls.required, list) and len(cls.required):
            for name in cls.required:
                if name not in d:
                    return False
            else:
                return True
        else:
             return False

        return False
Jsonizable = add_metaclass(Jsonizable, CamelCasedClass)


class BatchEncoder(JsonEncoder):
    '''
    A encoder for simplejson or json module to encode `Jsonizable` object.
    '''
    def default(self, obj):
        if isinstance(obj, Jsonizable):
            return obj.detail()
        if isinstance(obj, datetime):
            return obj.isoformat(' ')
        return JsonEncoder.encode(self, obj)
