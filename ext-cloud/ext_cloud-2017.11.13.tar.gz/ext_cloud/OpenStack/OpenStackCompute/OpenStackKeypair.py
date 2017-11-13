from ext_cloud.BaseCloud.BaseCompute.BaseKeypair import BaseKeypaircls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackKeypaircls(OpenStackBaseCloudcls, BaseKeypaircls):

    __openstack_keypair = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_keypair = arg[0]

        super(OpenStackKeypaircls, self).__init__(id=self.__openstack_keypair.fingerprint,
                                                  name=self.__openstack_keypair.name, credentials=kwargs['credentials'])

    @property
    def privatekey(self):
        if hasattr(self.__openstack_keypair, 'privatekey'):
            return self.__openstack_keypair.privatekey
        return

    @property
    def publickey(self):
        if hasattr(self.__openstack_keypair, 'publickey'):
            return self.__openstack_keypair.publickey

        if hasattr(self.__openstack_keypair, 'public_key'):
            return self.__openstack_keypair.public_key

        return

    def delete(self):
        return self.__openstack_keypair.delete()
