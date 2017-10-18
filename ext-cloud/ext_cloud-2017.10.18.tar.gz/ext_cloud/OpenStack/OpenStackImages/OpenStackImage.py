from ext_cloud.BaseCloud.BaseImages.BaseImage import BaseImagecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackImagecls(OpenStackBaseCloudcls, BaseImagecls):

    __openstack_image = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_image = arg[0]
        super(OpenStackImagecls, self).__init__(id=self.__openstack_image.id,
                                                name=self.__openstack_image.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        return self.__human_format(self.__openstack_image['size'])

    @property
    def state(self):
        return self.__openstack_image['status']

    @property
    def arch(self):
        return self.__openstack_image['architecture'] if hasattr(self.__openstack_image, 'architecture') else None

    @property
    def os_type(self):
        return self.__openstack_image['os_type'] if hasattr(self.__openstack_image, 'os_type') else None

    @property
    def os_distribution(self):
        return self.__openstack_image['os_distro'] if hasattr(self.__openstack_image, 'os_distro') else None

    @property
    def format(self):
        return self.__openstack_image['disk_format']

    def __human_format(self, num):
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0
