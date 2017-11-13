from ext_cloud.BaseCloud.BaseCompute.BaseInstanceType import BaseInstanceTypecls
from ext_cloud.Azure.AzureBaseCloud import AzureBaseCloudcls


class AzureInstanceTypecls(AzureBaseCloudcls, BaseInstanceTypecls):

    __azure_instancetype = None

    def __init__(self, *arg, **kwargs):
        self.__azure_instancetype = arg[0]

        super(AzureInstanceTypecls, self).__init__(id=self.__azure_instancetype['id'], name=self.__azure_instancetype['name'], credentials=kwargs['credentials'])

    @property
    def memory(self):
        return self.__azure_instancetype['ram']

    @property
    def disk(self):
        return None

    @property
    def cpus(self):
        return self.__azure_instancetype['cpus']
