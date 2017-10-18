from ext_cloud.BaseCloud.BaseIdentity.BaseTenant import BaseTenantcls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls


class OpenStackTenantcls(OpenStackBaseCloudcls, BaseTenantcls):

    __openstack_tenant = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_tenant = arg[0]
        super(OpenStackTenantcls, self).__init__(id=self.__openstack_tenant.id,
                                                 name=self.__openstack_tenant.name, credentials=kwargs['credentials'])

    @property
    def status(self):
        return 'enabled' if self.__openstack_tenant.enabled is True else 'disabled'

    @property
    def usage(self):
        from ext_cloud.BaseCloud.BaseResources.BaseResourceUsage import BaseResourceUsagecls
        import datetime
        now = datetime.datetime.now()
        epoch = datetime.datetime(year=1970, month=1, day=1)
        tenant_usage = self._Clients.nova.usage.get(self.oid, epoch, now)

        if not hasattr(tenant_usage, 'total_vcpus_usage'):
            return None
        usage_dict = {}
        usage_dict['hours_cpu'] = tenant_usage.total_vcpus_usage
        usage_dict['hours_disk'] = tenant_usage.total_local_gb_usage
        usage_dict['hours_memory'] = tenant_usage.total_memory_mb_usage

        deleted_vms = used_vms = 0
        for vm in tenant_usage.server_usages:
            if vm['state'] == 'terminated':
                deleted_vms += 1
            else:
                used_vms += 1
        usage_dict['deleted_vms'] = deleted_vms
        usage_dict['used_vms'] = used_vms

        return BaseResourceUsagecls(**usage_dict)

    def list_metrics(self):
        metrics = []

        from ext_cloud.BaseCloud.BaseResources.BaseMetrics import BaseMetricscls
        # replace . with - for tenant name
        tenant_name = self.name.replace('.', '_').replace('@', '_')
        metric_str = 'openstack.tenant.' + tenant_name + '.'
        resource_usage = self.usage
        if resource_usage is not None:
            for varible in dir(resource_usage):
                if not varible.startswith("_") and isinstance(getattr(resource_usage.__class__, varible), property):
                    value = getattr(resource_usage, varible)
                    if value is None:
                        continue
                    metrics.append(BaseMetricscls(metric_str + varible, value))

        # network metrics
        from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNetworks import OpenStackNetworkscls
        network_obj = OpenStackNetworkscls(**self._credentials)
        metrics.append(BaseMetricscls(metric_str + 'networks.count',
                                      len(network_obj.get_networks_by_tenant_id(self.oid))))
        metrics.append(BaseMetricscls(metric_str + 'subnets.count',
                                      len(network_obj.get_subnets_by_tenant_id(self.oid))))
        metrics.append(BaseMetricscls(metric_str + 'networks.used_floating_ips',
                                      len(network_obj.list_floating_ips_by_tenant_id(self.oid))))

        return metrics
