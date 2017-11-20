# -*- coding:utf-8 -*-

import inspect
from terminal import prompt, password, green
from batchcompute_sge.lib import bccluster_json, ecs_client, sge_common,it_config
import socket
import time
import os
from ..util.debugger import *

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_hostname():
    hostname = socket.gethostname()
    return hostname

def get_hostname_ip(hostname):
    try:
        ip = socket.gethostbyname(hostname)
        return ip
    except:
        return None

def fix_hostname_ip():
    hostname = get_hostname()
    ip = get_ip()
    hostname_ip = get_hostname_ip(hostname)

    if ip=='127.0.0.1' or not hostname_ip or hostname_ip != ip:
        print('fix ip hostname binding...')
        with open('/etc/hosts', 'r') as f:
            txt = f.read()

        if hostname_ip != ip:
            txt += '\n%s %s' % (ip, hostname)
        else:
            lines = txt.split('\n')
            t=[]
            for line in lines:
                line = line.strip()
                line_ip_host = line.split(' ')
                if 2==len(line_ip_host) and line_ip_host[0]==hostname_ip[1]:
                    t.append(ip+' '+line_ip_host[1])
                else:
                    t.append(line)
            txt = '\n'.join(t)

        with open('/etc/hosts', 'w+') as f:
            f.write(txt)
        print('fixed')



def register_service():
    d = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
    script_file = os.path.join(d, '../bin/sge_master_watchdog')
    cmd = 'chmod 755 ' + script_file
    sge_common.run_cmd(cmd)
    cmd = 'cp %s /etc/init.d' % script_file
    sge_common.run_cmd(cmd)
    cmd = 'command -v chkconfig >/dev/null 2>&1'
    if sge_common.run_cmd(cmd) == 0:
        cmd = 'chkconfig --add sge_master_watchdog >/dev/null 2>&1'
        sge_common.run_cmd(cmd)
        cmd = 'chkconfig sge_master_watchdog on >/dev/null 2>&1'
        sge_common.run_cmd(cmd)
    elif sge_common.run_cmd('command -v update-rc.d >/dev/null 2>&1') == 0:
        cmd = 'update-rc.d sge_master_watchdog defaults >/dev/null 2>&1'
        sge_common.run_cmd(cmd)
    else:
        raise Exception('no available service tools such as chkconfig, update-rc.d etc.')

def restart_service():
    cmd = '/sbin/service sge_master_watchdog restart'
    if os.environ.get('DEBUG'):
        print cmd
    msg = sge_common.run_cmd_for_stdout(cmd)
    if 'error' in msg or "sge_qmaster didn't start" in msg:
        raise Exception('Failed to run: %s, msg: %s' % (cmd, msg))

def login(region, accessKeyId='', accessKeySecret='', oxsRegion='', oxsAccessKeyId='', oxsAccessKeySecret=''):

    #print('login: %s %s %s' % (region, accessKeyId, accessKeySecret))

    '''
    steps:

     1. 登录 ak , 生成配置 /root/.bccluster.json
     2. 查询 master 安全组, 放到配置中。
     3. watchdog--> init 开机自启, 启动
     4. qconf  失败重试

    :param region:
    :param accessKeyId:
    :param accessKeySecret:
    :return:
    '''

    fix_hostname_ip()


    try:
        opt = bccluster_json.get()
    except:
        opt = {}

    opt['region'] = region

    if accessKeyId:
        opt['access_key_id'] = accessKeyId
    else:
        opt['access_key_id'] = prompt('input access_key_id')

    if accessKeySecret:
        opt['access_key_secret'] = accessKeySecret
    else:
        opt['access_key_secret'] = password('input access_key_secret')



    # for test env
    if oxsRegion:
        opt['oxs_region'] = oxsRegion
    if oxsAccessKeyId:
        opt['oxs_access_key_id'] = oxsAccessKeyId
    if oxsAccessKeySecret:
        opt['oxs_access_key_secret'] = oxsAccessKeySecret


    # 额外加个, 获取所有ecs instancetype 列表
    generate_ecs_instance_type_map(opt)


    master_host_name = socket.gethostname()
    master_instance_id = get_master_instance_id(master_host_name)

    try:
        # classic
        result = ecs_client.get_sg_id_by_instance_id(master_instance_id, opt)

        if len(result['Instances']['Instance'])==0:
            # vpc
            master_instance_id = os.popen('curl http://100.100.100.200/latest/meta-data/instance-id').read()
            result = ecs_client.get_sg_id_by_instance_id(master_instance_id, opt)

        if len(result['Instances']['Instance'])>0:

            opt['master_security_group_id'] = result['Instances']['Instance'][0]['SecurityGroupIds']['SecurityGroupId'][0]
            print('Got master_security_group_id: %s' % opt['master_security_group_id'] )


            if result['Instances']['Instance'][0].get('VpcAttributes') and result['Instances']['Instance'][0]['VpcAttributes'].get('VpcId'):
                opt['master_vpc_id'] = result['Instances']['Instance'][0]['VpcAttributes'].get('VpcId')
                print('Got master_vpc_id: %s' % opt['master_vpc_id'])

        else:
            raise Exception('Can not found master_security_group_id by %s' % master_instance_id)

        bccluster_json.save(opt)

        # todo 3. watchdog--> init 开机自启, 启动
        sge_common.set_act_qmaster(sge_common.SGE_ROOT, sge_common.SGE_CELL_NAME, master_host_name)
        register_service()
        restart_service()
        time.sleep(1)

        # step 4. qconf -as $(hostname)
        qconf_cmd = 'qconf -as %s' % master_host_name
        print(qconf_cmd)
        os.system(qconf_cmd)

        print(green('login success'))

    except Exception as e:
        dstack()

        e = '%s' % e
        if 'nodename nor servname provided' in e:
            raise Exception('Invalid region %s' % region)
        else:
            raise Exception(e)




def get_master_instance_id(name):
    if name[1] == 'Z' and name[-1:] == 'Z':
        return '%s-%s' % (name[:1],name[2:-1] )
    else:
        raise Exception('Current machine is not an available master machine')


# generate ecs instanse type map
def generate_ecs_instance_type_map(opt):
    result = ecs_client.get_all_instance_types(opt)

    arr = result.get('InstanceTypes').get('InstanceType')

    m = {}
    for n in arr:
        m[n['InstanceTypeId']]={
            'name': n['InstanceTypeId'],
            'cpu': n['CpuCoreCount'],
            'memory': n['MemorySize'],
        }
    it_config.save(m)
