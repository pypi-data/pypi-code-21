from ext_cloud.BaseCloud.BaseIdentity.BaseIdentity import BaseIdentitycls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackIdentitycls(OpenStackBaseCloudcls, BaseIdentitycls):

    def __init__(self, **kwargs):
        super(OpenStackIdentitycls, self).__init__(credentials=kwargs)

    def list_metrics(self):
        from ext_cloud.BaseCloud.BaseResources.BaseMetrics import BaseMetricscls
        metrics = []
        metrics.append(BaseMetricscls('openstack.tenants.count', len(self.list_tenants())))
        metrics.append(BaseMetricscls('openstack.users.count', len(self.list_users())))

        # alltenants metrics
        import datetime

        now = datetime.datetime.utcnow()
        usages = self._Clients.nova.usage.list(now - datetime.timedelta(days=1), now, detailed=True)
        vms = total_memory_mb_usage = total_local_gb_usage = total_vcpus_usage = 0

        for usage in usages:
            total_vcpus_usage += usage.total_vcpus_usage
            total_memory_mb_usage += usage.total_memory_mb_usage
            total_local_gb_usage += usage.total_local_gb_usage
            vms += len(usage.server_usages)

        metrics.append(BaseMetricscls('openstack.alltentant1day.hours_cpu', total_vcpus_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1day.hours_memory', total_memory_mb_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1day.hours_disk', total_local_gb_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1day.used_vm', vms))

        from dateutil.relativedelta import relativedelta
        one_month_back = now - relativedelta(months=1)
        usages = self._Clients.nova.usage.list(one_month_back, now, detailed=True)
        vms = total_memory_mb_usage = total_local_gb_usage = total_vcpus_usage = 0

        for usage in usages:
            total_vcpus_usage += usage.total_vcpus_usage
            total_memory_mb_usage += usage.total_memory_mb_usage
            total_local_gb_usage += usage.total_local_gb_usage
            vms += len(usage.server_usages)

        metrics.append(BaseMetricscls('openstack.alltentant1month.hours_cpu', total_vcpus_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1month.hours_memory', total_memory_mb_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1month.hours_disk', total_local_gb_usage))
        metrics.append(BaseMetricscls('openstack.alltentant1month.used_vm', vms))
        return metrics

    @property
    def Childrens(self):
        return self.list_tenants()

    def list_users_cache(self):
        from ext_cloud.utils.dogpile_utils import get_region
        from dogpile.cache.api import NO_VALUE

        region = get_region()

        users = region.get('users')
        if users is not NO_VALUE:
            return users
        dic = {}
        users = self.list_users()
        for user in users:
            dic[user.id] = user.obj_to_dict()

        region.set('users', dic)
        return dic

    def list_users(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackUser import OpenStackUsercls
        openstack_users = self._Clients.keystone.users.list()
        users = []
        for openstack_user in openstack_users:
            user = OpenStackUsercls(openstack_user, credentials=self._credentials)
            users.append(user)
        return users

    def get_user_by_id(self, user_id):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackUser import OpenStackUsercls
        from keystoneclient.openstack.common.apiclient.exceptions import NotFound
        try:
            openstack_user = self._Clients.keystone.users.get(user_id)
        except NotFound:
            # user got deleted
            return None

        user = OpenStackUsercls(openstack_user, credentials=self._credentials)
        return user

    def list_tenants_cache(self):
        from dogpile.cache.api import NO_VALUE
        from ext_cloud.utils.dogpile_utils import get_region

        region = get_region()

        tenants = region.get('tenants')
        if tenants is not NO_VALUE:
            return tenants
        dic = {}
        tenants = self.list_tenants()
        for tenant in tenants:
            dic[tenant.id] = tenant.obj_to_dict()

        region.set('tenants', dic)
        return dic

    def list_tenants(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackTenant import OpenStackTenantcls
        openstack_tenants = self._Clients.keystone.tenants.list()
        tenants = []
        for openstack_tenant in openstack_tenants:
            tenant = OpenStackTenantcls(openstack_tenant, credentials=self._credentials)
            tenants.append(tenant)
        return tenants

    def get_tenant_by_id(self, tenant_id):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackTenant import OpenStackTenantcls
        from keystoneclient.openstack.common.apiclient.exceptions import NotFound
        try:
            openstack_tenant = self._Clients.keystone.tenants.get(tenant_id)
        except NotFound:
            return None
        tenant = OpenStackTenantcls(openstack_tenant, credentials=self._credentials)
        return tenant

    def create_token(self):
        from ext_cloud.OpenStack.utils.OpenStackClients import OpenStackClientsCls
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackToken import OpenStackTokenCls
        keystone_client = OpenStackClientsCls().get_keystone_client(self._credentials)
        return OpenStackTokenCls(keystone_client, credentials=self._credentials)
