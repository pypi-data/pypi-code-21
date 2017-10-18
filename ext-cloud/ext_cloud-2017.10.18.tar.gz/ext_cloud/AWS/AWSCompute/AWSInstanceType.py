from ext_cloud.BaseCloud.BaseCompute.BaseInstanceType import BaseInstanceTypecls
from ext_cloud.AWS.AWSBaseCloud import AWSBaseCloudcls


class AWSInstanceTypecls(AWSBaseCloudcls, BaseInstanceTypecls):

    __aws_instancetype = None

    def __init__(self, *arg, **kwargs):
        self.__aws_instancetype = arg[0]

        super(AWSInstanceTypecls, self).__init__(id=self.__aws_instancetype['id'], name=self.__aws_instancetype['name'], credentials=kwargs['credentials'])

    @property
    def memory(self):
        return self.__aws_instancetype['ram']

    @property
    def disk(self):
        return self.__aws_instancetype['disk']

    @property
    def cpus(self):
        return self.__aws_instancetype['cpus']
