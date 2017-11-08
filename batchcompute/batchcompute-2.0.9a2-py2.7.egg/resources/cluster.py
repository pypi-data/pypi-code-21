import copy

from batchcompute.utils import (partial, add_metaclass, CamelCasedClass)
from batchcompute.utils.jsonizable import Jsonizable
from batchcompute.utils.constants import (STRING, NUMBER, TIME)


class GroupDescription(Jsonizable):
    '''
    Description class of the group resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'DesiredVMCount': NUMBER,
        'InstanceType': STRING,
        'ResourceType': STRING,
    }
    required = [
        'DesiredVMCount'
    ]

    def __init__(self, dct={}):
        super(GroupDescription, self).__init__(dct)
        if 'ResourceType' not in self._d:
            self.setproperty('ResourceType', 'OnDemand')
        if 'InstanceType' not in self._d:
            self.setproperty('InstanceType', '')

    def setproperty(self, key, value):
        super_set = super(GroupDescription, self).setproperty
        if key == 'InstanceType' and not value.strip():
            pass
        else:
            super_set(key, value)


GroupDescription = add_metaclass(GroupDescription, CamelCasedClass)


class SystemDisk(Jsonizable):
    '''Description class of the disk resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Type': STRING,
        'Size': NUMBER,
    }
    required = ['Size']

    def __init__(self, dct={}):
        super(SystemDisk, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(SystemDisk, self).setproperty
        if key == 'Type' and not value.strip():
            pass
        else:
            super_set(key, value)


SystemDisk = add_metaclass(SystemDisk, CamelCasedClass)


class DataDisk(Jsonizable):
    '''Description class of the disk resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Type': STRING,
        'Size': NUMBER,
        'MountPoint': STRING,
    }
    required = ['Size']

    def __init__(self, dct={}):
        super(DataDisk, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(DataDisk, self).setproperty
        if key == 'MountPoint' and not value.strip():
            pass
        elif key == 'Type' and not value.strip():
            pass
        else:
            super_set(key, value)


DataDisk = add_metaclass(DataDisk, CamelCasedClass)


class Disks(Jsonizable):
    '''Description class of the disks resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'SystemDisk': (dict, SystemDisk),
        'DataDisk': (dict, DataDisk)
    }
    required = ['SystemDisk', 'DataDisk']

    def __init__(self, dct={}):
        super(Disks, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Disks, self).setproperty
        if key == 'SystemDisk' and isinstance(value, dict):
            new_value = SystemDisk(value)
        elif key == 'DataDisk' and isinstance(value, dict):
            new_value = DataDisk(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(Disks, self).getproperty

        if key == "SystemDisk" and "SystemDisk" not in self._d:
            self.setproperty("SystemDisk", SystemDisk())
        if key == "DataDisk" and "DataDisk" not in self._d:
            self.setproperty("DataDisk", DataDisk())

        return super_get(key)


Disks = add_metaclass(Disks, CamelCasedClass)


class Classic(Jsonizable):
    '''Description class of the classic network resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'AllowSecurityGroup': list,
        'AllowSecurityGroupEgress': list,
        'AllowIpAddress': list,
        'AllowIpAddressEgress': list
    }

    def __init__(self, dct={}):
        super(Classic, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Classic, self).setproperty
        super_set(key, value)


Classic = add_metaclass(Classic, CamelCasedClass)


class VPC(Jsonizable):
    '''Description class of the classic network resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'CidrBlock': STRING,
        'VpcId': STRING,
        'ExpressConnectSpec': STRING,
        'OppositeRegionId': STRING,
        'OppositeAccessPointId': STRING,
        'OppositeRouterType': STRING,
        'OppositeRouterId': STRING,
        'OppositeInterfaceId': STRING,
    }

    def __init__(self, dct={}):
        super(VPC, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(VPC, self).setproperty
        super_set(key, value)


VPC = add_metaclass(VPC, CamelCasedClass)


class Networks(Jsonizable):
    '''Description class of the networks resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Classic': (dict, Classic),
        'VPC': (dict, VPC),
    }

    def __init__(self, dct={}):
        super(Networks, self).__init__(dct)
        if 'Classic' not in self._d:
            self.setproperty('Classic', Classic())
        if 'VPC' not in self._d:
            self.setproperty('VPC', VPC())

    def setproperty(self, key, value):
        super_set = super(Networks, self).setproperty
        if key == 'Classic' and isinstance(value, dict):
            new_value = Classic(value)
        elif key == 'VPC' and isinstance(value, dict):
            new_value = VPC(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(Networks, self).getproperty

        if key == "Classic" and "Classic" not in self._d:
            self.setproperty("Classic", Classic())
        if key == "VPC" and "VPC" not in self._d:
            self.setproperty("VPC", VPC())

        return super_get(key)


Networks = add_metaclass(Networks, CamelCasedClass)


class MountEntry(Jsonizable):
    '''Description class of the mount resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Source': STRING,
        'Destination': STRING,
        'WriteSupport': bool,
    }

    def __init__(self, dct={}):
        super(MountEntry, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(MountEntry, self).setproperty
        super_set(key, value)


MountEntry = add_metaclass(MountEntry, CamelCasedClass)


class NAS(Jsonizable):
    '''Description class of the NAS resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'AccessGroup': list,
        'FileSystem': list,
    }

    def __init__(self, dct={}):
        super(NAS, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(NAS, self).setproperty
        super_set(key, value)

    def getproperty(self, key):
        super_get = super(NAS, self).getproperty

        if key == "AccessGroup" and "AccessGroup" not in self._d:
            self.setproperty("AccessGroup", list())
        elif key == "FileSystem" and "FileSystem" not in self._d:
            self.setproperty("FileSystem", list())

        return super_get(key)


NAS = add_metaclass(NAS, CamelCasedClass)


class OSS(Jsonizable):
    '''Description class of the OSS resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'AccessKeyId': STRING,
        'AccessKeySecret': STRING,
        'SecurityToken': STRING,
    }

    def __init__(self, dct={}):
        super(OSS, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(OSS, self).setproperty
        super_set(key, value)


OSS = add_metaclass(OSS, CamelCasedClass)


class Mounts(Jsonizable):
    '''Description class of the mounts resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Entries': list,
        'Locale': STRING,
        'Lock': bool,
        'CacheSupport': bool,
        'CacheBlockSize': NUMBER,
        'CacheTotalSize': NUMBER,
        'NAS': (NAS, dict),
        'OSS': (OSS, dict),
    }

    def __init__(self, dct={}):
        super(Mounts, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Mounts, self).setproperty
        if key == 'Entries' and isinstance(value, list):
            new_value = []
            for entry in value:
                new_value.append(self._validate_entry(entry))
        elif key == "NAS" and isinstance(value, dict):
            new_value = NAS(value)
        elif key == "OSS" and isinstance(value, dict):
            new_value = OSS(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(Mounts, self).getproperty

        if key == "Entries" and "Entries" not in self._d:
            self.setproperty("Entries", list())
        if key == "NAS" and "NAS" not in self._d:
            self.setproperty("NAS", NAS())
        if key == "OSS" and "OSS" not in self._d:
            self.setproperty("OSS", OSS())
        return super_get(key)

    def add_entry(self, entry):
        self.Entries.append(self._validate_entry(entry))

    def _validate_entry(self, entry):
        return copy.deepcopy(entry) if entry.__class__ == MountEntry else MountEntry(entry)


Mounts = add_metaclass(Mounts, CamelCasedClass)


class Configs(Jsonizable):
    '''Description class of the configs resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Disks': (dict, Disks),
        'Networks': (dict, Networks),
        'Mounts': (dict, Mounts),
    }
    required = ['Disks']

    def __init__(self, dct={}):
        super(Configs, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Configs, self).setproperty
        if key == 'Disks' and isinstance(value, dict):
            new_value = Disks(value)
        elif key == 'Networks' and isinstance(value, dict):
            new_value = Networks(value)
        elif key == "Mounts" and isinstance(value, dict):
            new_value = Mounts(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(Configs, self).getproperty

        if key == "Networks" and "Networks" not in self._d:
            self.setproperty('Networks', Networks())
        elif key == "Mounts" and "Mounts" not in self._d:
            self.setproperty("Mounts", Mounts())
        elif key == "Disks" and "Disks" not in self._d:
            self.setproperty("Disks", Disks())

        return super_get(key)

    def add_system_disk(self, size, type_='cloud'):
        assert isinstance(size, NUMBER) and isinstance(type_, STRING), \
            'size must be number and type_ must be string'
        disk = {
            'Type': type_,
            'Size': size,
        }

        if "Disks" in self._d:
            self._d['Disks']['SystemDisk'] = disk
        else:
            self._d['Disks'] = {
                'SystemDisk': disk
            }

    def add_data_disk(self, size, type_='cloud', mount_point=''):
        assert isinstance(size, NUMBER) and isinstance(type_, STRING) and \
               isinstance(mount_point, STRING), 'size must be number and type_ must be string'
        disk = {
            'Type': type_,
            'Size': size,
            'MountPoint': mount_point,
        }

        if "Disks" in self._d:
            self._d['Disks']['DataDisk'] = disk
        else:
            self._d['Disks'] = {
                "DataDisk": disk
            }


Configs = add_metaclass(Configs, CamelCasedClass)


class Topic(Jsonizable):
    '''
    Description class of notification configuration in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Endpoint': STRING,
        'Events': list,
    }
    required = [
    ]

    def __init__(self, dct={}):
        super(Topic, self).__init__(dct)
        if 'Name' not in self._d:
            self.setproperty('Name', "")
        if 'Endpoint' not in self._d:
            self.setproperty('Endpoint', "")
        if 'Events' not in self._d:
            self.setproperty('Events', list())

    def setproperty(self, key, value):
        super_set = super(Topic, self).setproperty
        super_set(key, value)


Topic = add_metaclass(Topic, CamelCasedClass)


class Notification(Jsonizable):
    '''
    Description class of notification configuration in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Topic': (Topic, dict),
    }
    required = [
    ]

    def __init__(self, dct={}):
        super(Notification, self).__init__(dct)
        if 'Topic' not in self._d:
            self.setproperty('Topic', dict())

    def setproperty(self, key, value):
        super_set = super(Notification, self).setproperty
        if key == 'Topic' and isinstance(value, dict):
            new_value = Topic(value)
        else:
            new_value = value
        super_set(key, new_value)


Notification = add_metaclass(Notification, CamelCasedClass)


class ClusterDescription(Jsonizable):
    '''
    Description class of the cluster resource type in batchcompute service.
    '''
    resource_name = 'clusters'
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Description': STRING,
        'ImageId': STRING,
        'InstanceType': STRING,
        'UserData': dict,
        'ScheduleType': STRING,
        'Configs': (Configs, dict),
        'Notification': (Notification, dict),
        'Groups': dict,
        'Bootstrap': STRING,
        'EnvVars': dict,
    }
    required = [
        'Name',
        'ImageId',
        'Groups'
    ]

    def __init__(self, dct={}):
        super(ClusterDescription, self).__init__(dct)
        if 'Groups' not in self._d:
            self.setproperty('Groups', {})
        if 'UserData' not in self._d:
            self.setproperty('UserData', {})
            # if 'ScheduleType' not in self._d:
            # self.setproperty('ScheduleType', "Poll")

    def setproperty(self, key, value):
        super_set = super(ClusterDescription, self).setproperty
        if key == 'Groups' and isinstance(value, dict):
            new_value = {}
            for group_name in value:
                new_value[group_name] = self._validate_group(value[group_name])
        elif key == 'Configs' and isinstance(value, dict):
            new_value = Configs(value)
        elif key == 'Notification' and isinstance(value, dict):
            new_value = Notification(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(ClusterDescription, self).getproperty

        if key == "EnvVars" and "EnvVars" not in self._d:
            self.setproperty('EnvVars', dict())
        if key == "UserData" and "UserData" not in self._d:
            self.setproperty('UserData', dict())
        if key == "Configs" and "Configs" not in self._d:
            self.setproperty("Configs", Configs())

        return super_get(key)

    def _validate_group(self, group):
        return copy.deepcopy(group) if group.__class__ == GroupDescription else GroupDescription(group)

    def add_group(self, group_name, group):
        if not group_name and not isinstance(group_name, STRING):
            raise TypeError('''Group name must be str and can't be empty ''')
        self._d['Groups'][group_name] = self._validate_group(group)

    def delete_group(self, group_name):
        if group_name in self._d['Groups']:
            del self._d['Groups'][group_name]
        else:
            pass

    def get_group(self, group_name):
        if group_name in self._d['Groups']:
            return self._d['Groups'][group_name]
        else:
            raise KeyError(''''%s' is not a valid group name''' % group_name)


ClusterDescription = add_metaclass(ClusterDescription, CamelCasedClass)


class ModifyGroupDescription(Jsonizable):
    '''
    Description class of the modify group resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'DesiredVMCount': NUMBER,
    }
    required = [
        'DesiredVMCount'
    ]

    def __init__(self, dct={}):
        super(ModifyGroupDescription, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(ModifyGroupDescription, self).setproperty
        super_set(key, value)


ModifyGroupDescription = add_metaclass(ModifyGroupDescription, CamelCasedClass)


class ModifyConfigs(Jsonizable):
    '''Description class of the modify configs resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'Mounts': (dict, Mounts),
    }
    required = ['Mounts']

    def __init__(self, dct={}):
        super(ModifyConfigs, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(ModifyConfigs, self).setproperty
        if key == "Mounts" and isinstance(value, dict):
            new_value = Mounts(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(ModifyConfigs, self).getproperty

        if key == "Mounts" and "Mounts" not in self._d:
            self.setproperty("Mounts", Mounts())

        return super_get(key)


ModifyConfigs = add_metaclass(ModifyConfigs, CamelCasedClass)


class ModifyClusterDescription(Jsonizable):
    '''
    Description class of the modify cluster resource type in batchcompute service.
    '''
    descriptor_type = 'data descriptor'
    descriptor_map = {
        'UserData': dict,
        'Configs': (ModifyConfigs, dict),
        'Groups': dict,
        'EnvVars': dict,
        'ImageId': STRING,
    }
    required = []

    def __init__(self, dct={}):
        super(ModifyClusterDescription, self).__init__(dct)
        if 'Groups' not in self._d:
            self.setproperty('Groups', {})

    def setproperty(self, key, value):
        super_set = super(ModifyClusterDescription, self).setproperty
        if key == 'Groups' and isinstance(value, dict):
            new_value = {}
            for group_name in value:
                new_value[group_name] = self._validate_group(value[group_name])
        elif key == 'Configs' and isinstance(value, dict):
            new_value = ModifyConfigs(value)
        else:
            new_value = value
        super_set(key, new_value)

    def getproperty(self, key):
        super_get = super(ModifyClusterDescription, self).getproperty

        if key == "Groups" and "Groups" not in self._d:
            self.setproperty("Groups", dict())
        if key == "EnvVars" and "EnvVars" not in self._d:
            self.setproperty('EnvVars', dict())
        if key == "UserData" and "UserData" not in self._d:
            self.setproperty('UserData', dict())
        if key == "Configs" and "Configs" not in self._d:
            self.setproperty("Configs", ModifyConfigs())
        if key == "ImageId" and "ImageId" not in self._d:
            self.setproperty("ImageId", "")

        return super_get(key)

    def _validate_group(self, group):
        return copy.deepcopy(group) if group.__class__ == ModifyGroupDescription else ModifyGroupDescription(group)

    def add_group(self, group_name, group):
        if not group_name and not isinstance(group_name, STRING):
            raise TypeError('''Group name must be str and can't be empty ''')
        self._d['Groups'][group_name] = self._validate_group(group)

    def delete_group(self, group_name):
        if group_name in self._d['Groups']:
            del self._d['Groups'][group_name]
        else:
            pass

    def get_group(self, group_name):
        if group_name in self._d['Groups']:
            return self._d['Groups'][group_name]
        else:
            raise KeyError(''''%s' is not a valid group name''' % group_name)


ModifyClusterDescription = add_metaclass(ModifyClusterDescription, CamelCasedClass)
