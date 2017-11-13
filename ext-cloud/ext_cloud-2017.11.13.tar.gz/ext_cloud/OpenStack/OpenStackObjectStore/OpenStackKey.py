from ext_cloud.BaseCloud.BaseObjectStore.BaseKey import BaseKeycls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackKeycls(OpenStackBaseCloudcls, BaseKeycls):

    __openstack_key = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_key = arg[0]

        super(OpenStackKeycls, self).__init__(id=self.__openstack_key.name,
                                              name=self.__openstack_key.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        pass

    def delete(self):
        pass

    def download(self, file_path):
        pass

    def upload(self, file_path):
        pass

    def get_url(self):
        pass
