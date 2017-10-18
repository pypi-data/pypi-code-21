from ext_cloud.BaseCloud.BaseVolumes.BaseSnapshot import BaseSnapshotcls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSSnapshotcls(AWSBaseCloudcls, BaseSnapshotcls):

    __aws_snapshot = None

    def __init__(self, *arg, **kwargs):
        self.__aws_snapshot = arg[0]
        name = None
        if 'Name' in self.__aws_snapshot.tags:
            name = self.__aws_snapshot.tags['Name']

        super(AWSSnapshotcls, self).__init__(id=self.__aws_snapshot.id, name=name, credentials=kwargs['credentials'])

    @property
    def size(self):
        pass

    @property
    def state(self):
        return self.__aws_snapshot.status
