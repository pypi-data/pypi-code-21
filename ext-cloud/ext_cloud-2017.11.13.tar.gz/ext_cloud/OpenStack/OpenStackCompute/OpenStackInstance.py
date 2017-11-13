from __future__ import division

from ext_cloud.BaseCloud.BaseCompute.BaseInstance import STATE
from ext_cloud.BaseCloud.BaseCompute.BaseInstance import BaseInstancecls
from ext_cloud.OpenStack.OpenStackBaseCloud import OpenStackBaseCloudcls

import datetime

import collections
STATE_MAP = collections.defaultdict(lambda: STATE.UNKNOWN)
STATE_MAP['ACTIVE'] = STATE.RUNNING
STATE_MAP['PAUSED'] = STATE.PAUSED
STATE_MAP['SHUTOFF'] = STATE.STOPPED
STATE_MAP['ERROR'] = STATE.ERROR
STATE_MAP['BUILD'] = STATE.STARTING


class OpenStackInstancecls(OpenStackBaseCloudcls, BaseInstancecls):

    __openstack_instance = None

    def __init__(self, *arg, **kwargs):
        self.__openstack_instance = arg[0]
        super(OpenStackInstancecls, self).__init__(id=self.__openstack_instance.id, name=self.__openstack_instance.name, credentials=kwargs['credentials'])

    @property
    def size(self):
        from ext_cloud.OpenStack.OpenStackCompute.OpenStackCompute import OpenStackComputecls
        compute = OpenStackComputecls(**self._credentials)
        instance_types = compute.list_instancetypes_cache()
        return instance_types[self.__openstack_instance.flavor['id']]['name'] if self.__openstack_instance.flavor['id'] in instance_types else None

    @property
    def total_memory(self):
        from ext_cloud.OpenStack.OpenStackCompute.OpenStackCompute import OpenStackComputecls
        compute = OpenStackComputecls(**self._credentials)
        instance_types = compute.list_instancetypes_cache()
        return int(instance_types[self.__openstack_instance.flavor['id']]['memory']) if self.__openstack_instance.flavor['id'] in instance_types else None

    @property
    def state(self):
        return STATE_MAP[self.__openstack_instance.status].name

    def start(self):
        return self.__openstack_instance.start_instance()

    def stop(self):
        return self.__openstack_instance.stop_instance()

    def reboot(self):
        return self.__openstack_instance.reboot_instance()

    def delete(self):
        pass

    def setname(self, name):
        pass

    def attach_nic(self, port_id=None, net_id=None, ip_address=None):
        self.__openstack_instance.interface_attach(port_id, net_id, ip_address)

    def detach_nic(self, port_id=None):
        self.__openstack_instance.interface_attach(port_id)

    def add_security_group(self, security_group):
        self.__openstack_instance.add_security_group(security_group)

    @property
    def keypair_name(self):
        return self.__openstack_instance.key_name

    @property
    def image_id(self):
        if isinstance(self.__openstack_instance.image, dict):
            return self.__openstack_instance.image['id']

        return None

    @property
    def tenant_name(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        identity = OpenStackIdentitycls(**self._credentials)
        tenants = identity.list_tenants_cache()
        return tenants[self.tenant_id]['name'] if self.tenant_id in tenants else None

    @property
    def tenant_id(self):
        return self.__openstack_instance.tenant_id

    @property
    def user_name(self):
        if self.user_id is None:
            return None

        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        identity = OpenStackIdentitycls(**self._credentials)
        users = identity.list_users_cache()
        return users[self.user_id]['name'] if self.user_id in users else None

    @property
    def user_id(self):
        return self.__openstack_instance.user_id

    @property
    def availability_zone(self):
        return getattr(self.__openstack_instance, 'OS-EXT-AZ:availability_zone')

    @property
    def hypervisor_name(self):
        return getattr(self.__openstack_instance, 'OS-EXT-SRV-ATTR:hypervisor_hostname')

    @property
    def hypervisor_instance_name(self):
        return getattr(self.__openstack_instance, 'OS-EXT-SRV-ATTR:instance_name')

    @property
    def launch_time(self):
        return getattr(self.__openstack_instance, 'OS-SRV-USG:launched_at')

    @property
    def image_name(self):
        if self.image_id is None:
            return None
        from ext_cloud.OpenStack.OpenStackImages.OpenStackImages import OpenStackImagescls
        images_service = OpenStackImagescls(**self._credentials)
        images = images_service.list_images_cache()
        return images[self.image_id]['name'] if self.image_id in images else None

    @property
    def arch(self):
        pass

    @property
    def network_id(self):
        nics = self.__openstack_instance.interface_list()
        if len(nics) == 0:
            return None
        return nics[0].net_id

    @property
    def subnet_id(self):
        pass

    @property
    def port_id(self):
        # return the first port id
        nics = self.__openstack_instance.interface_list()
        if len(nics) == 0:
            return None
        return nics[0].port_id

    @property
    def mac_id(self):
        nics = self.__openstack_instance.interface_list()
        if len(nics) == 0:
            return None
        return nics[0].mac_addr

    @property
    def private_ip(self):
        for key in self.__openstack_instance.addresses:
            nics = self.__openstack_instance.addresses[key]
            for nic in nics:
                if nic['OS-EXT-IPS:type'] == 'fixed':
                    return nic['addr']

    @property
    def public_ip(self):
        for key in self.__openstack_instance.addresses:
            nics = self.__openstack_instance.addresses[key]
            for nic in nics:
                if nic['OS-EXT-IPS:type'] == 'floating':
                    return nic['addr']

    @property
    def dns_name(self):
        pass

    @property
    def creation_time(self):
        pass

    @property
    def os_type(self):
        pass

    def attach_floatingip(self):
        from ext_cloud.OpenStack.OpenStackNetworks.OpenStackNetworks import OpenStackNetworkscls
        nics = OpenStackNetworkscls(**self._credentials).get_all_nics()
        nic_id = None
        for nic in nics:
            if nic.ip_address == self.private_ip:
                nic_id = nic.id
                break
        floatingips_dict = self._Clients.neutron.list_floatingips()
        floatingips_list = floatingips_dict['floatingips']
        floatingip_id = None
        for floatingip in floatingips_list:
            if floatingip['fixed_ip_address'] is None:
                floatingip_id = floatingip['id']
                break

        # empty floating ip not found, create?
        if floatingip_id is None:
            return
        self._Clients.neutron.update_floatingip(floatingip_id, {'floatingip': {'port_id': nic_id}})

    def addtag(self):
        pass

    def gettags(self):
        pass

        # return count number of avg time between start time and end time
    def cpu_usage(self, start_time=None, end_time=None, count=1):
        ret = []
        time_diff = (end_time - start_time).total_seconds()
        increment_value = int(time_diff / count)

        query = []
        query.append({'field': 'resource_id', 'value': self.oid, 'op': 'eq'})
        query.append({'field': 'timestamp', 'value': start_time.isoformat(), 'op': 'gt'})
        query.append({'field': 'timestamp', 'type': '', 'value': end_time.isoformat(), 'op': 'lt'})

        stats = self._Clients.ceilometer.statistics.list('cpu_util', q=query, period=increment_value)
        for s in stats:
            ret.append({'start_time': s.period_start, 'end_time': s.period_end, 'avg': s.avg})

        return ret

    def net_tx_usage(self, start_time=None, end_time=None, count=1):
        ret = []
        if self.port_id is None:
            return ret
        time_diff = (end_time - start_time).total_seconds()
        increment_value = int(time_diff / count)

        query = []

        resource_id = self.hypervisor_instance_name + '-' + self.oid + '-tap' + self.port_id[:11]
        query.append({'field': 'resource_id', 'value': resource_id, 'op': 'eq'})
        query.append({'field': 'timestamp', 'value': start_time.isoformat(), 'op': 'gt'})
        query.append({'field': 'timestamp', 'type': '', 'value': end_time.isoformat(), 'op': 'lt'})

        try:
            stats = self._Clients.ceilometer.statistics.list('network.outgoing.bytes', q=query, period=increment_value)
        except BaseException:
            # Wrong type. Expected '<type 'float'>', got '<class 'bson.int64.Int64'>' (HTTP 400)
            # fixed in ceilometer 5.0, Remove this try except later
            return ret
        for s in stats:
            period_end = datetime.datetime.strptime(s.period_end, "%Y-%m-%dT%H:%M:%S.%f")
            ret.append({'time': period_end, 'bytes': s.max})

        return ret

    def net_rx_usage(self, start_time=None, end_time=None, count=1):
        ret = []
        if self.port_id is None:
            return ret
        time_diff = (end_time - start_time).total_seconds()
        increment_value = int(time_diff / count)

        query = []

        resource_id = self.hypervisor_instance_name + '-' + self.oid + '-tap' + self.port_id[:11]
        query.append({'field': 'resource_id', 'value': resource_id, 'op': 'eq'})
        query.append({'field': 'timestamp', 'value': start_time.isoformat(), 'op': 'gt'})
        query.append({'field': 'timestamp', 'type': '', 'value': end_time.isoformat(), 'op': 'lt'})

        try:
            stats = self._Clients.ceilometer.statistics.list('network.incoming.bytes', q=query, period=increment_value)
        except BaseException:
            # Wrong type. Expected '<type 'float'>', got '<class 'bson.int64.Int64'>' (HTTP 400)
            # fixed in ceilometer 5.0, Remove this try except later
            return ret
        for s in stats:
            period_end = datetime.datetime.strptime(s.period_end, "%Y-%m-%dT%H:%M:%S.%f")
            ret.append({'time': period_end, 'bytes': s.max})

        return ret
        # return count number of avg time between start time and end time

    def mem_usage(self, start_time=None, end_time=None, count=1):
        ret = []
        time_diff = (end_time - start_time).total_seconds()
        increment_value = int(time_diff / count)

        query = []
        query.append({'field': 'resource_id', 'value': self.oid, 'op': 'eq'})
        query.append({'field': 'timestamp', 'value': start_time.isoformat(), 'op': 'gt'})
        query.append({'field': 'timestamp', 'type': '', 'value': end_time.isoformat(), 'op': 'lt'})

        stats = self._Clients.ceilometer.statistics.list('memory.usage', q=query, period=increment_value)
        for s in stats:
            ret.append({'start_time': s.period_start, 'end_time': s.period_end, 'avg': s.avg, 'percentage': s.avg / self.total_memory})

        return ret

    # By defalt return the stats of the last one hour with 6 samples of 10 mins each.
    # By default, ceilometer agent sends stats every 10 mins
    def list_usage_metrics(self, start_time=datetime.datetime.now() - datetime.timedelta(hours=1), end_time=datetime.datetime.now(), count=6):

        metrics = []
        import time
        from ext_cloud.BaseCloud.BaseResources.BaseMetrics import BaseMetricscls
        metric_str = 'openstack.tenant.' + self.tenant_name.replace('@', '_').replace('.', '_') + '.instance.' + self.oid + '.' + self.name + '.'

        results = self.cpu_usage(start_time, end_time, count)
        for result in results:
            full_metric_str = metric_str + 'cpu_usage'

            new_metric = BaseMetricscls(full_metric_str, result['avg'], int(time.mktime(end_time.timetuple())))
            metrics.append(new_metric)

        results = self.mem_usage(start_time, end_time, count)
        for result in results:
            full_metric_str = metric_str + 'mem_usage'

            new_metric = BaseMetricscls(full_metric_str, result['avg'], int(time.mktime(end_time.timetuple())))
            metrics.append(new_metric)

        results = self.net_rx_usage(start_time, end_time, count)
        for result in results:
            full_metric_str = metric_str + 'net_rx'

            new_metric = BaseMetricscls(full_metric_str, result['bytes'], int(time.mktime(result['time'].timetuple())))
            metrics.append(new_metric)

        results = self.net_tx_usage(start_time, end_time, count)
        for result in results:
            full_metric_str = metric_str + 'net_tx'

            new_metric = BaseMetricscls(full_metric_str, result['bytes'], int(time.mktime(result['time'].timetuple())))
            metrics.append(new_metric)

        return metrics

    @property
    def is_zombie(self):
        from ext_cloud.OpenStack.OpenStackIdentity.OpenStackIdentity import OpenStackIdentitycls
        tenant = OpenStackIdentitycls(**self._credentials).get_tenant_by_id(self.tenant_id)
        if tenant is None:
            return True

        user = OpenStackIdentitycls(**self._credentials).get_user_by_id(self.user_id)
        if user is None:
            return True

        return False
