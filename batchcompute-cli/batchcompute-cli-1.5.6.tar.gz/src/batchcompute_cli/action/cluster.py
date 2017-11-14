# -*- coding:utf-8 -*-

from ..util import client, formater, list2table, result_cache
from terminal import bold, magenta, white, blue, green,red, yellow
from ..const import CMD
from batchcompute.utils.jsonizable import BatchEncoder
import json

PROGRESS_LEN = 70

def all(clusterId=None, description=False, log=False, show_json=False):
    if clusterId:
        get(clusterId, description, log, show_json)
    else:
        list(show_json)


def list(show_json=False):

    result = client.list_clusters()

    if show_json:
        print(json.dumps(result, indent=2, cls=BatchEncoder))
        return

    arr = formater.items2arr(result.get('Items'))

    result_len = len(arr)

    arr = formater.format_date_in_arr(arr, ['CreationTime'])

    # sort
    arr = sort_cluster_list(arr)

    for item in arr:
        total =0
        actual_count = 0
        for k in item['Groups']:
            g = item['Groups'][k]
            actual_count += g['ActualVMCount']
            total += g['DesiredVMCount']
        item['Counts'] = '%s / %s' % (actual_count,total)
        #item['Description'] =  formater.sub(item['Description'],10)


    result_cache.save(arr, 'Id', 'clusters')

    #print(white('RequestId: %s' % result.get('RequestId')))
    print('%s' % bold(magenta('Clusters:')))
    list2table.print_table(arr,['Id','Name',('State','State', formater.get_cluster_state),'Counts','CreationTime',('CreationTimeFromNow','FromNow')])

    arrlen = len(arr)
    cache_str =white('(cache %s %s)' %  (arrlen, 'rows' if arrlen>1 else 'row' ) )
    print('%s %s' % ( green('Total: %s' % result_len), cache_str))


    print(white('\n  type "%s c <Id|No.>" to show cluster detail\n' % (CMD)))

def get(clusterId, descOnly=False, oplog=False, show_json=False):
    clusterId = result_cache.get(clusterId, 'clusters')

    print(white('exec: bcs c %s' % clusterId))
    result = client.get_cluster(clusterId)

    if show_json:
        print(result)
        return

    if descOnly:
        print(result)
        return

    arr = [{
        'a': '%s: %s' % (blue('Id'), result.get('Id')),
        'b': '%s: %s' % (blue('Name'), result.get('Name')),
        'c': '%s: %s' % (blue('State'), formater.get_cluster_state(result.get('State')))
    },{
        'a': '%s: %s' % (blue('ImageId'), result.get('ImageId')),
        #'b': '%s: %s' % (blue('InstanceType'),  result.get('InstanceType')),
        'c': '',
        'b': '%s: %s' % (blue('Created'), formater.from_now(result.get('CreationTime')))
    }]
    print('%s' % bold(magenta('Cluster:')))
    list2table.print_table(arr, ['a','b','c'], show_no=False, show_header=False)

    # disks
    disks = result.Configs.Disks
    print(blue('Disks:'))
    if disks.get('SystemDisk'):
        print('  |--System Disk: %s (%s) %sGB' % ('/', blue(disks['SystemDisk']['Type']), disks['SystemDisk']['Size']) )
    if disks.get('DataDisk') and disks['DataDisk'].get('MountPoint'):
        print('  |--Data Disk: %s (%s) %sGB' % (disks['DataDisk']['MountPoint'], blue(disks['DataDisk']['Type']), disks['DataDisk']['Size'] ))
    print('')

    # mounts
    mounts = result.Configs.Mounts
    print('%s (Locale: %s , Lock: %s , CacheSupport: %s)' % (blue('Mounts:'), mounts.get('Locale'), mounts.get('Lock'), mounts.get('CacheSupport')))


    entries = mounts.get('Entries')
    if entries:
        for ent in entries:
           print('  |--%s %s %s' % (ent['Destination'], blue('<-'), green(ent['Source'])))

    nas  = mounts.get('  Nas')
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
    networks = result.Configs.Networks
    if networks:
        print('  |--Classic:')
        if networks.get('Classic'):
            if networks['Classic'].get('AllowIpAddress'):
                print('     AllowIpAddress: %s' % ','.join(networks['Classic']['AllowIpAddress']))
            if networks['Classic'].get('AllowIpAddressEgress'):
                print('     AllowIpAddressEgress: %s' % ','.join(networks['Classic']['AllowIpAddressEgress']))
            if networks['Classic'].get('AllowSecurityGroup'):
                print('     AllowSecurityGroup: %s' % ','.join(networks['Classic']['AllowSecurityGroup']))
            if networks['Classic'].get('AllowSecurityGroupEgress'):
                print('     AllowSecurityGroupEgress: %s' % ','.join(networks['Classic']['AllowSecurityGroupEgress']))

        # vpc
        if networks.get('VPC'):
            print('  |--VPC:')
            for (k, v) in networks.get('VPC').items():
                if v:
                    print('     %s : %s' % (k, v))

    print('')

    # notification
    if result.get('Notification').get('Topic').get('Events'):
        print('%s' % (blue('Notification Topic')))
        print('  %s: %s' % (blue('Endpoint'), result.get('Notification').get('Topic').get('Endpoint')))
        print('  %s: %s' % (blue('Name'), result.get('Notification').get('Topic').get('Name')))
        print('  %s: %s' % (blue('Events'), ','.join(result.get('Notification').get('Topic').get('Events'))))


    # description
    if result.get('Description'):
        print('%s: %s' % (blue('Description'), result.get('Description')))


    # groups
    groups = []
    total_desired_vm_count = 0
    for groupName in result.Groups:
        v = formater.to_dict(result.Groups[groupName])
        v['Name'] = groupName
        v['VMCount'] = '%s / %s' % (v['ActualVMCount'],v['DesiredVMCount'])
        ins = client.get_ins_type_map().get(v['InstanceType'])
        if ins:
            v['InstanceType/cpu/mem'] = '%s, %sCores, %sGB' % (v['InstanceType'], ins['cpu'], ins['memory'])
        else:
            v['InstanceType/cpu/mem'] = v['InstanceType']

        if v.get('Disks'):
            if v['Disks'].get('SystemDisk'):
                v['SystemDisk'] = '%s:%sGB' %(v['Disks']['SystemDisk']['Type'], str(v['Disks']['SystemDisk']['Size']) )
            else:
                v['SystemDisk'] = ''
            if v['Disks'].get('DataDisk'):
                v['DataDisk'] = '%s:%sGB:%s' %( v['Disks']['DataDisk']['Type'] , v['Disks']['DataDisk']['Size'], v['Disks']['DataDisk']['MountPoint'])
            else:
                v['DataDisk'] = ''
        else:
            v['SystemDisk'] = ''
            v['DataDisk'] = ''

        priceLimit = v.get('SpotPriceLimit') or 0
        if v['ResourceType']=='Spot' and priceLimit > 0:
            v['ResourceType/SpotPrice'] = '%s, <=%s' % (v['ResourceType'], priceLimit)
        else:
            v['ResourceType/SpotPrice'] = v['ResourceType']

        groups.append(v)
        total_desired_vm_count = total_desired_vm_count + v['DesiredVMCount']


    result_cache.save(groups, 'Name', 'groups')


    # metric
    print(blue('Metrics:'))
    metrics = formater.to_dict(result.get('Metrics'))
    metrics['UnallocatedCount'] = total_desired_vm_count - metrics['StartingCount'] - metrics['RunningCount'] - metrics['StoppingCount'] - metrics['StoppedCount']
    cols = [('Starting',blue), ('Running',green), ('Stopping',yellow), ('Stopped',red),('Unallocated',white)]
    t = []
    p = []

    for k in cols:
        t.append( (('  %s: %s' % (k[1](k[0]), metrics.get('%sCount' % k[0])) )) )
        if total_desired_vm_count != 0:
            plen =  metrics.get('%sCount' % k[0]) * PROGRESS_LEN/total_desired_vm_count
        else:
            plen = 0
        plen = int(plen)
        p.append(  str(k[1]('=' * plen)) if plen>0 else '' )
    print('  '.join(t))


    # metric progress
    print(' | %s |' % (''.join(p)) )

    # user data
    ud = result.get('UserData')
    if ud:
        print('%s' % (blue('User Data:')))
        for (k,v) in ud.items():
            print('  %s : %s' % (k,v))

    # env vars
    env = result.get('EnvVars')
    if env:
        print('%s' % (blue('Env Vars:')))
        for (k, v) in env.items():
            print('  %s : %s' % (k, v))


    # print groups
    print('%s' % bold(magenta('Groups:')))
    list2table.print_table(groups, ['Name','VMCount','InstanceType/cpu/mem', ('ResourceType/SpotPrice','ResourceType/PriceLimit' if priceLimit>0 else 'ResourceType'),'SystemDisk', 'DataDisk'])

    # OperationLogs
    if oplog:
       print('%s:\n  %s' % (blue('Operation Logs'), '\n  '.join(result.get('OperationLogs'))))


    #print(result)

def sort_cluster_list(arr):
    others_arr = []
    deleting_arr = []

    for n in arr:
        if n['State'] == 'Deleting':
            deleting_arr.append(n)
        else:
            others_arr.append(n)

    deleting_arr = formater.order_by(deleting_arr, ['CreationTime'], True)
    others_arr = formater.order_by(others_arr, ['CreationTime'], True)

    return deleting_arr + others_arr

