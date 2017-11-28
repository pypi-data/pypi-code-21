# -*- coding: utf-8 -*-
from terminal import red
from .externals.command import Command

from . import const,i18n_util
from .action import cluster,cluster_create,cluster_delete,cluster_update


COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()


def update():
    # update cluster
    cmd_update_cluster = Command('update_cluster', alias=['uc'],
                                 arguments=['clusterId', 'groupName'],
                                 description=MSG['update_cluster']['description'],
                                 usage='''Usage: %s update_cluster|uc <clusterId> [groupName] [option]

          Examples:

              1. %s uc cls-idxxx1 group -n 2   # update cluster set group.DesiredVMCount=2
              2. %s uc cls-idxxx1 -n 2         # ignore group name when it is 'group' ''' % (COMMAND, CMD, CMD),
                                 func=cluster_update.update)
    cmd_update_cluster.option("-y, --yes", MSG['update_cluster']['option']['yes'])
    cmd_update_cluster.option("-n, --nodes [desiredVMCount]", MSG['update_cluster']['option']['nodes'],
                              resolve=cluster_update.trans_nodes)

    cmd_update_cluster.option("-m, --mount [kv_pairs]", MSG['update_cluster']['option']['mount'],
                              resolve=cluster_create.trans_mount)
    cmd_update_cluster.option("-i, --image [imageId]", MSG['update_cluster']['option']['image'],
                              resolve=cluster_update.trans_image)
    cmd_update_cluster.option("-u, --user_data [kv_pairs]",
                              MSG['update_cluster']['option']['user_data'],
                              resolve=cluster_update.trans_user_data)
    cmd_update_cluster.option("-e, --env [kv_pairs]", MSG['update_cluster']['option']['env'],
                              resolve=cluster_update.trans_env)
    cmd_update_cluster.option("--spot_price_limit [spot_price_limit]",
                              MSG['update_cluster']['option']['spot_price_limit'])
    cmd_update_cluster.option("--show_json",
                              MSG['update_cluster']['option']['show_json'])
    return cmd_update_cluster

def delete():
    # delete cluster
    cmd_del_cluster = Command('delete_cluster', alias=['dc'],
                              arguments=['clusterId'],
                              description=MSG['delete_cluster']['description'],
                              usage='''Usage: %s delete_cluster|dc [clusterId,clusterId2,clusterId3...] [option]

    Examples:

        1. %s dc cls-idxxx1                # delete cluster with clusterId
        2. %s dc cls-idxxx1,cls-idxxx2 -y  # delete clusters in silent mode''' % (COMMAND, CMD, CMD),
                              func=cluster_delete.del_cluster)
    cmd_del_cluster.option("-y, --yes", MSG['delete_cluster']['option']['yes'])
    return cmd_del_cluster

def create():
    # create cluster
    cmd_create_cluster = Command('create_cluster', alias=['cc'],
                                 description=MSG['create_cluster']['description'],
                                 arguments=['clusterName'],
                                 usage='''Usage: %s create_cluster|cc [option] <clusterName>

    Examples:

        1. %s cc cluster1
        2. %s cc cluster2 -n 3
        3. %s cc cluster2 -i %s -t %s -n 1 -d 'this is description' -u key1:value1,k2:v2
        4. %s cc cluster3 --notification_topic my-mns-topic --notification_events OnClusterDeleted,OnInstanceActive --notification_endpoint <your_mns_endpoint>    # set notification
        5. %s cc cluster4 --resource_type Spot  # creating with spot resource type''' % (
                                     COMMAND, CMD, CMD, CMD, IMG_ID, INS_TYPE, CMD, CMD),
                                 spliter=' ',
                                 # spliter='\n    -----%s----------------' % blue('create, update, delete'),
                                 func=cluster_create.create_cluster)
    cmd_create_cluster.option("-i, --image [imageId]", MSG['create_cluster']['option']['image'],
                              resolve=cluster_create.trans_image)
    cmd_create_cluster.option("-t, --type [instanceType]", MSG['create_cluster']['option']['type'])
    cmd_create_cluster.option("-n, --nodes [instanceCount]", MSG['create_cluster']['option']['nodes'],
                              resolve=cluster_create.trans_nodes)
    cmd_create_cluster.option("-d, --description [description]",
                              MSG['create_cluster']['option']['description'])
    cmd_create_cluster.option("-u, --user_data [kv_pairs]",
                              MSG['create_cluster']['option']['user_data'],
                              resolve=cluster_create.trans_user_data)

    cmd_create_cluster.option("-e, --env [kv_pairs]", MSG['create_cluster']['option']['env'],
                              resolve=cluster_create.trans_env)
    cmd_create_cluster.option("--disk [disk_configs]",
                              MSG['create_cluster']['option']['disk'],
                              resolve=cluster_create.trans_disk)

    cmd_create_cluster.option("--resource_type [resource_type]",
                              MSG['create_cluster']['option']['resource_type'])

    cmd_create_cluster.option("--spot_price_limit [spot_price_limit]",
                              MSG['create_cluster']['option']['spot_price_limit'])

    cmd_create_cluster.option("-m, --mount [kv_pairs]",
                              '(%s) %s' % (red(MSG['changed']), MSG['create_cluster']['option']['mount']),
                              resolve=cluster_create.trans_mount)
    cmd_create_cluster.option("--nas_access_group [nas_access_group]",
                              MSG['create_cluster']['option']['nas_access_group'])
    cmd_create_cluster.option("--nas_file_system [nas_file_system]", MSG['create_cluster']['option']['nas_file_system'])

    cmd_create_cluster.option("--notification_endpoint [mns_endpoint]",
                              MSG['create_cluster']['option']['notification_endpoint'])
    cmd_create_cluster.option("--notification_topic [mns_topic]", MSG['create_cluster']['option']['notification_topic'])
    cmd_create_cluster.option("--notification_events [cluster_events]",
                              MSG['create_cluster']['option']['notification_events'],
                              resolve=cluster_create.trans_notification_events)
    cmd_create_cluster.option("--no_cache_support",
                              MSG['create_cluster']['option']['no_cache_support'])

    cmd_create_cluster.option("--vpc_cidr_block [vpc_cidr_block]",
                              MSG['create_cluster']['option']['vpc_cidr_block'])
    cmd_create_cluster.option("--vpc_id [vpc_id]",
                              MSG['create_cluster']['option']['vpc_id'])
    cmd_create_cluster.option("-f, --filePath [filePath]", MSG['create_cluster']['option']['filePath'],
                              visible=IS_GOD)
    cmd_create_cluster.option("--show_json",
                              MSG['create_cluster']['option']['show_json'])

    return cmd_create_cluster

def clusters():
    cmd_clusters = Command('cluster', alias=['c'],
                           arguments=['clusterId'],
                           description=MSG['cluster']['description'],
                           usage='''Usage: %s cluster|c [clusterId|No.] [option]

    Examples:

        list cluster:
          1. %s c

        get cluster info:
          1. %s c cls-6ki4fsea5ldlvsupbrk01q
          2. %s c 1
          3. %s c 1 -l''' % (COMMAND, CMD, CMD, CMD, CMD),
                           func=cluster.all)
    cmd_clusters.option('-d,--description', MSG['cluster']['option']['description'])
    cmd_clusters.option('-l,--log', MSG['cluster']['option']['oplog'])
    cmd_clusters.option('--show_json', MSG['cluster']['option']['show_json'], visible=IS_GOD)

    return cmd_clusters

