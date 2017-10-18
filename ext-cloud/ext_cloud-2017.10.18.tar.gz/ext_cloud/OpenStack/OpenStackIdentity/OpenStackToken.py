from ext_cloud.BaseCloud.BaseIdentity.BaseToken import BaseTokencls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackTokenCls(OpenStackBaseCloudcls, BaseTokencls):

    __keystone_client = None

    def __init__(self, *arg, **kwargs):
        self.__keystone_client = arg[0]
        super(OpenStackTokenCls, self).__init__(id=self.__keystone_client.auth_token, name=self.__keystone_client.auth_token, credentials=kwargs['credentials'])

    @property
    def username(self):
        return self.__keystone_client.username

    @property
    def tenant_name(self):
        return self.__keystone_client.tenant_name

    @property
    def auth_url(self):
        return self.__keystone_client.auth_url

    @property
    def expiry_time(self):
        return self.__keystone_client.auth_ref.expires

    @property
    def issued_time(self):
        return self.__keystone_client.auth_ref.issued

    @property
    def roles(self):
        return self.__keystone_client.auth_ref.role_names

    @property
    def is_scoped(self):
        return self.__keystone_client.auth_ref.scoped

    @property
    def is_federated(self):
        return self.__keystone_client.auth_ref.is_federated
