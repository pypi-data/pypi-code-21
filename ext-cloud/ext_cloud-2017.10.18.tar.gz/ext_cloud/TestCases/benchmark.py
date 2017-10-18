#!/usr/bin/python
from os import environ
from datetime import datetime


class Benchmark:

    def __init__(self):
        self._nova_client = None
        self._keystone_client = None
        self._neutron_client = None
        self._network = None
        self._subnet = None
        self._vms = []
        self._nics = []
        self._stats = None
        self._run_id = 0

        self.check_env_varibles()
        self.init_clients()
        self.init_network()
        self._stats = [[0 for _ in range(int(environ.get('RUNS')))] for _ in range(int(environ.get('MAX_VMS')))]
        self._run_id = 0

    def init_network(self):
        params = {'network': {'name': 'TEST'}}
        self._network = self._neutron_client.create_network(params)
        params = {
            'subnet': {'network_id': self._network['network']['id'],
                       'ip_version': 4,
                       'name': 'TEST',
                       'cidr': '10.0.0.0/24'}}
        self._subnet = self._neutron_client.create_subnet(params)

    def delete_network(self):
        self._neutron_client.delete_network(self._network['network']['id'])

    def create_vms(self, count=1):
        self._vms = []
        for i in range(count):
            params = {'port': {'network_id': self._network['network']['id'],
                               'fixed_ips': [{'subnet_id': self._subnet['subnet']['id']}]
                               }
                      }

            nic_dict = self._neutron_client.create_port(params)
            self._nics.append(nic_dict)
            nics = [{"port-id": nic_dict['port']['id']}]
            vm = self._nova_client.servers.create('TEST', environ['IMAGE_ID'], environ['FLAVOR_ID'], nics=nics)
            self._vms.append(vm)
            vm_is_up = False
            while vm_is_up is False:
                vm_info = self._nova_client.servers.get(vm.id)
                if vm_info.status == 'ACTIVE':
                    vm_is_up = True
                    launch_time = getattr(vm_info, 'OS-SRV-USG:launched_at')
                    created_time = datetime.strptime(vm_info.created, '%Y-%m-%dT%H:%M:%SZ')
                    launch_time = datetime.strptime(getattr(vm_info, 'OS-SRV-USG:launched_at'), '%Y-%m-%dT%H:%M:%S.%f')
                    self._stats[self._run_id][i] = (launch_time - created_time).total_seconds()
                if vm_info.status == 'ERROR':
                    return

                from time import sleep
                sleep(5)

    def delete_vms(self):
        for vm in self._vms:
            self._nova_client.servers.delete(vm.id)

        self._vms = []
        for nic in self._nics:
            self._neutron_client.delete_port(nic['port']['id'])

    def start(self):
        for _ in range(int(environ.get('RUNS'))):
            self.create_vms(count=int(environ.get('MAX_VMS')))
            self.delete_vms()
            self._run_id += 1

    def cleanup(self):
        self.delete_network()

    def printstats(self):
        print self._stats

    def init_clients(self):
        from keystoneauth1 import loading
        from keystoneauth1 import session
        from novaclient import client as novaclient
        from neutronclient.v2_0 import client as neutronclient
        from keystoneclient.v3 import client as keystoneclient

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(auth_url=environ['OS_AUTH_URL'], username=environ['OS_USERNAME'], password=environ['OS_PASSWORD'], project_name=environ['OS_PROJECT_NAME'], user_domain_id=environ['OS_USER_DOMAIN_ID'], project_domain_id=environ['OS_PROJECT_DOMAIN_ID'])
        self._session = session.Session(auth=auth)
        self._nova_client = novaclient.Client(2, session=self._session)
        self._keystone_client = keystoneclient.Client(session=self._session)
        service = self._keystone_client.services.list(name='neutron', type='network')
        endpoint = self._keystone_client.endpoints.list(service=service[0].id)
        self._neutron_client = neutronclient.Client(token=auth.get_token(self._session), endpoint_url=endpoint[0].url)

    def check_env_varibles(self):
        env_varibles = ['OS_PROJECT_DOMAIN_ID', 'OS_USER_DOMAIN_ID', 'OS_PROJECT_NAME', 'OS_TENANT_NAME', 'OS_USERNAME', 'OS_PASSWORD', 'OS_AUTH_URL', 'OS_IDENTITY_API_VERSION', 'IMAGE_ID', 'FLAVOR_ID', 'RUNS', 'MAX_VMS']

        for env_varible in env_varibles:
            if environ.get(env_varible) is None:
                raise Exception('Environment varible {}  not exported'.format(env_varible))

    def clean_up(self):
        pass


b = Benchmark()
b.start()
b.cleanup()
b.printstats()
