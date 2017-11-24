#!/usr/bin/env python
import copy
import json
import socket
import subprocess
from batchcompute import Client, ClientError
from aliyunsdkcore import client as ECSClient
from aliyunsdkecs.request.v20140526 import DescribeSecurityGroupAttributeRequest
from aliyunsdkecs.request.v20140526 import AuthorizeSecurityGroupRequest 
from aliyunsdkecs.request.v20140526 import RevokeSecurityGroupRequest
from batchcompute_sge.lib import sge_common

def sge_add_host(host):
    cmd = 'qconf -ah ' + host
    sge_common.run_cmd(cmd)

def sge_delete_host(host):
    cmd = 'qconf -dh ' + host
    sge_common.run_cmd(cmd)

def sge_add_exec_host(host):
    cmd = 'qconf -ae ' + host
    sge_common.run_cmd(cmd)

def sge_delete_exec_host(host):
    cmd = 'qconf -de ' + host
    sge_common.run_cmd(cmd)

def sge_add_to_allhosts(host):
    cmd = 'qconf -aattr hostgroup hostlist %s @allhosts' % host
    sge_common.run_cmd(cmd)

def sge_delete_from_allhosts(host, logger = None):
    cmd = 'qconf -dattr hostgroup hostlist %s @allhosts' % host
    if logger:
        logger.info(cmd)
    sge_common.run_cmd(cmd)

def sge_get_master_host_name():
    return socket.gethostname()


class Refresher():
    def __init__(self, config, logger = None):
        region = str(config['region'])
        port = int(config.get('bcs_port', 80))
        domain = 'batchcompute.%s.aliyuncs.com' % region
        Client.register_region(region, domain, port = port)
        self.bc_client = Client(domain, str(config['access_key_id']), str(config['access_key_secret']))

        ecs_access_id = str(config.get('oxs_access_key_id', config['access_key_id']))
        ecs_access_key = str(config.get('oxs_access_key_secret', config['access_key_secret']))
        ecs_region = str(config.get('oxs_region', region))
        self.ecs_client = ECSClient.AcsClient(ecs_access_id, ecs_access_key, ecs_region)

        self.master_security_group_id = str(config.get('master_security_group_id', ''))
        self.master_vpc_id = str(config.get('master_vpc_id', ''))
        self.cluster_id = str(config.get('cluster_id', ''))
        self.group_name = 'default' 

        self.logger = logger

        if not self.master_security_group_id and not self.master_vpc_id:
            raise Exception('Both master_security_group_id and master_vpc_id are empty')

    def list_allowed_ips(self):
        ips = []
        request = DescribeSecurityGroupAttributeRequest.DescribeSecurityGroupAttributeRequest()
        request.set_accept_format('json')
        request.set_SecurityGroupId(self.master_security_group_id)
        request.set_Direction('ingress')
        request.set_NicType('intranet')
        raw_result = self.ecs_client.do_action(request)
        result = json.loads(raw_result)
        if 'Code' in result and 'Message' in result:
            raise Exception(raw_result)
        for r in result['Permissions']['Permission']:
            if 'SourceCidrIp' in r:
                ip = r['SourceCidrIp']
                if ip:
                    ip = ip.split('/')[0]
                    if ip != '0.0.0.0':
                        ips.append(ip)
        return ips

    def authorize_ip(self, ip):
        request = AuthorizeSecurityGroupRequest.AuthorizeSecurityGroupRequest()
        request.set_accept_format('json')
        request.set_SecurityGroupId(self.master_security_group_id)
        request.set_IpProtocol('all')
        request.set_SourceCidrIp(ip + '/32')
        request.set_PortRange('-1/-1')
        request.set_NicType('intranet')
        request.set_Policy('accept')

        result = self.ecs_client.do_action(request)
        if 'Code' in result and 'Message' in result:
            raise Exception(result)

    def revoke_ip(self, ip):
        request = RevokeSecurityGroupRequest.RevokeSecurityGroupRequest()
        request.set_accept_format('json')
        request.set_SecurityGroupId(self.master_security_group_id)
        request.set_IpProtocol('all')
        request.set_SourceCidrIp(ip + '/32')
        request.set_PortRange('-1/-1')
        request.set_NicType('intranet')
        request.set_Policy('accept')

        result = self.ecs_client.do_action(request)
        if 'Code' in result and 'Message' in result:
            raise Exception(result)

    def update_security_group(self, new_instances):
        to_be_added = []
        allowed_ips = self.list_allowed_ips()

        for (h, ip) in new_instances.items():
            if ip in allowed_ips:
                allowed_ips.remove(ip)
            else:
                to_be_added.append(ip)

        for ip in allowed_ips:
            try:
                self.revoke_ip(ip)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))

        for ip  in to_be_added:
            try:
                self.authorize_ip(ip)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))

    def fetch_exec_node_configs(self):
        if not self.cluster_id:
            return {}

        marker = "" 
        max_item = 100
        round = 0
        res = {}
        while marker or round == 0:
            response = self.bc_client.list_cluster_instances(
                    self.cluster_id, 
                    self.group_name, 
                    marker, 
                    max_item)
            marker = response.NextMarker
            for cluster_instance in response.Items:
                if cluster_instance.State == 'Running':
                    if cluster_instance.HostName and cluster_instance.IpAddress:
                        res[cluster_instance.HostName] = cluster_instance.IpAddress#XXX
            round += 1
        return res

    def update_etc_hosts(self, configs):
        content = ''
        hosts = '/etc/hosts'
        comment = '# added by bccluster, do NOT modify this'
        need_update = False
        tmp = copy.deepcopy(configs)

        with open(hosts, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                if line.find(comment) < 0:
                    content += line + '\n'
                else:
                    for (host_name, ip_address) in tmp.items():
                        if line.find(host_name) >= 0 and line.find(ip_address) >= 0:
                            del tmp[host_name]
                        else:
                            need_update = True

        if not tmp and not need_update:
            if self.logger:
                self.logger.info('no need to update hosts')
            return

        content += '\n'

        for (host_name, ip_address) in configs.items():
            content += ('%s %s %s\n' % (ip_address, host_name, comment))

        with open(hosts, 'w') as f:
            f.write(content)

        if self.logger:
            self.logger.info('update hosts: ' + str(configs))

    def _list_hosts(self, cmd):
        master_host_name = sge_get_master_host_name()
        stdout = sge_common.run_cmd_for_stdout(cmd).split()
        res = []
        for line in stdout:
            h = line.strip()
            if h != master_host_name:
                res.append(h)
        return res

    def list_sge_hosts(self):
        cmd = 'qconf -sh'
        return self._list_hosts(cmd)

    def list_sge_exec_hosts(self):
        cmd = 'qconf -sel'
        try:
            return self._list_hosts(cmd)
        except Exception, e:
            if 'no execution host defined' in str(e):
                return []
            raise e

    def update_sge_hosts(self, new_instances, old_sge_hosts):
        new_instances = copy.deepcopy(new_instances)
        to_be_deleted = []
        for h in old_sge_hosts:
            if h in new_instances:
                del new_instances[h]
            else:
                to_be_deleted.append(h)

        if to_be_deleted and self.logger:
            self.logger.info('delete hosts: ' + str(to_be_deleted))
        for h in to_be_deleted:
            try:
                sge_delete_from_allhosts(h)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))
            try:
                sge_delete_host(h)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))

        if new_instances and self.logger:
            self.logger.info('add hosts: ' + str(new_instances))
        for h in new_instances:
            try:
                sge_add_host(h)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))
            try:
                sge_add_to_allhosts(h)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))

    def update_sge_exec_hosts(self, new_instances, old_sge_exec_hosts):
        new_instances = copy.deepcopy(new_instances)
        to_be_deleted = []
        for h in old_sge_exec_hosts:
            if h in new_instances:
                del new_instances[h]
            else:
                to_be_deleted.append(h)

        if to_be_deleted and self.logger:
            self.logger.info('delete exec hosts: ' + str(to_be_deleted))
        for h in to_be_deleted:
            try:
                sge_delete_exec_host(h)
            except Exception, e:
                if self.logger:
                    self.logger.exception(str(e))

        '''
        if new_instances and self.logger:
            self.logger.info('add exec hosts: ' + str(new_instances))
        for h in new_instances:
            sge_add_exec_host(h)
        '''

    def refresh(self):
        configs = self.fetch_exec_node_configs()

        try:
            self.update_etc_hosts(configs)
            hosts = self.list_sge_hosts()
            exec_hosts = self.list_sge_exec_hosts()

            for h in exec_hosts:
                if h not in hosts:
                    try:
                        if self.logger:
                            self.logger.info('exec host %s not in hosts' % h)
                        sge_delete_from_allhosts(h, self.logger)
                    except Exception, e:
                        if self.logger:
                            self.logger.exception(str(e))

            self.update_sge_hosts(configs, hosts)
            self.update_sge_exec_hosts(configs, exec_hosts)
        except Exception, e:
            if self.logger:
                self.logger.exception(str(e))

        self.update_security_group(configs)

