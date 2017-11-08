import copy

from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, ANY)


class Parameter(Jsonizable):
    """Parameter"""

    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Description': STRING,
        'Type': STRING,
        'Default': ANY,
        'LocalPath': STRING
    }
    required = []
    available_types = {
        "String": STRING + (type(None), ),
        "Number": NUMBER + (type(None), ),
    }

    def __init__(self, dct={}):
        super(Parameter, self).__init__(dct)
        if "Description" not in self._d:
            self._d["Description"] = ""
        if "Default" not in self._d:
            self._d["Default"] = None
        if "Type" not in self._d:
            self._d["Type"] = "String"
        if "LocalPath" not in self._d:
            self._d["LocalPath"] = ""

        if self._d["Type"] not in self.available_types:
            raise RuntimeError("""Type must be one of belows: %s""" % self.available_types)

        default_value = self._d["Default"]
        type_ = self.available_types[self._d["Type"]]

        if not isinstance(default_value, type_):
            raise RuntimeError("""Default value type(%s) does not match Type value(%s)""" % (type(default_value), type_))
Parameter = add_metaclass(Parameter, CamelCasedClass)

InputParameter = Parameter 
OutputParameter = Parameter


class Docker(Jsonizable):
    """Docker"""

    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Image': STRING,
        'RegistryOSSPath': STRING,
    }
    required = ['Image']

    def __init__(self, dct={}):
        super(Docker, self).__init__(dct)
Docker = add_metaclass(Docker, CamelCasedClass)


class VM(Jsonizable):
    """VM"""

    descriptor_type = 'data descriptor'
    descriptor_map = {
        'ECSImageId': STRING,
    }
    required = ['ECSImageId']

    def __init__(self, dct={}):
        super(VM, self).__init__(dct)
VM = add_metaclass(VM, CamelCasedClass)

def define_one_config(name, value_type, default_value):

    class OneConfig(Jsonizable):
        descriptor_type = 'data descriptor'
        descriptor_map = {
            'Description': STRING,
            'Default': ANY,
            'Overwritable': bool,
        }
        required = []
        default = None

        def __init__(self, dct={}):
            super(self.__class__, self).__init__(dct)
            if 'Default' not in self._d:
                self.setproperty("Default", self.default)
            if 'Description' not in self._d:
                self.setproperty('Description', "")
            if 'Overwritable' not in self._d:
                self.setproperty('Overwritable', True)

    class ConfigMeta(CamelCasedClass):
        def __new__(cls, nm, parents, attrs):
            super_new = super(ConfigMeta, cls).__new__
            cls.default = default_value
            attrs['descriptor_map']['Default'] = value_type

            return super_new(cls, name, parents, attrs)

    if not isinstance(default_value, value_type):
        raise RuntimeError("default value type not match")

    return add_metaclass(OneConfig, ConfigMeta)

MaxRetryCount = define_one_config("MaxRetryCount", NUMBER, 0)
ResourceType = define_one_config("ResourceType", STRING, "OnDemand")
InstanceType = define_one_config("InstanceType", STRING, "")
InstanceCount = define_one_config("InstanceCount", NUMBER, 1)
MinDiskSize = define_one_config("MinDiskSize", NUMBER, 40)
DiskType = define_one_config("DiskType", STRING, "cloud_efficiency")
Timeout = define_one_config("Timeout", NUMBER, 86400)

class Config(Jsonizable):
    """Config"""

    descriptor_type = 'data descriptor'
    descriptor_map = {
        'ResourceType': (dict, ResourceType),
        'InstanceType': (dict, InstanceType),
        'InstanceCount': (dict, InstanceCount),
        'MinDiskSize': (dict, MinDiskSize),
        'DiskType': (dict, DiskType),
        'MaxRetryCount': (dict, MaxRetryCount),
        'Timeout': (dict, Timeout)
    }
    required = []

    def __init__(self, dct={}):
        super(Config, self).__init__(dct)

    def set_resource_type(self, value, overwritable=True, description=""):
        self.ResourceType.Default = value
        self.ResourceType.Description = description
        self.ResourceType.overwritable = overwritable

    def set_instance_type(self, value, overwritable=True, description=""):
        self.InstanceType.Default = value
        self.InstanceType.Description = description
        self.InstanceType.Overwritable = overwritable

    def set_instance_count(self, value, overwritable=True, description=""):
        self.InstanceCount.Default = value
        self.InstanceCount.Description = description
        self.InstanceCount.Overwritable = overwritable

    def set_min_disk_size(self, value, overwritable=True, description=""):
        self.MinDiskSize.Default = value
        self.MinDiskSize.Description = description
        self.MinDiskSize.Overwritable = overwritable

    def set_disk_type(self, value, overwritable=True, description=""):
        self.DiskType.Default = value
        self.DiskType.Description = description
        self.DiskType.Overwritable = overwritable

    def set_max_retry_count(self, value, overwritable=True, description=""):
        self.MaxRetryCount.Default = value
        self.MaxRetryCount.Description = description
        self.MaxRetryCount.Overwritable = overwritable

    def set_timeout(self, value, overwritable=True, description=""):
        self.Timeout.Default = value
        self.Timeout.Description = description
        self.Timeout.Overwritable = overwritable
Config = add_metaclass(Config, CamelCasedClass)


class AppDescription(Jsonizable):
    """AppDescription"""

    resource_name = 'apps'
    descriptor_type = 'data descriptor'
    descriptor_map = {
            'Name': STRING,
            'Description': STRING,
            'InputParameters': dict,
            'OutputParameters': dict,
            'Docker': (dict, Docker),
            'VM': (dict, VM),
            'CommandLine': STRING,
            'EnvVars': dict,
            'Daemonize': bool,
            'Config': (dict, Config)
            }
    required = [
            'Name',
            'CommandLine'
            ]

    def __init__(self, dct={}):
        super(AppDescription, self).__init__(dct)
        if 'InputParameters' not in self._d:
            self.setproperty('InputParameters' , dict())
        if 'OutputParameters' not in self._d:
            self.setproperty('OutputParameters', dict())

    def _validate_input_parameter(self, params):
        return copy.deepcopy(params) if params.__class__ == InputParameter else InputParameter(params)

    def add_input_parameter(self, name, params):
        if not name and not isinstance(name, STRING):
            raise TypeError('''parameter name must be str and can't be empty ''')
        self._d['InputParameters'][name] = self._validate_input_parameter(params)

    def delete_input_parameter(self, name):
        if  name in self._d['InputParameters']:
            del self._d['InputParameters'][name]
        else:
            pass

    def get_input_parameter(self, name):
        if name in self._d['InputParameters']:
            return self._d['InputParameters'][name]
        else:
            raise KeyError(''''%s' is not a valid inputParameter name''' % name)

    def _validate_output_parameter(self, params):
        return copy.deepcopy(params) if params.__class__ == OutputParameter else OutputParameter(params)

    def add_output_parameter(self, name, params):
        if not name and not isinstance(name, STRING):
            raise TypeError('''outputParameter name must be str and can't be empty ''')
        self._d['OutputParameters'][name] = self._validate_output_parameter(params)

    def delete_output_parameter(self, name):
        if name in self._d['OutputParameters']:
            del self._d['OutputParameters'][name]
        else:
            pass

    def get_outpu_parameter(self, name):
        if name in self._d['OutputParameters']:
            return self._d['OutputParameters'][name]
        else:
            raise KeyError(''''%s' is not a valid outputParameter name''' % name)

    def setproperty(self, key, value):
        super_set = super(AppDescription, self).setproperty
        if key == 'InputParameters' and isinstance(value, dict):
            for name, params in value.items():
                value[name] = self._validate_input_parameter(params)
            new_value = value
        elif key == "OutputParameters" and isinstance(value, dict):
            for name, params in value.items():
                value[name] = self._validate_output_parameter(params)
            new_value = value
        else:
            new_value = value
        super_set(key, new_value)

    def set_resource_type(self, value, overwritable=True, description=""):
        self.Config.set_resource_type(value, overwritable, description)

    def set_instance_type(self, value, overwritable=True, description=""):
        self.Config.set_instance_type(value, overwritable, description)

    def set_instance_count(self, value, overwritable=True, description=""):
        self.Config.set_instance_count(value, overwritable, description)

    def set_min_disk_size(self, value, overwritable=True, description=""):
        self.Config.set_min_disk_size(value, overwritable, description)

    def set_disk_type(self, value, overwritable=True, description=""):
        self.Config.set_disk_type(value, overwritable, description)

    def set_max_retry_count(self, value, overwritable=True, description=""):
        self.Config.set_max_retry_count(value, overwritable, description)

    def set_timeout(self, value, overwritable=True, description=""):
        self.Config.set_timeout(value, overwritable, description)
AppDescription = add_metaclass(AppDescription, CamelCasedClass)
