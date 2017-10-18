from ext_cloud.BaseCloud.BaseCloud import BaseCloudcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackcls(OpenStackBaseCloudcls, BaseCloudcls):

    def __init__(self, **kwargs):
        self. __identity = None
        self.__compute = None
        self.__networks = None
        self.__images = None
        self.__volumes = None
        self.__objectstore = None
        self.__templates = None
        self.__resources = None
        self.__childrens = None
        self.__services = None
        self.__regions = None

        if 'username' in kwargs:
            self._credentials = kwargs
            return None
        import os
        # load credentials from environment varible
        if os.environ.get('OS_USERNAME') is not None:
            dic = {}
            dic['username'] = os.environ.get('OS_USERNAME')
            dic['password'] = os.environ.get('OS_PASSWORD')
            dic['tenant_name'] = os.environ.get('OS_TENANT_NAME')
            dic['auth_url'] = os.environ.get('OS_AUTH_URL')
            dic['cacert'] = os.environ.get('OS_CACERT')
            self._credentials = dic

            return None
        # load credentials from config file
        if os.path.exists('/etc/ext_cloud/ext_cloud.conf'):
            from ext_cloud.OpenStack.utils.ConfFileParser import config_file_dic
            dic = config_file_dic()
            self._credentials = dic

            return None
        else:
            raise Exception("Credentails not exported in environment varibles and /etc/ext_cloud/ext_cloud.conf file")

    @property
    def identity(self):
        if self.__identity is None:
            from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
            self.__identity = OpenStackIdentitycls(**self._credentials)

        return self.__identity

    @property
    def compute(self):
        if self.__compute is None:
            from ext_cloud.OpenStack.OpenStackCompute.OpenStackCompute import OpenStackComputecls
            self.__compute = OpenStackComputecls(**self._credentials)

        return self.__compute

    @property
    def networks(self):
        if self.__networks is None:
            from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNetworks import OpenStackNetworkscls
            self.__networks = OpenStackNetworkscls(**self._credentials)

        return self.__networks

    @property
    def images(self):
        if self.__images is None:
            from ext_cloud.OpenStack.OpenStackImages.OpenStackImages import OpenStackImagescls
            self.__images = OpenStackImagescls(**self._credentials)

        return self.__images

    @property
    def volumes(self):
        if self.__volumes is None:
            from ext_cloud.OpenStack.OpenStackVolumes.OpenStackVolumes import OpenStackVolumescls
            self.__volumes = OpenStackVolumescls(**self._credentials)

        return self.__volumes

    @property
    def templates(self):
        if self.__templates is None:
            from ext_cloud.OpenStack.OpenStackTemplates.OpenStackTemplates import OpenStackTemplatescls
            self.__templates = OpenStackTemplatescls(**self._credentials)

        return self.__templates

    @property
    def objectstore(self):
        if self.__objectstore is None:
            from ext_cloud.OpenStack.OpenStackObjectStore.OpenStackObjectStore import OpenStackObjectStorecls
            self.__objectstore = OpenStackObjectStorecls(**self._credentials)

        return self.__objectstore

    @property
    def resources(self):
        if self.__resources is None:
            from ext_cloud.OpenStack.OpenStackResources.OpenStackResources import OpenStackResourcescls
            self.__resources = OpenStackResourcescls(**self._credentials)

        return self.__resources

    @property
    def regions(self):
        if self.__regions is None:
            from ext_cloud.OpenStack.OpenStackRegions.OpenStackRegions import OpenStackRegionscls
            self.__regions = OpenStackRegionscls(credentials=self._credentials)

        return self.__regions

    @property
    def services(self):
        if self.__services is None:
            from ext_cloud.OpenStack.OpenStackServices.OpenStackServices import OpenStackServicescls
            self.__services = OpenStackServicescls(**self._credentials)

        return self.__services

    @property
    def Childrens(self):
        if self.__childrens is None:
            self.__childrens = [self.identity, self.compute, self.networks,
                                self.services, self.regions, self.volumes, self.images]

        return self.__childrens

    def validate_credentials(self):
        self.networks.list_networks()
        return True
