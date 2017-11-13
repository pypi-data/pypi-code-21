from ext_cloud.BaseCloud.BaseVolumes.BaseSnapshot import BaseSnapshotcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackSnapshotcls(OpenStackBaseCloudcls, BaseSnapshotcls):

    __openstack_snapshot = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_snapshot = arg[0]

        super(OpenStackSnapshotcls, self).__init__(id=self.__openstack_snapshot.id,
                                                   name=self.__openstack_snapshot.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        return self.__openstack_snapshot.size

    @property
    def state(self):
        return self.__openstack_snapshot.status

    @property
    def is_zombie(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        tenant = OpenStackIdentitycls(
            **self._credentials).get_tenant_by_id(self.tenant_id)
        if tenant is None:
            return True

        return False

    @property
    def tenant_id(self):
        return getattr(self.__openstack_snapshot, 'os-extended-snapshot-attributes:project_id')
