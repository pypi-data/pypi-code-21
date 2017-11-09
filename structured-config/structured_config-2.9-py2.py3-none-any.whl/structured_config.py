__author__ = "Andrew Leech"
__copyright__ = "Copyright 2017, alelec"
__license__ = "MIT"
__maintainer__ = "Andrew Leech"
__email__ = "andrew@alelec.net"

import os
import yaml
import wrapt
import aenum
import inspect
import appdirs
import logging
import pkg_resources
from itertools import chain
from copy import copy, deepcopy
from collections import OrderedDict
from functools import total_ordering


class ConfigFile(object):
    def __init__(self, config_path, config, appname=None):
        """
        Config file container.
        :param str config_path: path to file for storage. Either absolute
                                 or relative. If relative, appname is required
                                 to determine user config folder for platform
        :param Structure config: top level config item
        :param str appname: When using relative path fon config_file,
                             appname is required for user config dir
        """
        self.write_enabled = False
        self.config_path = config_path
        # convert passed in config to a registered instance
        self.config = self.register_structure(config)
        conftype = config if config.__class__ is TypeStructure else config.__class__
        assert isinstance(self.config, conftype)
        log = logging.getLogger("Config")

        if not os.path.isabs(self.config_path):
            if not appname:
                try:
                    mainpkg = __import__('__main__').__package__.split('.')[0]
                    appname = pkg_resources.get_distribution(mainpkg).project_name
                except (AttributeError, IndexError):
                    raise ValueError("Must provide appname for relative config file path")
            appdir = appdirs.user_data_dir(appname=appname)
            if not os.path.exists(appdir):
                try:
                    os.makedirs(appdir)
                except:
                    pass
            self.config_path = os.path.join(appdir, self.config_path)

        # Startup
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as configfile:
                saved_config = yaml.load(configfile).__getstate__()
                self.config.__setstate__(saved_config)
                log.info("Loaded config from %s" % self.config_path)

        self.write_enabled = True

        # Ensure the config file exists for new installations.
        if not os.path.exists(self.config_path):
            self.write_yaml()
            log.info("Initialised new config file at %s" % self.config_path)

    def write_yaml(self):
        if self.write_enabled:
            try:
                os.makedirs(os.path.dirname(self.config_path))
            except OSError:
                pass
            with open(self.config_path, 'w') as configfile:
                yaml.dump(self.config, configfile,
                          default_flow_style=False, Dumper=NoAliasDumper)

    def register_structure(self, structure):
        """
        This will attach this config files' writer to the structure
        :param Structure structure: key to register
        :returns: structure as passed in
        """

        def attach(_structure):
            if inspect.isclass(_structure) and issubclass(_structure, Structure):
                _structure = _structure()
            if isinstance(_structure, Structure):
                _structure.__reg_configfile__(self)

            return _structure

        def register_val(_val):
            if isinstance(_val, Dict):
                _val.__reg_configfile__(self)
            elif isinstance(_val, List):
                _val.__reg_configfile__(self)

            if isinstance(_val, dict):
                _val = Dict(_val)
                for k, v in _val.items():
                    _val[k] = attach(v)
                _val.__reg_configfile__(self)
            elif isinstance(_val, (list, set, tuple)):
                _val = List((attach(v) for v in _val))
                _val.__reg_configfile__(self)

            else:
                _val = attach(_val)
            return _val

        structure = register_val(structure)

        if isinstance(structure, Structure):
            for key, val in structure:
                val = register_val(val)
                structure[key] = val

        return structure


class _ConstructionOrderDict(dict):
    """Track field order and ensure field names are not reused.

    TypeStructure will use the names found in self.__field_names__ to translate
    to indices.
    """

    def __init__(self, *args, **kwds):
        self.__field_names__ = []
        super(_ConstructionOrderDict, self).__init__(*args, **kwds)

    def __setitem__(self, key, value):
        """Records anything not dundered or not a descriptor.

        If a field name is used twice, an error is raised.

        Single underscore (sunder) names are reserved.
        """
        if key in self.__field_names__:
            # overwriting a field?
            raise TypeError('Attempted to reuse field name: %r' % key)
        elif key[:2] == key[-2:] == '__':
            pass
        elif not (hasattr(value, '__get__') or  # Check not a descriptor
                  hasattr(value, '__set__') or
                  hasattr(value, '__delete__')):
            self.__field_names__.append(key)
        super(_ConstructionOrderDict, self).__setitem__(key, value)


class TypeStructure(type):
    @classmethod
    def __prepare__(mcs, cls, bases, *args, **kwargs):
        return _ConstructionOrderDict()

    def __init__(cls, name, bases, dct):
        cls.__field_names__ = dct.__field_names__
        super(TypeStructure, cls).__init__(name, bases, dct)


@total_ordering
class Structure(metaclass=TypeStructure):
    def __new__(cls, *args, **kwargs):
        self = super(Structure, cls).__new__(cls)
        self.__dict__ = OrderedDict()
        self._config_file = None  # type: ConfigFile

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
            ConfigFile(args[0], self, appname)

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
                    value = current.converter(value)

                changed = current.converter(value) != current.value
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
                for key, val in self.__dict__.items() if not key.startswith('_')]

    def __setstate__(self, state):
        if hasattr(state, '__getstate__'):
            state = state.__getstate__()
        if isinstance(state, dict):
            state = state.items()
        for key, val in state:
            try:
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

        return OrderedDict([(key, _dict(self[key])) for key, val in self if not key.startswith('_')])

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


def list_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_list(list(data))


yaml.add_representer(List, list_rep)


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


def dict_rep(dumper, data):
    """
    Ensure pyyaml treats our list as a regular list
    """
    return dumper.represent_dict(dict(data))


yaml.add_representer(Dict, dict_rep)


class NoAliasDumper(yaml.dumper.Dumper):
    """
    Disable alias when writing yaml as these make it harder to
    manually read/modify the config file
    """

    def ignore_aliases(self, data):
        return True


class Field(object):
    """
    Base class for fields that allows capturing of comments or'ed with the field
    """
    def __init__(self, value):
        self.value = value

    def __or__(self, other):
        self.__doc__ = other
        return self

    def __getstate__(self):
        return self.value

    def __setstate__(self, state):
        self.value = state

    def __deepcopy__(self, memodict=None):
        n = self.__class__(deepcopy(self.value, memodict or {}))
        n.__doc__ = self.__doc__
        return n


class TypedField(Field):
    def __init__(self, value, converter, store_converted=True, **kwargs):
        super(TypedField, self).__init__(value=value)
        self.converter = converter
        self.store_converted = store_converted

        cls = self.__class__
        self._yaml_tag = '!' + cls.__name__

        yaml.add_constructor(self._yaml_tag, self._from_yaml)

    def __deepcopy__(self, memodict=None):
        if self.__class__ is TypedField:
            n = self.__class__(deepcopy(self.value, memodict or {}), self.converter, self.store_converted)
        else:
            n = self.__class__(deepcopy(self.value, memodict or {}))
        n.__doc__ = self.__doc__
        return n

    @classmethod
    def _from_yaml(cls, loader, node):
        return loader.construct_yaml_object(node, cls)


class IntField(TypedField):
    def __init__(self, value):
        super(IntField, self).__init__(value, int)


class StrField(TypedField):
    def __init__(self, value):
        super(StrField, self).__init__(value, str)


class FloatField(TypedField):
    def __init__(self, value):
        super(FloatField, self).__init__(value, float)


class PathField(TypedField):
    def __init__(self, value):
        try:
            from pathlib import Path
        except ImportError:
            from pathlib2 import Path
        super(PathField, self).__init__(value, Path)


class RangedNumber(TypedField):
    def __init__(self, value, min, max):
        self.min = min
        self.max = max
        super(RangedNumber, self).__init__(value, self.__check__)

    def __check__(self, value):
        if self.min <= value <= self.max:
            return value
        raise ValueError("%s out of range (%s - %s)" % (value, self.min, self.max))

    def update_range(self, min, max):
        self.min = min
        self.max = max

    def __repr__(self):
        return "<RangedInt:%s<=%s<=%s>" % (self.min, self.value, self.max)

    def __deepcopy__(self, memodict=None):
        n = self.__class__(*deepcopy((self.value, self.min, self.max), memodict or {}))
        n.__doc__ = self.__doc__
        return n


class RangedFloat(RangedNumber):
    def __check__(self, value):
        return super(RangedFloat, self).__check__(float(value))


class RangedInt(RangedNumber):
    def __check__(self, value):
        return super(RangedInt, self).__check__(int(value))


class RangedInts(RangedInt):
    def __check__(self, values):
        return [super(RangedInts, self).__check__(value) for value in values]


class BoolField(TypedField):
    def __init__(self, value):
        super(BoolField, self).__init__(value, self.to_bool)

    @staticmethod
    def to_bool(val):
        if isinstance(val, str):
            val = val.lower() in ['yes', 'true']
        else:
            val = True if val else False
        return val


class Selection(str, aenum.Enum):
    def __init__(self, *_, **__):
        self._value_ = self.name
        str.__init__(self)

    def __deepcopy__(self, memodict=None):
        """Enums are immutable, so it's safe for deepcopy to return self
        """
        return self

    def __copy__(self):
        return self

    def __str__(self):
        return self._value_

    def __eq__(self, other):
        return self is other or str(other) == self._value_


class SelectionField(TypedField):
    def __init__(self, value, allowed_values):
        """
        Enforces the value to be one of the allowed values
        :param str|property value:
        :param List[str] | Type[Selection] allowed_values: the list of allowed values
        """
        if isinstance(allowed_values, list):
            allowed_values = Selection('Selection', allowed_values)
        self.allowed_values = allowed_values
        super(SelectionField, self).__init__(value, self.check)

    def check(self, val):
        return self.allowed_values[str(val)].name

    def __deepcopy__(self, memodict=None):
        n = self.__class__(copy(self.value), copy(self.allowed_values))
        n.__doc__ = self.__doc__
        return n


class MultiSelection(SelectionField):
    def __init__(self, values, allowed_values):
        """
        Enforces the values to be in the allowed values
        :param list|tuple values: list of values which all need to be allowed
        :param List[str] | Type[Selection] allowed_values: the list of allowed values
        """
        super(MultiSelection, self).__init__(tuple(values), allowed_values)

    def check(self, vals):
        return tuple((super(MultiSelection, self).check(val) for val in vals))

