from ext_cloud.BaseCloud.BaseVolumes.BaseVolume import BaseVolumecls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSVolumecls(AWSBaseCloudcls, BaseVolumecls):

    __aws_volume = None

    def __init__(self, *arg, **kwargs):
        self.__aws_volume = arg[0]
        name = None
        if 'Name' in self.__aws_volume.tags:
            name = self.__aws_volume.tags['Name']

        super(AWSVolumecls, self).__init__(id=self.__aws_volume.id, name=name, credentials=kwargs['credentials'])

    # override name property
    @AWSBaseCloudcls.name.setter
    def name(self, value):
        self.__aws_volume.add_tag('Name', value)
        self._name = value

    @property
    def description(self):
        pass

    @property
    def size(self):
        return self.__aws_volume.size

    @property
    def state(self):
        return self.__aws_volume.status

    @property
    def instance_id(self):
        return self.__aws_volume.attach_data.instance_id

    @property
    def device_name(self):
        return self.__aws_volume.attach_data.device

    @property
    def attach_time(self):
        attach_time = self.__aws_volume.attach_data.attach_time
        if attach_time is None:
            return
        import datetime
        dt = datetime.datetime.strptime(attach_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        return dt.strftime("%B %d, %Y %I:%M:%S %p")

    @property
    def creation_time(self):
        creation_time = self.__aws_volume.create_time
        if creation_time is None:
            return
        import datetime
        dt = datetime.datetime.strptime(creation_time, '%Y-%m-%dT%H:%M:%S.%fZ')
        return dt.strftime("%B %d, %Y %I:%M:%S %p")

    def addtag(self, name, value):
        self.__aws_volume.add_tag(name, value)

    def gettags(self):
        return self.__aws_volume.tags
