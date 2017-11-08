'''Implementation of jsonizable Job, Task, Instance, Image and four types
responses of BatchComputeClient service.
'''
import copy

from batchcompute.utils import CamelCasedClass, remap, add_metaclass
from batchcompute.utils.jsonizable import Jsonizable, BatchEncoder
from batchcompute.utils.constants import STRING, NUMBER, TIME, PY2, PY3, COLLECTION
from batchcompute.utils.functions import import_json
from batchcompute.utils.log import get_logger
from batchcompute.resources import Configs, Mounts, Disks
from batchcompute.resources import InputMappingConfig 
from batchcompute.resources import Notification 
from batchcompute.resources import AppDescription

json = import_json()
logger = get_logger('batchcompute.client.response')

########################
#RESOURCES STATUS CLASS#
########################
class Group(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'DesiredVMCount': NUMBER,
        'ActualVMCount': NUMBER,
        'InstanceType': STRING,
        'ResourceType': STRING,
        'Disks': (dict, Disks),
    }

    def __init__(self, dct):
        super(Group, self).__init__(dct)
Group = add_metaclass(Group, CamelCasedClass)

class Metrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'RunningCount': NUMBER,
        'StartingCount': NUMBER,
        'StoppingCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(Metrics, self).__init__(dct)
Metrics = add_metaclass(Metrics, CamelCasedClass)

class Cluster(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Id': STRING,
        'OwnerId': NUMBER,
        'Description': STRING,
        'CreationTime': TIME,
        'State': STRING,
        'InstanceType': STRING,
        'ImageId': STRING,
        'UserData': dict,
        'EnvVars': dict,
        'InputMapping': dict,
        'InputMappingConfig': (InputMappingConfig, dict),
        'Notification': (Notification, dict),
        'Configs': (Configs, dict),
        'WriteSupport': bool,
        'Bootstrap': STRING,
        'SecurityGroup': STRING,
        'Groups': dict,
        'OperationLogs': list,
        'Metrics': (Metrics, dict),
    }

    def __init__(self, dct):
        super(Cluster, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Cluster, self).setproperty
        if key == 'Groups':
            new_value = {}
            for group_name in value:
                new_value[group_name] = self._validate_group(value[group_name])
        elif key == 'Configs' and isinstance(value, dict):
            new_value = Configs(value)
        elif key == 'Metrics' and isinstance(value, dict):
            new_value = Metrics(value)
        elif key == 'InputMappingConfig' and isinstance(value, dict):
            new_value = InputMappingConfig(value)
        elif key == 'Notification' and isinstance(value, dict):
            new_value = Notification(value)
        else:
            new_value = value
        super_set(key, new_value)

    def _validate_group(self, group):
        return copy.deepcopy(group) if isinstance(group, Group) else Group(group)

    def get_group(self, group_name):
        if group_name in self._d['Groups']:
            return self._d['Groups'][group_name]
        else:
            raise KeyError(''''%s' is not a valid group name''' % group_name)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_cluster_id = other
            else:
                other_cluster_id = other['Id']
            return cmp(self['Id'], other_cluster_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_cluster_id = other
            else:
                other_cluster_id = other['Id']
            return self['Id'] < other_cluster_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Id']):
            other_cluster_id = other
        else:
            other_cluster_id = other['Id']
        return self['Id'] == other_cluster_id
Cluster = add_metaclass(Cluster, CamelCasedClass)

class ClusterInstance(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Id': STRING,
        'Hint': STRING,
        'State': STRING,
        'IpAddress': STRING,
        'HostName': STRING,
        'ErrorCode': NUMBER,
        'ErrorMessage': STRING,
        'CreationTime': TIME,
    }

    def __init__(self, dct):
        super(ClusterInstance, self).__init__(dct)
ClusterInstance = add_metaclass(ClusterInstance, CamelCasedClass)

class TaskMetrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'WaitingCount': NUMBER,
        'RunningCount': NUMBER,
        'FinishedCount': NUMBER,
        'FailedCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(TaskMetrics, self).__init__(dct)
TaskMetrics = add_metaclass(TaskMetrics, CamelCasedClass)

class InstanceMetrics(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'WaitingCount': NUMBER,
        'RunningCount': NUMBER,
        'FinishedCount': NUMBER,
        'FailedCount': NUMBER,
        'StoppedCount': NUMBER,
    }

    def __init__(self, dct):
        super(InstanceMetrics, self).__init__(dct)
InstanceMetrics = add_metaclass(InstanceMetrics, CamelCasedClass)


class Job(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Name': STRING,
        'Id': STRING,
        'Priority': NUMBER,
        'Owner': STRING,
        'State': STRING,
        'Message': STRING,
        'CreationTime': TIME, 
        'StartTime': TIME, 
        'EndTime': TIME, 
        'TaskMetrics': (TaskMetrics, dict),
        'InstanceMetrics': (InstanceMetrics, dict)
    }

    def __init__(self, dct):
        super(Job, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Job, self).setproperty
        if key == 'TaskMetrics' and isinstance(value, dict):
            new_value = TaskMetrics(value)
        elif key == 'InstanceMetrics' and isinstance(value, dict):
            new_value = InstanceMetrics(value)
        else:
            new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            '''
            Used as method to sort a collection of Job in Python 2.

            Build-in functions `cmp` and `__cmp__` were deprecated since Python
            3.
            '''
            if isinstance(other, self.descriptor_map['Id']):
                other_job_id = other
            else:
                other_job_id = other['Id']
            return cmp(self['Id'], other_job_id)

    if PY3:
        def __lt__(self, other):
            '''
            Used as method to sort a collection of Job in Python 3.
            '''
            if isinstance(other, self.descriptor_map['Id']):
                other_job_id = other
            else:
                other_job_id = other.Id
            return self.Id < other_job_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Id']):
            other_job_id = other
        else:
            other_job_id = other['Id']
        return self['Id'] == other_job_id
Job = add_metaclass(Job, CamelCasedClass)


class Task(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'TaskName': STRING,
        'State': STRING,
        'StartTime': TIME,
        'EndTime': TIME,
        'InstanceMetrics': (InstanceMetrics, dict),
    }

    def __init__(self, dct):
        super(Task, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Task, self).setproperty
        if key == 'InstanceMetrics' and isinstance(value, dict):
            new_value = InstanceMetrics(value)
        else:
            new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['TaskName']):
                other_task_name = other
            else:
                other_task_name = other.TaskName
            return cmp(self['TaskName'], other_task_name)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['TaskName']):
                other_task_name = other
            else:
                other_task_name = other.TaskName
            return self.TaskName < other_task_name 

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['TaskName']):
            other_task_name = other
        else:
            other_task_name = other.TaskName
        return self.TaskName == other_task_name 
Task = add_metaclass(Task, CamelCasedClass)

class Disk(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'ECSSnapshotId': STRING,
    }

    def __init__(self, dct):
        super(Disk, self).__init__(dct)
Disk = add_metaclass(Disk, CamelCasedClass)


class Result(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'ExitCode': NUMBER,
        'ErrorCode': STRING,
        'ErrorMessage': STRING,
        'Detail': STRING,
    }

    def __init__(self, dct):
        super(Result, self).__init__(dct)
Result = add_metaclass(Result, CamelCasedClass)


class Error(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
         'Code': STRING,
         'Message': STRING
    }
    required = []

    def __init__(self, dct={}):
        super(Error, self).__init__(dct)
Error = add_metaclass(Error, CamelCasedClass)

class Instance(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'InstanceId': NUMBER,
        'State': STRING,
        'StartTime': TIME,
        'EndTime': TIME,
        'RetryCount': NUMBER,
        'Progress': NUMBER,
        'StdoutRedirectPath': STRING,
        'StderrRedirectPath': STRING,
        'Result': (Result, dict),
        'Error': (Error, dict),
        'Outputs': dict,
    }

    def __init__(self, dct):
        super(Instance, self).__init__(dct)
        if 'Outputs' not in self._d:
            self.setproperty('Outputs', dict())

    def setproperty(self, key, value):
        super_set = super(Instance, self).setproperty
        if key == 'Result' and isinstance(value, dict):
            new_value = Result(value)
        elif key == 'Error' and isinstance(value, dict):
            new_value = Error(value)
        else:
            new_value = value
        super_set(key, new_value)

    def get_output(self, name):
        if name in self._d['Outputs']:
            return self._d['Outputs'][name]
        else:
            raise KeyError(''''%s' is not a valid Output name''' % name)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['InstanceId']):
                other_instance_id = other
            else:
                other_instance_id = other['InstanceId']
            return cmp(self['InstanceId'], other_instance_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['InstanceId']):
                other_instance_id = other
            else:
                other_instance_id = other['InstanceId']
            return self['InstanceId'] < other_instance_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['InstanceId']):
            other_instance_id = other
        else:
            other_instance_id = other['InstanceId']
        return self['InstanceId'] == other_instance_id
Instance = add_metaclass(Instance, CamelCasedClass)

class SynchronousInstance(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'RequestId': STRING,
        'StartTime': TIME,
        'EndTime': TIME,
        'Outputs': dict,
        'Error': (Error, dict),
    }

    def __init__(self, dct):
        super(SynchronousInstance, self).__init__(dct)
        if 'Outputs' not in self._d:
            self.setproperty('Outputs', dict)

    def setproperty(self, key, value):
        super_set = super(SynchronousInstance, self).setproperty
        if key == 'Error' and isinstance(value, dict):
            new_value = Error(value)
        else:
            new_value = value
        super_set(key, new_value)

    def get_output(self, name):
        if name in self._d['Outputs']:
            return self._d['Outputs'][name]
        else:
            raise KeyError(''''%s' is not a valid Output name''' % name)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['RequestId']):
                other_instance_id = other
            else:
                other_instance_id = other['RequestId']
            return cmp(self['RequestId'], other_instance_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['RequestId']):
                other_instance_id = other
            else:
                other_instance_id = other['RequestId']
            return self['RequestId'] < other_instance_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['RequestId']):
            other_instance_id = other
        else:
            other_instance_id = other['RequestId']
        return self['RequestId'] == other_instance_id
SynchronousInstance = add_metaclass(SynchronousInstance, CamelCasedClass)

class Image(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        "Name": STRING,
        "Id": STRING,
        "Type": STRING,
        "Description": STRING,
        "EcsImageId": STRING,
        "OwnerId": NUMBER,
        "Platform": STRING,
        "CreationTime": TIME
    }

    def __init__(self, dct):
        super(Image, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Image, self).setproperty
        new_value = value
        super_set(key, new_value)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_image_id = other
            else:
                other_image_id = other['Id']
            return cmp(self['Id'], other_image_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['Id']):
                other_image_id = other
            else:
                other_image_id = other['Id']
            return self['Id'] < other_image_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Id']):
            other_image_id = other
        else:
            other_image_id = other['Id']
        return self['Id'] == other_image_id
Image = add_metaclass(Image, CamelCasedClass)

class Quota(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        "AvailableClusterInstanceDataDiskType": list,
        "AvailableClusterInstanceSystemDiskType": list,
        "AvailableClusterInstanceType": list ,
        "AvailableClusterResourceType": list,
        "AvailableSpotInstanceType": list,
    }

    def __init__(self, dct):
        super(Quota, self).__init__(dct)

    def setproperty(self, key, value):
        super_set = super(Quota, self).setproperty
        new_value = value
        super_set(key, new_value)
Quota = add_metaclass(Quota, CamelCasedClass)

class App(AppDescription):
    descriptor_type = "data descriptor"
    descriptor_map = copy.deepcopy(AppDescription.descriptor_map)
    descriptor_map["CreationTime"] = TIME 

    def __init__(self, dct={}):
        super(App, self).__init__(dct)

    if PY2:
        def __cmp__(self, other):
            if isinstance(other, self.descriptor_map['Name']):
                other_app_id = other
            else:
                other_app_id = other['Name']
            return cmp(self['Name'], other_app_id)

    if PY3:
        def __lt__(self, other):
            if isinstance(other, self.descriptor_map['Name']):
                other_app_id = other
            else:
                other_app_id = other['Name']
            return self['Name'] < other_app_id

    def __eq__(self, other):
        if isinstance(other, self.descriptor_map['Name']):
            other_app_id = other
        else:
            other_app_id = other['Name']
        return self['Name'] == other_app_id
App = add_metaclass(App, CamelCasedClass)


class AppRevision(Jsonizable):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Revision': NUMBER,
        'UpdateTime': TIME,
            }
    def __init__(self, dct):
        super(AppRevision, self).__init__(dct)
AppRevision = add_metaclass(AppRevision, CamelCasedClass)


################
#RESPONSE CLASS#
################

class RawResponse(object):
    '''
    Base class for all client response subclasses.

    Mainly suppulys `StatusCode`, `RequestId` and `Date` property and methods
    to retrive them.

    '''
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'StatusCode': NUMBER,
        'RequestId': STRING,
        'Date': STRING,
    }

    def __init__(self, response, human_readable):
        self._d = {}

        self.setproperty('StatusCode', response.status)
        self.setproperty('RequestId', response.getheader('x-acs-request-id', "") or response.getheader('request-id', ""))
        self.setproperty('Date', response.getheader('date'))

        response_body = response.read()
        logger.debug("Raw data recieved from batchcompute service: %s", response_body)
        self.content = remap(response_body, human_readable)

    def getproperty(self, key):
        return self._d[key]

    def setproperty(self, key, value):
        if key in self.descriptor_map:
            if isinstance(value, self.descriptor_map[key]):
                self._d[key] = value
            else:
                raise TypeError('Property %s must be type of %s, actual value: %s'%(key,
                                str(self.descriptor_map[key]), str(value)))

    if PY2:
        def __str__(self):
            return json.dumps(self._d, indent=4) 
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return json.dumps(self._d, indent=4) 
        __repr__ = __bytes__
RawResponse = add_metaclass(RawResponse, CamelCasedClass)


class CreateResponse(RawResponse):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'Id': STRING,
        'Name': STRING
    }
    descriptor_map.update(RawResponse.descriptor_map)

    def __init__(self, response, human_readable):
        super(CreateResponse, self).__init__(response, human_readable)
        if 'Id' in self.content:
            self.setproperty('Id', self.content['Id'])
        if 'Name' in self.content:
            self.setproperty('Name', self.content['Name'])
            if 'Id' not in self.content:
                self.setproperty('Id', self.content['Name'])
CreateResponse = add_metaclass(CreateResponse, CamelCasedClass)

class ActionResponse(RawResponse):
    '''
    Response for operations on jobs(Stop, Start, delete).
    '''
    def __init__(self, response, human_readable):
        super(ActionResponse, self).__init__(response, human_readable)


class GetResponse(RawResponse):
    '''
    Response for get operations on jobs, tasks or images.
    '''
    def __init__(self, response, type_, human_readable):
        super(GetResponse, self).__init__(response, human_readable)
        # Instantiation the real resource status class with the http body(
        # usually a json formatted string) returned by BatchCompute service.
        self._container = type_(self.content)

    def __getattr__(self, attr):
        return getattr(self._container, attr)

    if PY2:
        def __str__(self):
            return self._container.__str__()
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return self._container.__bytes__()
        __repr__ = __bytes__


class ListResponse(RawResponse):
    descriptor_type = 'non data descriptor'
    descriptor_map = {
        'NextMarker': STRING + NUMBER,
        'Items': list
    }
    descriptor_map.update(RawResponse.descriptor_map)

    def __init__(self, response, type_, human_readable):
        super(ListResponse, self).__init__(response, human_readable)
        self.type = type_
        if "Items" in self.content:
            self._container = [item for item in map(self._instantial_item, self.content['Items'])]
            self.setproperty('NextMarker', self.content['NextMarker'])
        else:
            self._container = [item for item in map(self._instantial_item, self.content)]
            self.setproperty('NextMarker', "")
        self.setproperty('Items', self._container)

    def _instantial_item(self, obj):
        if isinstance(self.type, COLLECTION):
            for type_ in self.type:
                if isinstance(obj, type_):
                    return type_(obj)
        else:
            return self.type(obj)

    def __getattr__(self, attr):
        return getattr(self._container, attr)

    def __iter__(self):
        return iter(self._container)

    def __getitem__(self, index_or_slice):
        return self._container[index_or_slice]

    def __len__(self):
        return len(self._container)

    if PY2:
        def __str__(self):
            return json.dumps(self._d, indent=4, cls=BatchEncoder)
        __repr__ = __str__

    if PY3:
        def __bytes__(self):
            return json.dumps(self._d, indent=4, cls=BatchEncoder)
        __repr__ = __bytes__
ListResponse = add_metaclass(ListResponse, CamelCasedClass)
