import json
from batchcompute_sge.lib import batchcompute_client, bccluster_json, sge_common
from terminal import green, confirm, bold,magenta, blue, yellow, red, white
from batchcompute_sge.util import list2table, formatter
import socket
from ..util.debugger import *
from batchcompute.core import ClientError

PROGRESS_LEN = 70


def start(nodes, type, image, disk=None,
          mount=None,  nas_access_group=None, nas_file_system=None, no_cache_support=False,
          vpc_cidr_block=None,
          show_json=False):

    obj = bccluster_json.get_required_login()

    if not obj.get('master_security_group_id'):
        raise Exception('you need to login first')

    # has cluster id
    cluster_id = obj.get('cluster_id')

    if cluster_id:
        raise Exception('Found cluster_id, you need to run "bcc stop" to stop it first')

    hostName = socket.gethostname()
    localIP =  socket.gethostbyname(hostName)


    cluster_desc = {}
    cluster_desc['Name'] = "sge-cls-"+ hostName
    cluster_desc['ImageId'] = image
    cluster_desc['InstanceType'] = type
    cluster_desc['Description'] = 'sge cluster, master hostname: %s, created by %s' % (hostName, obj.get('access_key_id'))

    cluster_desc['Groups'] = {
        'default': {
            'InstanceType': type,
            'DesiredVMCount': nodes,
            'ResourceType': 'OnDemand'
        }
    }

    cluster_desc['Bootstrap'] = '/usr/local/bin/sge_bootstrap'
    cluster_desc['EnvVars'] = {
        'SGE_MASTER_IP_ADDRESS': localIP,
        'SGE_MASTER_HOST_NAME': hostName
    }

    cluster_desc['Configs'] = {
        'Networks': {
            'Classic': {
                'AllowSecurityGroup': [obj.get('master_security_group_id')]
            }
        },
        'Mounts': {
           'NAS': {

           }
        }
    }

    # for test env
    if obj.get('oxs_access_key_id') and obj.get('oxs_access_key_secret'):
        cluster_desc['UserData'] = {
            'SecurityCredentials/OssAccessKeyId': obj.get('oxs_access_key_id'),
            'SecurityCredentials/OssAccessKeySecret': obj.get('oxs_access_key_secret'),
            'SecurityCredentials/OssSecurityToken': ''
        }


    if disk:
        cluster_desc['Configs']['Disks'] = disk

    if mount:
        extend_mount(cluster_desc, mount)

    if nas_access_group:
        cluster_desc['Configs']['Mounts']['NAS']['AccessGroup'] = nas_access_group.split(',')
    if nas_file_system:
        cluster_desc['Configs']['Mounts']['NAS']['FileSystem'] = nas_file_system.split(',')

    if no_cache_support:
        cluster_desc['Configs']['Mounts']['CacheSupport'] = not no_cache_support

    if obj.get('master_vpc_id'):
        if not cluster_desc['Configs']['Networks'].get('VPC'):
            cluster_desc['Configs']['Networks']['VPC'] = {}
        cluster_desc['Configs']['Networks']['VPC']['VpcId']=obj['master_vpc_id']

        if not vpc_cidr_block:
            raise Exception('--vpc_cidr_block option is required in VPC')

        cluster_desc['Configs']['Networks']['VPC']['CidrBlock']=vpc_cidr_block


    if show_json:
        print(json.dumps(cluster_desc, indent=4))
    else:
        if obj.get('cluster_id'):
            raise Exception('cluster is started, type "bcc status" for more')

        result = batchcompute_client.create_cluster(cluster_desc)

        if result.StatusCode == 201:
            print(green('batchCompute cluster created, id=%s' % result.Id))

            # save cluster id
            obj['cluster_id']=result.Id
            bccluster_json.save(obj)

            print('\n  type "bcc status" for more\n')


def status(log=False):

    obj = bccluster_json.get_required_login()


    print('%s' % bold(magenta('Master:')))
    hostName = socket.gethostname()
    localIP = socket.gethostbyname(hostName)
    print('  %s: %s'  % (blue('HostName'), hostName ))
    print('  %s: %s' % (blue('IP'), localIP))


    # todo 1: check master watch dog
    cmd = '/sbin/service sge_master_watchdog status'
    out = sge_common.run_cmd_for_stdout(cmd)
    if out.find('running') == -1:
        cmd = '/sbin/service sge_master_watchdog restart'
        sge_common.run_cmd(cmd)

    # step 2: check workers

    # test 'cls-6kiga3ronlg61pnmbui004'
    cluster_id = obj.get('cluster_id')

    if cluster_id:
        cluster_info = batchcompute_client.get_cluster(cluster_id)
        print('%s' % bold(magenta('Worker Config:')))

        print('  %s: %s' % (blue('BatchCompute ClusterId'), cluster_info.get('Id')))
        print('  %s: %s' % (blue('ImageId'), cluster_info.get('ImageId')))
        if cluster_info.get('InstanceType'):
            print('  %s: %s' % (blue('InstanceType'), cluster_info.get('InstanceType')))
        print('  %s: %s' % (blue('State'), formatter.get_cluster_state(cluster_info.get('State'))))


        # disks
        disks = cluster_info.Configs.Disks
        print('  %s' % blue('Disks:'))
        if disks.get('SystemDisk'):
            print(
            '    |--System Disk: %s (%s) %sGB' % ('/', blue(disks['SystemDisk']['Type']), disks['SystemDisk']['Size']))
        if disks.get('DataDisk') and disks['DataDisk'].get('MountPoint'):
            print('    |--Data Disk: %s (%s) %sGB' % (
            disks['DataDisk']['MountPoint'], blue(disks['DataDisk']['Type']), disks['DataDisk']['Size']))
        print('')

        # mounts
        mounts = cluster_info.Configs.Mounts
        print('%s (Locale: %s , Lock: %s , CacheSupport: %s)' % (
        blue('Mounts:'), mounts.get('Locale'), mounts.get('Lock'), mounts.get('CacheSupport')))

        entries = mounts.get('Entries')
        if entries:
            for ent in entries:
                print('  |--%s %s %s' % (ent['Destination'], blue('<-'), green(ent['Source'])))

        nas = mounts.get('  Nas')
        if nas:
            if nas.get('AccessGroup'):
                print('    AccessGroup: %s' % (','.join(nas['AccessGroup'])))
            if nas.get('FileSystem'):
                print('    FileSystem: %s' % (','.join(nas['FileSystem'])))

        oss = mounts.get('OSS')
        if oss:
            if oss.get('AccessKeyId'):
                print('    AccessKeyId: %s' % nas['AccessGroup'])
            if oss.get('AccessKeySecret'):
                print('    AccessKeySecret: %s' % nas['AccessKeySecret'])
            if oss.get('AccessSecurityToken'):
                print('    AccessSecurityToken: %s' % nas['AccessSecurityToken'])

        # Networks
        networks = cluster_info.Configs.Networks
        if networks:
            print('  |--Classic:')
            if networks.get('Classic'):
                if networks['Classic'].get('AllowIpAddress'):
                    print('     |--AllowIpAddress: %s' % ','.join(networks['Classic']['AllowIpAddress']))
                if networks['Classic'].get('AllowIpAddressEgress'):
                    print('     |--AllowIpAddressEgress: %s' % ','.join(networks['Classic']['AllowIpAddressEgress']))
                if networks['Classic'].get('AllowSecurityGroup'):
                    print('     |--AllowSecurityGroup: %s' % ','.join(networks['Classic']['AllowSecurityGroup']))
                if networks['Classic'].get('AllowSecurityGroupEgress'):
                    print('     |--AllowSecurityGroupEgress: %s' % ','.join(networks['Classic']['AllowSecurityGroupEgress']))

            # vpc
            if networks.get('VPC'):
                print('  |--VPC:')
                for (k, v) in networks.get('VPC').items():
                    if v:
                        print('     |--%s : %s' % (k, v))

        print('')


        # groups
        groups = []
        total_desired_vm_count = 0
        for groupName in cluster_info.Groups:
            v = formatter.to_dict(cluster_info.Groups[groupName])
            v['Name'] = groupName
            v['VMCount'] = '%s / %s' % (v['ActualVMCount'], v['DesiredVMCount'])
            ins = get_ins_type_map().get(v['InstanceType'])
            if ins:
                v['InstanceType/cpu/mem'] = '%s, %sCores, %sGB' % (v['InstanceType'], ins['cpu'], ins['memory'])
            else:
                v['InstanceType/cpu/mem'] = v['InstanceType']
            groups.append(v)
            total_desired_vm_count = total_desired_vm_count + v['DesiredVMCount']



        # metric
        print('%s' % bold(magenta('Worker status:')))
        metrics = formatter.to_dict(cluster_info.get('Metrics'))
        metrics['UnallocatedCount'] = total_desired_vm_count - metrics['StartingCount'] - metrics['RunningCount'] - \
                                      metrics['StoppingCount'] - metrics['StoppedCount']
        cols = [('Starting', blue), ('Running', green), ('Stopping', yellow), ('Stopped', red), ('Unallocated', white)]
        t = []
        p = []

        for k in cols:
            t.append((('  %s: %s' % (k[1](k[0]), metrics.get('%sCount' % k[0])))))
            plen = metrics.get('%sCount' % k[0]) * PROGRESS_LEN / total_desired_vm_count
            plen = int(plen)
            p.append(str(k[1]('=' * plen)) if plen > 0 else '')
        print('  '.join(t))

        # metric progress
        print(' | %s |' % (''.join(p)))



        ### ip list
        print('%s' % bold(magenta('Worker list:')))
        result = batchcompute_client.list_cluster_instances(cluster_id, 'default')

        arr = formatter.items2arr(result.get('Items'))
        arr = formatter.format_date_in_arr(arr, ['CreationTime', 'StartTime', 'EndTime'])


        list2table.print_table(arr, ['Id','IpAddress', ('State', 'State', formatter.get_job_state), 'CreationTime','Hint'], False)

        if log:
            # OperationLogs
            print('%s:\n  %s' % (bold(magenta('Operation Logs')), '\n  '.join(cluster_info.get('OperationLogs'))))
        print('')
    else:
        print('%s' % bold(magenta('Workers:')))
        print(yellow('  Not found worker cluster, type "bcc start -h" for more\n'))



def resize(nodes):
    obj = bccluster_json.get_required_login()
    cluster_id = obj.get('cluster_id')

    try:
        nodes = int(nodes)
    except:
        raise Exception('nodes should be an integer')

    if not cluster_id:
        raise Exception('Not found cluster_id, you should start cluster first')

    batchcompute_client.update_cluster_vm_count(cluster_id,'default',nodes)

    print(green('\n  resize success\n'))


def stop():
    obj = bccluster_json.get_required_login()
    cluster_id = obj.get('cluster_id')

    if not cluster_id:
        raise Exception('Not found cluster_id, you should start cluster first')

    try:
        if confirm("This action will release all worker machines, Are you sure", default=False):
            batchcompute_client.delete_cluster(cluster_id)

            del obj['cluster_id']
            bccluster_json.save(obj)
            print(green('\n  stop success\n'))


    except ClientError as e:
        dstack()
        if e.code!='InvalidResource.NotFound' and e.code !='StateConflict':
            raise e
    except KeyboardInterrupt:
        print('')
        return







##################################################


def get_ins_type_map():
    arr = batchcompute_client.list_instance_types()
    m = {}
    for item in arr:
        m[item['name']] = item
    return m


def trans_nodes(n):
    try:
        n = int(n)
        return n if n >= 0 else 1
    except:
        return 1


def trans_mount(s):
    if not s:
        return None
    arr = s.split(',')
    mount = {}
    for item in arr:
        item = item.strip()
        if item.startswith('oss://') or item.startswith('nas://'):
            ind = item.rfind(':')
            k = item[0:ind]
            v = item[ind+1:]
        else:
            [k,v]=item.split(':',1)

        if len(v)==1 and str.isalpha(v):
            v = v + ':'
        mount[k]=v
    return mount


def extend_mount(desc, mount_m):
    desc['Configs']['Mounts']['Entries'] = []
    for k, v in mount_m.items():
        if k.startswith('oss://') or k.startswith('nas://'):
            desc['Configs']['Mounts']['Entries'].append({
                "Destination": v,
                "Source": k,
                "WriteSupport": k.endswith('/')
            })




def trans_disk(disk):

    try:
        infos = disk.split(',')

        result = {}

        for info in infos:
            info = info.strip()
            if info.startswith('system:'):
                (name, type, size) = info.split(':')
                type = type.strip()
                result['SystemDisk'] = {
                    'Type': '' if type=='default' else type, 'Size': int(size)
                }
            elif info.startswith('data:'):
                (name, type2, size2, mount_point) = info.split(':')
                type2 = type2.strip()
                result['DataDisk'] = {
                    'Type': '' if type2=='default' else type2, 'Size': int(size2), 'MountPoint': mount_point.strip()
                }
            else:
                raise Exception('Invalid disk format')

        return result

    except BaseException as e:
        raise Exception(
            'Invalid disk format, it should like this: --disk system:ephemeral:40,data:cloud:500:/home/disk, append -h for more')

