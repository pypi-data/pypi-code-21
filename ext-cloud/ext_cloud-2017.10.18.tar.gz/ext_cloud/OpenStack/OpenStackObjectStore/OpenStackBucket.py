from ext_cloud.BaseCloud.BaseObjectStore.BaseBucket import BaseBucketcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls
from ext_cloud.OpenStack.OpenStackObjectStore.OpenStackKey import OpenStackKeycls


class OpenStackBucketcls(OpenStackBaseCloudcls, BaseBucketcls):

    def __init__(self, *arg, **kwargs):
        self.__openstack_bucket = None
        self.__openstack_bucket = arg[0]

        super(OpenStackBucketcls, self).__init__(id=self.__openstack_bucket.name,
                                                 name=self.__openstack_bucket.name, credentials=kwargs['credentials'])

    def get_all_keys(self):
        openstack_keys = self.__openstack_bucket.get_all_keys()
        keys = []
        for openstack_key in openstack_keys:
            key = OpenStackKeycls(openstack_key, credentials=self._credentials)
            keys.append(key)

        return keys

    def delete(self):
        self.__openstack_bucket.delete()
