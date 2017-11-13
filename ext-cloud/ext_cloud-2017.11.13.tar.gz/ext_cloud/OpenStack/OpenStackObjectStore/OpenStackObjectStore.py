from ext_cloud.BaseCloud.BaseObjectStore.BaseObjectStore import BaseObjectStorecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackObjectStorecls(OpenStackBaseCloudcls, BaseObjectStorecls):

    def __init__(self, **kwargs):
        self.__swiftclient = None
        self._credentials['username'] = kwargs['username']
        self._credentials['password'] = kwargs['password']
        self._credentials['region_name'] = kwargs['region_name']

    @property
    def __SwiftClient(self):
        return self.__swiftclient

    @__SwiftClient.getter
    def __SwiftClient(self):
        if self.__swiftclient is None:
            # Todo
            return "TODO"
        return self.__swiftclient

    def get_all_buckets(self):
        pass

    def get_bucket_by_name(self, bucket_name):
        pass

    def create_bucket(self, bucket_name):
        pass
