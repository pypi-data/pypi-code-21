
# -*- coding:utf-8 -*-

from ..util import client,config, formater, oss_client,util,dag
from terminal import green
import json
import os
import uuid
import tarfile
from ..const import CMD,EVENTS


try:
    import ConfigParser
except:
    import configparser as ConfigParser


DEFAULT='DEFAULT'
TIMEOUT=86400

def submit(cmd=None, job_name=None, description=None, cluster=None, timeout=None, nodes=None,
           force=False, auto_release=False, docker=None, pack=None, env=None, read_mount=None, write_mount=None, mount=None,
           file=None, user_data=None, priority=None, image=None,type=None, disk=None, lock=False, locale=None,
           reserve_on_fail=False,
           no_cache_support=False,
           notification_endpoint=None, notification_topic=None, notification_events=None,
           resource_type=None,
           nas_access_group=None,
           nas_file_system=None,
           spot_price_limit=None,
            vpc_cidr_block = None,
            vpc_id=None,
           show_json=False,show_dag=False):

    if cmd == None and file == None  or cmd!=None and cmd.startswith('-'):
        print('\n  type "%s sub -h" for more\n' % CMD)
        return

    # compatible timeout
    if str.isdigit(type or ''):
        timeout = int(type)
        type = None

    job_desc = trans_file_to_job_desc(file, not show_json and not show_dag)

    opt = {
        'cmd': cmd,
        'job_name': job_name,
        'description': description,
        'cluster': cluster,
        'disk': disk,
        'user_data': user_data,
        'timeout': timeout,
        'nodes' : nodes,
        'force': force,
        'auto_release': auto_release,
        'reserve_on_fail': reserve_on_fail,
        'no_cache_support': no_cache_support,
        'lock': lock,
        'locale': locale,

        'image': image,
        'type': type,

        'resource_type': resource_type,



        'priority': priority,

        'docker': docker,
        'pack': pack,
        'env': env,

        'read_mount': read_mount,
        'write_mount': write_mount,
        'mount': mount,

        'notification_endpoint': notification_endpoint,
        'notification_topic': notification_topic,
        'notification_events': notification_events,

        'nas_access_group': nas_access_group,
        'nas_file_system': nas_file_system,

        'vpc_id': vpc_id,
        'vpc_cidr_block': vpc_cidr_block if vpc_cidr_block else config.getConfigs(config.COMMON, ['vpc_cidr_block']).get('vpc_cidr_block'),
        'spot_price_limit': spot_price_limit

    }


    job_desc = fix_by_opt(job_desc, opt, not show_json and show_dag)


    deal_with_pack(job_desc, show_json or show_dag)



    tasks = job_desc['DAG']['Tasks']
    for (taskName,task) in tasks.items():
        if  task.get('AutoCluster') \
                and task['AutoCluster'].get('Configs') \
                and task['AutoCluster']['Configs'].get('Networks') \
                and task['AutoCluster']['Configs']['Networks'].get('VPC') \
                and task['AutoCluster']['Configs']['Networks']['VPC'].get('VpcId'):
            if not task['AutoCluster']['Configs']['Networks']['VPC'].get('CidrBlock'):
               raise Exception('vpc_id must works with vpc_cidr_block, taskName=%s' % taskName)



    if show_dag:
        # calc deps
        deps = util.get_task_deps(job_desc.get('DAG'))
        matric = dag.sortIndex(deps)

        # dag
        dag.draw(deps, matric)

    elif show_json:
        print(json.dumps(job_desc, indent=4))
    else:
        result = client.create_job(job_desc)

        if result.StatusCode==201:
            print(green('Job created: %s' % result.Id))

def deal_with_pack(desc, show_json):
    pre_oss_path = config.get_oss_path()
    rand = gen_rand_id()

    tasks = desc['DAG']['Tasks']

    m = {}
    for (task_name,task_desc) in tasks.items():
        task_desc['Parameters']['StdoutRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)
        task_desc['Parameters']['StderrRedirectPath'] = '%s%s/logs/' % (pre_oss_path,rand)

        pack = task_desc.get('pack')

        if pack:

            if not m.get(pack):
                if not m:
                    package_path = '%s%s/worker.tar.gz' % (pre_oss_path, rand)
                else:
                    package_path = '%s%s/worker_%s.tar.gz' % (pre_oss_path, rand, task_name)
                m[pack] = package_path

                # pack upload
                if not show_json:
                    pack_upload(pack, package_path)


            task_desc['Parameters']["Command"]['PackagePath'] = m[pack]
            del task_desc['pack']
        else:
            task_desc['Parameters']["Command"]['PackagePath'] = ''



    return desc


def pack_upload(pack, package_path):

    if ',' in pack:
        print('packing multi-files..')
        arr = pack.split(',')
        build_tar_from_arr_and_upload(arr, package_path)
    else:
        folder_path = formater.get_abs_path(pack)
        if os.path.isdir(folder_path):
            print('packing folder..')
            build_tar_from_dir_and_upload(folder_path, package_path)
        else:
            print('packing a single file..')
            build_tar_from_arr_and_upload([pack],package_path)

def fix_by_opt(desc, opt, check_cluster):

    if opt.get('job_name'):
        desc['Name'] = opt['job_name']
    if opt.get('description'):
        desc['Description'] = opt['description']
    if opt.get('priority'):
        desc['Priority'] = trans_priority(opt['priority'])
    if opt.get('force'):
        desc['JobFailOnInstanceFail'] = not opt['force']
    if opt.get('auto_release'):
        desc['AutoRelease'] = opt['auto_release']

    # notification
    if opt.get('notification_endpoint'):
        desc['Notification']['Topic']['Endpoint'] = opt['notification_endpoint']
    if opt.get('notification_topic'):
        desc['Notification']['Topic']['Name'] = opt['notification_topic']
    if opt.get('notification_events'):
        desc['Notification']['Topic']['Events'] = opt['notification_events']

    tasks = desc['DAG']['Tasks']


    for (task_name,task_desc) in tasks.items():

        if opt.get('cmd'):
            task_desc['Parameters']['Command']['CommandLine']=opt['cmd']

        if not task_desc['Parameters']['Command'].get('CommandLine'):
            raise Exception('Missing required option: cmd')


        if opt.get('timeout'):
            task_desc['Timeout'] = trans_timeout(opt['timeout'])
        if opt.get('nodes'):
            task_desc['InstanceCount'] = trans_nodes(opt['nodes'])

        cluster_id = ''

        if opt.get('cluster'):

            cluster_info = trans_cluster(opt['cluster'],opt['image'],opt['type'],check_cluster)

            cluster_id =  cluster_info.get('ClusterId')

            if cluster_id and cluster_id!='':

                # clusterId
                task_desc['ClusterId'] = cluster_info.get('ClusterId')
                task_desc['AutoCluster']={}
            else:
                # auto cluster
                extend(task_desc['AutoCluster'], cluster_info['AutoCluster'])



        #extend(task_desc, trans_cluster(opt['cluster'],opt['image'],opt['type'],check_cluster))

        else:
            if opt.get('image'):
                task_desc['AutoCluster']['ImageId'] = opt.get('image')
            if opt.get('type'):
                task_desc['AutoCluster']['InstanceType'] = opt.get('type')


        cluster_id = cluster_id or task_desc['ClusterId']


        if not cluster_id or cluster_id=='':

            if opt.get('resource_type'):
                task_desc['AutoCluster']['ResourceType'] = opt.get('resource_type')
            if not task_desc['AutoCluster'].get('ResourceType'):
                task_desc['AutoCluster']['ResourceType'] = 'OnDemand'

            # spot price limit
            if opt.get('spot_price_limit'):
                spot_price_limit = opt.get('spot_price_limit')

                if spot_price_limit is not None:
                    spot_price_limit = float(spot_price_limit)
                    if not task_desc['AutoCluster'].get('ResourceType') == 'Spot':
                        raise Exception('spot_price_limit works only if resource_type is Spot')

                    if spot_price_limit > 0:
                        task_desc['AutoCluster']['SpotPriceLimit'] = spot_price_limit
                        task_desc['AutoCluster']['SpotStrategy'] = 'SpotWithPriceLimit'
                    else:
                        task_desc['AutoCluster']['SpotStrategy'] = 'SpotAsPriceGo'

            if opt.get('user_data'):
                user_data_m = trans_user_data(opt['user_data'])
                if not task_desc['AutoCluster'].get('UserData'):
                    task_desc['AutoCluster']['UserData'] = {}
                extend(task_desc['AutoCluster']['UserData'], user_data_m)

            if opt.get('disk') and task_desc.get('AutoCluster'):
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs']={}
                task_desc['AutoCluster']['Configs']['Disks'] = opt['disk']

            if opt.get('reserve_on_fail'):
                task_desc['AutoCluster']['ReserveOnFail'] = opt.get('reserve_on_fail')



            # vpc
            if opt.get('vpc_cidr_block') :
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs'] = {}
                if not task_desc['AutoCluster']['Configs'].get('Networks'):
                    task_desc['AutoCluster']['Configs']['Networks'] = {}
                if not task_desc['AutoCluster']['Configs']['Networks'].get('VPC'):
                    task_desc['AutoCluster']['Configs']['Networks']['VPC'] = {}
                task_desc['AutoCluster']['Configs']['Networks']['VPC']['CidrBlock'] = opt.get('vpc_cidr_block')
            if opt.get('vpc_id') :
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs'] = {}
                if not task_desc['AutoCluster']['Configs'].get('Networks'):
                    task_desc['AutoCluster']['Configs']['Networks'] = {}
                if not task_desc['AutoCluster']['Configs']['Networks'].get('VPC'):
                    task_desc['AutoCluster']['Configs']['Networks']['VPC'] = {}
                task_desc['AutoCluster']['Configs']['Networks']['VPC']['VpcId'] = opt.get('vpc_id')

        # mounts
        if opt.get('no_cache_support'):
            task_desc['Mounts']['CacheSupport'] = not opt.get('no_cache_support')

        if opt.get('nas_access_group'):
            if not task_desc.get('Mounts'):
                task_desc['Mounts'] = {}
            if not task_desc['Mounts'].get('NAS'):
                task_desc['Mounts']['NAS'] = {}
            task_desc['Mounts']['NAS']['AccessGroup'] = opt.get('nas_access_group').split(',')

        if opt.get('nas_file_system'):
            if not task_desc.get('Mounts'):
                task_desc['Mounts'] = {}
            if not task_desc['Mounts'].get('NAS'):
                task_desc['Mounts']['NAS'] = {}
            task_desc['Mounts']['NAS']['FileSystem'] = opt.get('nas_file_system').split(',')

        if opt.get('docker'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(opt['docker']))
        if opt.get('env'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(opt['env']))



        if opt.get('mount'):
            extend_mount(task_desc, trans_mount(opt['mount']))
        if opt.get('read_mount'):
            extend_mount(task_desc, trans_mount(opt['read_mount']))



        if opt.get('write_mount'):
            extend(task_desc['OutputMapping'], reverse_kv(trans_mount(opt['write_mount'])))

        if opt.get('lock'):
            task_desc['Parameters']['InputMappingConfig']['Lock'] = opt['lock']
        if opt.get('locale'):
            task_desc['Parameters']['InputMappingConfig']['Locale'] = opt['locale']


        # cache
        if opt.get('pack'):
            task_desc['pack'] = opt['pack']

    return desc



########################################
def get_mount_map(mounts):
    m = {}
    if mounts.get('Entries'):
      for n in mounts['Entries']:
        m[n['Source']]=n['Destination']
    return m

def extend_mount(desc, mount_m):
    if not desc['Mounts'].get('Entries'):
        desc['Mounts']['Entries'] = []

    # 去重
    i = 0
    for n in desc['Mounts']['Entries']:
        if mount_m.get(n['Source']):
            del desc['Mounts']['Entries'][i]
            i=i-1
        i += 1

    ####################################################
    for k,v in mount_m.items():
        if k.startswith('oss://') or k.startswith('nas://'):
            desc['Mounts']['Entries'].append({
                "Destination": v,
                "Source": k,
                "WriteSupport": k.endswith('/')
            })

def trans_file_to_job_desc(file, check_cluster):
    cf = ConfigParser.ConfigParser()
    # parse file
    if not file:
        desc = gen_job_desc()
        desc['DAG']['Tasks']['task'] = gen_task_desc()
        return desc


    # else
    cfg_path = os.path.join(os.getcwd(), file)
    if not os.path.exists(cfg_path):
        raise Exception('Invalid file: %s' % cfg_path)
    cf.read(cfg_path)

    # vars starts with $
    fit_vars(cf)


    desc = gen_job_desc()

    default_options = cf.defaults()

    if default_options:
        if default_options.get('job_name'):
            desc['Name'] = default_options['job_name']
        if default_options.get('description'):
            desc['Description'] = default_options['description']
        if default_options.get('priority'):
            desc['Priority'] = trans_priority(default_options['priority'])
        if default_options.get('force'):
            desc['JobFailOnInstanceFail'] = not cf.getboolean(DEFAULT,'force')
        if default_options.get('auto_release'):
            desc['AutoRelease'] = cf.getboolean(DEFAULT, 'auto_release')

        if default_options.get('deps'):
            desc['DAG']['Dependencies'] = trans_deps(cf.get(DEFAULT,'deps'))

        if default_options.get('notification_endpoint'):
            desc['Notification']['Topic']['Endpoint'] = default_options['notification_endpoint']
        if default_options.get('notification_topic'):
            desc['Notification']['Topic']['Name'] = default_options['notification_topic']
        if default_options.get('notification_events'):
            desc['Notification']['Topic']['Events'] = trans_notification_events(default_options['notification_events'])

    # without DEFAULT
    secs = cf.sections()

    for sec in secs:
        task_desc = gen_task_desc()


        # fix job fields in old version
        #################################
        if cf.has_option(sec,'job_name'):
            desc['Name'] = cf.get(sec,'job_name')
        if cf.has_option(sec,'description'):
            desc['Description'] = cf.get(sec,'description')
        if cf.has_option(sec,'priority'):
            desc['Priority'] = trans_priority(cf.get(sec,'priority'))
        if cf.has_option(sec,'force'):
            desc['JobFailOnInstanceFail'] = not cf.getboolean(sec,'force')
        if cf.has_option(sec, 'auto_release'):
            desc['AutoRelease'] = cf.getboolean(sec, 'auto_release')

        if cf.has_option(sec, 'notification_endpoint'):
            desc['Notification']['Topic']['Endpoint'] = cf.get(sec,'notification_endpoint')
        if cf.has_option(sec, 'notification_topic'):
            desc['Notification']['Topic']['Name'] = cf.get(sec,'notification_topic')
        if cf.has_option(sec, 'notification_events'):
            desc['Notification']['Topic']['Events'] = trans_notification_events(cf.get(sec,'notification_events'))

        #################################

        ## extend by default options
        if default_options:
            ####################################
            if cf.has_option(DEFAULT,'env'):
                extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(cf.get(DEFAULT,'env')))
            if cf.has_option(DEFAULT,'docker'):
                extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(cf.get(DEFAULT,'docker')))



            if cf.has_option(DEFAULT,'mount'):
                extend_mount(task_desc , trans_mount(cf.get(DEFAULT,'mount')))
            if cf.has_option(DEFAULT,'read_mount'):
                extend_mount(task_desc, trans_mount(cf.get(DEFAULT,'read_mount')))





            if cf.has_option(DEFAULT,'write_mount'):
                w_mount_m = trans_mount(cf.get(DEFAULT,'write_mount'))
                extend(task_desc['OutputMapping'], reverse_kv(w_mount_m))

            if cf.has_option(DEFAULT, 'user_data'):
                user_data_m = trans_user_data(cf.get(DEFAULT, 'user_data'))
                if not task_desc['AutoCluster'].get('UserData'):
                    task_desc['AutoCluster']['UserData'] = {}
                extend(task_desc['AutoCluster']['UserData'], user_data_m)


            if cf.has_option(DEFAULT, 'reserve_on_fail'):
                task_desc['AutoCluster']['ReserveOnFail']=cf.getboolean(DEFAULT, 'reserve_on_fail')

            if cf.has_option(DEFAULT, 'no_cache_support'):
                task_desc['Mounts']['CacheSupport'] = not cf.getboolean(DEFAULT, 'no_cache_support')
        ###################################




        if cf.has_option(sec, "cmd"):
            task_desc['Parameters']['Command']['CommandLine']= cf.get(sec,'cmd')
        # else:
        #     raise Exception('Missing required option: cmd')


        # cache
        if cf.has_option(DEFAULT, "pack"):
            task_desc['pack']=  cf.get(DEFAULT,'pack')
        if cf.has_option(sec, "pack"):
            task_desc['pack']=  cf.get(sec,'pack')

        if cf.has_option(sec, "timeout"):
            task_desc['Timeout']= trans_timeout(cf.getint(sec,'timeout'))
        if cf.has_option(sec,'nodes'):
            task_desc['InstanceCount']=trans_nodes(cf.getint(sec,'nodes'))

        cluster_id=''
        if cf.has_option(sec,'cluster'):
            img = cf.get(sec, 'image') if cf.has_option(sec,'image') else None
            tp = cf.get(sec, 'type') if cf.has_option(sec,'type') else None

            cluster_info = trans_cluster(cf.get(sec,'cluster'), img , tp, check_cluster)

            cluster_id = cluster_info.get('ClusterId')

            if cluster_id and cluster_id!='':
                task_desc['ClusterId'] = cluster_info.get('ClusterId')
                task_desc['AutoCluster']= {}
            else:
                extend(task_desc['AutoCluster'], cluster_info['AutoCluster'])
        else:
            if cf.has_option(sec,'image'):
                task_desc['AutoCluster']['ImageId']=cf.get(sec,'image')
            if cf.has_option(sec, 'type'):
                task_desc['AutoCluster']['InstanceType'] = cf.get(sec, 'type')



        if not cluster_id or cluster_id=='':

            if cf.has_option(sec, 'resource_type'):
                task_desc['AutoCluster']['ResourceType'] = cf.get(sec, 'resource_type')

            # spot price limit
            if cf.has_option(sec, 'spot_price_limit'):
                spot_price_limit = cf.get(sec, 'spot_price_limit')

                if spot_price_limit is not None:
                    spot_price_limit = float(spot_price_limit)
                    if not task_desc['AutoCluster'].get('ResourceType') == 'Spot':
                        raise Exception('spot_price_limit works only if resource_type is Spot')

                    if spot_price_limit > 0:
                        task_desc['AutoCluster']['SpotPriceLimit'] = spot_price_limit
                        task_desc['AutoCluster']['SpotStrategy'] = 'SpotWithPriceLimit'
                    else:
                        task_desc['AutoCluster']['SpotStrategy'] = 'SpotAsPriceGo'
                

            if cf.has_option(sec, 'disk') and task_desc.get('AutoCluster'):
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs'] = {}
                task_desc['AutoCluster']['Configs']['Disks'] = trans_disk(cf.get(sec, 'disk'))

            if cf.has_option(sec, 'user_data'):
                if not task_desc['AutoCluster']['UserData']:
                    task_desc['AutoCluster']['UserData'] = {}
                extend(task_desc['AutoCluster']['UserData'], trans_user_data(cf.get(sec, 'user_data')))

            # vpc
            if cf.has_option(sec, 'vpc_cidr_block'):
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs'] = {}
                if not task_desc['AutoCluster']['Configs'].get('Networks'):
                    task_desc['AutoCluster']['Configs']['Networks'] = {}
                if not task_desc['AutoCluster']['Configs']['Networks'].get('VPC'):
                    task_desc['AutoCluster']['Configs']['Networks']['VPC'] = {}
                task_desc['AutoCluster']['Configs']['Networks']['VPC']['CidrBlock'] = cf.get(sec, 'vpc_cidr_block')

            if cf.has_option(sec, 'vpc_id'):
                if not task_desc['AutoCluster'].get('Configs'):
                    task_desc['AutoCluster']['Configs'] = {}
                if not task_desc['AutoCluster']['Configs'].get('Networks'):
                    task_desc['AutoCluster']['Configs']['Networks'] = {}
                if not task_desc['AutoCluster']['Configs']['Networks'].get('VPC'):
                    task_desc['AutoCluster']['Configs']['Networks']['VPC'] = {}
                task_desc['AutoCluster']['Configs']['Networks']['VPC']['VpcId'] = cf.get(sec, 'vpc_id')
        # mounts
        if cf.has_option(sec, 'no_cache_support'):
            task_desc['Mounts']['CacheSupport'] = not cf.getboolean(sec, 'no_cache_support')

        if cf.has_option(sec, 'nas_access_group'):
            if not task_desc.get('Mounts'):
                task_desc['Mounts'] = {}
            if not task_desc['Mounts'].get('NAS'):
                task_desc['Mounts']['NAS'] = {}
            task_desc['Mounts']['NAS']['AccessGroup'] = cf.get(sec, 'nas_access_group').split(',')

        if cf.has_option(sec, 'nas_file_system'):
            if not task_desc.get('Mounts'):
                task_desc['Mounts'] = {}
            if not task_desc['Mounts'].get('NAS'):
                task_desc['Mounts']['NAS'] = {}
            task_desc['Mounts']['NAS']['FileSystem'] = cf.get(sec, 'nas_file_system').split(',')



        if cf.has_option(sec, 'reserve_on_fail'):
            task_desc['AutoCluster']['ReserveOnFail'] = cf.getboolean(sec, 'reserve_on_fail')


        if cf.has_option(sec,'env'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_env(cf.get(sec,'env')))
        if cf.has_option(sec,'docker'):
            extend(task_desc['Parameters']['Command']['EnvVars'], trans_docker(cf.get(sec,'docker')))


        if cf.has_option(sec, 'mount'):
            extend_mount(task_desc, trans_mount(cf.get(sec, 'mount')))

        if cf.has_option(sec,'read_mount'):
            extend_mount(task_desc, trans_mount(cf.get(sec,'read_mount')))



        if cf.has_option(sec,'write_mount'):
            w_mount_m = trans_mount(cf.get(sec,'write_mount'))
            extend(task_desc['OutputMapping'], reverse_kv(w_mount_m))

        if cf.has_option(sec,'lock'):
            task_desc['Parameters']['InputMappingConfig']['Lock'] = cf.get('lock')
        if cf.has_option(sec,'locale'):
            task_desc['Parameters']['InputMappingConfig']['Locale'] = cf.get('locale')

        desc['DAG']['Tasks'][sec]= task_desc

    return desc

####################################################



def extend(obj, obj2):
    for k in obj2:
        obj[k] = obj2[k]
    return obj

def trans_deps(deps):
    # A->b,c;d->e,f
    parts = deps.strip(';').split(';')
    m = {}
    for part in parts:
      if '->' in part:
        [k,v] = part.split('->')
        m[k] = [x.strip() for x in v.split(',')]
    return m

def trans_cluster(cluster, image=None, type=None, check_cluster=True):
    obj = util.parse_cluster_cfg(cluster, check_cluster)

    if obj['ClusterId']=='':
        if image:
           obj['AutoCluster']['ImageId'] = image
        if type:
            obj['AutoCluster']['InstanceType'] = type

    return obj


def override_opt(opt, file):
    # asd
    for (k,v) in file.items():
        if not opt.get(k):
           opt[k] = v
    return opt

def trans_nodes(n):
    try:
        n = int(n)
        return n if n > 0 else 1
    except:
        return 1

def trans_timeout(n):
    try:
        n = int(n)
        return n if n > 0 else TIMEOUT
    except:
        return TIMEOUT



def trans_docker(docker=None, ignoreErr=False):
    return util.trans_docker(docker, ignoreErr)

def trans_env(s):
    if not s:
        return {}
    arr = s.split(',')
    env = {}
    for item in arr:
        if item.strip() == '':
            continue
        kv=item.split(':',1)
        env[kv[0].strip()] = kv[1].strip() if len(kv) == 2 else ''
    return env


def trans_mount(s):
    return util.trans_mount(s)


def trans_priority(p=None):
    try:
        return int(p)
    except:
        return 1

def trans_disk(disk):
    return util.trans_disk(disk)


def trans_user_data(user_data):
    items = user_data.split(',')
    m = {}
    for item in items:
        if item.strip()=='':
            continue
        kv = item.split(':',1)
        m[kv[0].strip()]= kv[1].strip() if len(kv)==2 else ''
    return m

def trans_notification_events(events):

    arr = events.split(',')
    for n in arr:
        if n not in EVENTS.get('JOB'):
            raise Exception('Invalid job event: %s\n  Type bcs e for more' % n)

    return arr

#######################################

def reverse_kv(m):
    m2={}
    for k,v in m.items():
        m2[v]=k
    return m2

def gen_rand_id():
    return uuid.uuid1()





def build_tar_from_dir_and_upload(folder_path, oss_path):
    '''
    pack program files, and upload to oss_path
    :param folder_path:
    :param oss_path:
    :return:
    '''

    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    if os.path.exists(dist):
        os.remove(dist)

    # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:

        full_folder_path = formater.get_abs_path(folder_path)
        full_folder_path = full_folder_path.rstrip('/')+'/'
        print('base folder: %s' % full_folder_path)

        for root,dir,files in os.walk(folder_path):
            for file in files:
                fullpath=os.path.join(root,file)
                fullpath = formater.get_abs_path(fullpath)
                fname = fullpath[len(full_folder_path):]
                print('add %s' % fname)
                tar.add(fullpath, arcname=fname)

    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)


def build_tar_from_arr_and_upload(arr, oss_path):
    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    if os.path.exists(dist):
        os.remove(dist)

     # tar
    print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:
        for file in arr:
            fullpath = formater.get_abs_path(file)
            print('add %s' % file)
            tar.add(fullpath, arcname=os.path.basename(fullpath))

    # upload
    print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)


######################################
def fit_vars(cf):
    secs = cf.sections()

    mKey = {}


    for sec in secs:
        ks = cf.options(sec)
        for k in ks:
            if k.startswith('$'):
                mKey[k]= cf.get(sec, k)

    for sec in secs:
        ks = cf.options(sec)
        for k in ks:
            v =  _ch_vars(mKey, cf.get(sec, k))
            cf.set(sec, k, v)

def _ch_vars(m, v):
    for k in m:
        if k in v:
            v = v.replace(k, m.get(k))
    return v
#########################################

def gen_task_desc():
    cluster_info = trans_cluster(None)
    task_desc = {
        "OutputMapping": {},
        "Timeout": TIMEOUT,
        "InputMapping": {},
        "LogMapping": {},
        "InstanceCount": 1,
        "ClusterId": "",
        "Mounts": {
            'NAS': {},
        },
        "AutoCluster": {
           'ReserveOnFail': False
        },
        "MaxRetryCount": 0,
        "Parameters": {
            "StderrRedirectPath": "",
            "InputMappingConfig": {
                #"Locale": "GBK",
                "Lock": False
            },
            "StdoutRedirectPath": "",
            "Command": {
                "EnvVars": {},
                "CommandLine": "",
                "PackagePath": ""
            }
        },
        "WriteSupport": True
    }
    if cluster_info['ClusterId']:
        task_desc['AutoCluster']=cluster_info['ClusterId']
    else:
        extend(task_desc['AutoCluster'], cluster_info['AutoCluster'])
    return task_desc

def gen_job_desc():
    return {
        "DAG": {
            "Tasks": { },
            "Dependencies": {}
        },
        "Description": "BatchCompute cli job",
        "JobFailOnInstanceFail": True,
        "AutoRelease": False,
        "Priority": 1,
        "Type": "DAG",
        "Name": "cli-job",
        "Notification": {'Topic':{}}
    }