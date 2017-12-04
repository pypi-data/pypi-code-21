import inspect
from collections import OrderedDict
from copy import deepcopy
from functools import total_ordering
from itertools import chain

import wrapt
import yaml

from . import configfile
from .meta import TypeStructure
from .fields import Field, TypedField, Deprecated


@total_ordering
class Structure(metaclass=TypeStructure):
    def __new__(cls, *args, **kwargs):
        self = super(Structure, cls).__new__(cls)
        self.__dict__ = OrderedDict()
        self._config_file = None  # type: configfile.ConfigFile

        # Register structure for fields that require a reference
        [f.__register_structure__(self) for k, f in self if isinstance(f, Deprecated) and not k.startswith('_')]

        # Ensure instance has copy of attributes and defaults from definition
        self.__dict__.update([(k, deepcopy(getattr(cls, k))) for k in cls.__field_names__
                              if not k.startswith('_')])
        return self

    def __init__(self, *args, **kwargs):
        """
        Initialise a new structured config object.
        :param args: accepts filename, (optionally) appname to create top level config file
        :param kwargs: default values can be set / overridden for elements
        """
        cls = self.__class__
        # Set the yaml name of the class
        self._yaml_tag = '!' + cls.__name__

        self.__dict__.update(kwargs)

        yaml.add_constructor(self._yaml_tag, cls._from_yaml)
        yaml.add_representer(cls, self._to_yaml)
        if args:
            appname = args[1] if len(args) > 1 else None
            configfile.ConfigFile(args[0], self, appname)

    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)

    def _to_yaml(self, dumper, data):
        return dumper.represent_mapping(self._yaml_tag, data.__getstate__(), flow_style=False)

    def __dir__(self):
        return self.__field_names__ + ['__update__', '__as_dict__']

    def __reg_configfile__(self, config_file):
        self._config_file = config_file

    def __iter__(self):
        for key, val in self.__dict__.items():
            yield key, val

    def __contains__(self, item):
        return item in self.__dict__

    def __hasattr__(self, key):
        return key in self.__dict__

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, val, raw=False):
        return self.__setattr__(item, val)

    def __setattr__(self, key, value, raw=False):
        if not hasattr(self, key):
            changed = True
            super().__setattr__(key, value)
        else:
            value = value.value if isinstance(value, Field) else value
            try:
                current = self.__dict__[key]
            except KeyError:
                current = self.__getattribute__(key, raw=True)

            if isinstance(current, TypedField):
                if not raw and current.store_converted:
                    value = current.writer(value)

                changed = current.writer(value) != current.value
                current.value = value
            elif isinstance(current, Field):
                changed = current.value != value
                current.value = value
            else:
                changed = not hasattr(self, key) or value != current
                super().__setattr__(key, value)

        # Write out the yaml on each attribute update
        if changed and not key.startswith('_') and getattr(self, '_config_file', None):
            self._config_file.write_yaml()

    def __getattribute__(self, item, raw=False):
        current = object.__getattribute__(self, item)
        if not raw:
            if isinstance(current, TypedField):
                return current.converter(current.value)
            elif isinstance(current, Field):
                return current.value
        return current

    def __repr__(self):
        return "<%s:{%s}>" % (self.__class__.__name__, ', '.join(("%s:%s" % i for i in self)))

    def __eq__(self, other):
        if hasattr(other, '__getstate__') and not inspect.isclass(other):
            other = dict(other.__getstate__())
        return dict(self.__getstate__()) == other

    def __lt__(self, _):
        return None

    def __getstate__(self):
        return [(key, val.value if isinstance(val, Field) else val)
                for key, val in self.__dict__.items() if not (key.startswith('_') or isinstance(val, Deprecated))]

    def __setstate__(self, state):
        if hasattr(state, '__getstate__'):
            state = state.__getstate__()
        if isinstance(state, dict):
            state = state.items()
        for key, val in state:
            try:
                raw_current = self.__getattribute__(key, raw=True)
                if isinstance(raw_current, Deprecated):
                    raw_current.__register_structure__(self)
                    raw_current.value = val
                else:
                    current = self[key]
                    if inspect.isclass(current) and issubclass(current, Structure):
                        self[key] = current = current()
                    if hasattr(current, '__setstate__'):
                        current.__setstate__(val)
                    else:
                        self[key] = val
            except ValueError as ex:
                msg = "key: %s\n%s" % (key, ex.args[0])
                ex.args = (msg,) + ex.args[1:]
                raise

    def to_dict(self):
        import warnings
        warnings.warn('to_dict is deprecated, please use __as_dict__', DeprecationWarning, stacklevel=2)
        return self.__as_dict__()

    def __as_dict__(self):
        def _dict(val):
            if isinstance(val, Structure):
                val = val.__as_dict__()
            elif isinstance(val, List):
                val = [_dict(val) for val in list(val)]
            elif isinstance(val, Dict):
                val = dict(val)
            return val

        return OrderedDict([(key, _dict(self[key])) for key, val in self
                            if not (key.startswith('_') or isinstance(val, Deprecated))])

    def update(self):
        import warnings
        warnings.warn('update is deprecated, please use __update__', DeprecationWarning, stacklevel=2)
        return self.__as_dict__()

    def __update__(self, data, conf=None):
        conf = self if conf is None else conf
        for key, val in data.items():
            if (not key.startswith('_') and
                        key != '$$hashKey' and
                        key in conf):
                if isinstance(val, dict):
                    self.__update__(val, conf[key])
                elif isinstance(val, list):
                    current = conf[key]
                    if current == val:
                        continue
                    if isinstance(conf[key], list):
                        conf[key].clear()
                        conf[key].extend(val)
                    else:
                        for idx, lval in enumerate(val):
                            self.__update__(lval, conf[key][idx])
                else:
                    conf[key] = val

    @property
    def __config_file__(self):
        if self._config_file:
            return self._config_file.config_path

    def __fdoc__(self, field=None):
        """
        Returns the __doc__ for the given field
        :param str field: structure field to get doc for
        :return: str
        """
        entry = self.__getattribute__(field, raw=True)
        return entry.__doc__


class List(list):
    """
    Overridden list to allow us to wrap functions for automatic write.
    This is required as we can't wrap/replace the builtin list functions
    """

    # yaml_tag = '!list'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __reg_configfile__(self, config_file):
        wrapt.wrap_function_wrapper(self, 'clear', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, 'extend', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, 'pop', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, 'remove', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, 'append', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, 'insert', self._write_after(config_file))
        wrapt.wrap_function_wrapper(self, '__setstate__', self._pass_config(config_file))

    @staticmethod
    def _write_after(config_file):
        _config_file = config_file

        def __write_after(wrapped, instance, args, kwargs):
            ret = wrapped(*args, **kwargs)
            if _config_file:
                _config_file.register_structure(args)
                _config_file.register_structure(kwargs.values())
                _config_file.write_yaml()
            return ret

        return __write_after

    @staticmethod
    def _pass_config(config_file):
        _config_file = config_file

        def __pass_config(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs, config_file=_config_file)

        return __pass_config

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state, config_file=None):
        self.clear()
        for elem in state:
            if config_file and isinstance(elem, (Structure, List, Dict)):
                elem.__reg_configfile__(config_file)
        self.extend(state)

    def __or__(self, other):
        self.__doc__ = other
        return self


class Dict(dict):
    """
    Overridden dict to allow us to wrap functions for automatic write.
    Wrapping the builtins the same way as List didn't work, __setitem__
    would not fire the config writer
    """

    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self.__configfile__ = None

    def __reg_configfile__(self, config_file):
        self.__configfile__ = config_file

    def update(self, *args, **kwargs):
        ret = super(Dict, self).update(*args, **kwargs)
        self._write_after(items=chain(args, kwargs.values))
        return ret

    def clear(self):
        ret = super(Dict, self).clear()
        self._write_after()
        return ret

    def pop(self, *args, **kwargs):
        ret = super(Dict, self).pop(*args, **kwargs)
        self._write_after()
        return ret

    def popitem(self):
        ret = super(Dict, self).popitem()
        self._write_after()
        return ret

    def __setitem__(self, *args, **kwargs):
        ret = super(Dict, self).__setitem__(*args, **kwargs)
        self._write_after(items=chain(args, kwargs.values))
        return ret

    def __setslice__(self, *args, **kwargs):
        ret = super(Dict, self).__setslice__(*args, **kwargs)
        self._write_after(items=chain(args, kwargs.values))
        return ret

    def __delitem__(self, *args, **kwargs):
        ret = super(Dict, self).__delitem__(*args, **kwargs)
        self._write_after()
        return ret

    def _write_after(self, config_file=None, items=None):
        _config_file = config_file or self.__configfile__
        if _config_file:
            _config_file.register_structure(items)
            _config_file.write_yaml()

    @staticmethod
    def _pass_config(config_file):
        _config_file = config_file

        def __pass_config(wrapped, instance, args, kwargs):
            return wrapped(*args, **kwargs, config_file=_config_file)

        return __pass_config

    def __getstate__(self):
        return dict(self)

    def __setstate__(self, state, config_file=None):
        self.clear()
        for key, value in state.items():
            if config_file and isinstance(value, Structure):
                value.__reg_configfile__(config_file)
        self.update(state)

    def __or__(self, other):
        self.__doc__ = other
        return self