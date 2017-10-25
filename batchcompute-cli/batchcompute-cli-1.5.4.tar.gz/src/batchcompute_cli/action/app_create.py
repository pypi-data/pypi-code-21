from ..util import client,util, config, formater
from terminal import green
import json
import re

def create(app_name=None, cmd=None, file=None, description=None, docker=None, image=None, env=None,
           resource_type=None, type=None, nodes=None, min_disk_size=None, disk_type=None,
           max_retry_count=None, timeout=None,
           inputs=None, outputs=None, daemonize=False,
           show_json=False):

    desc = {}
    if file:
        with open(file,'r') as f:
            desc = json.loads(f.read())


    if app_name:
        desc['Name']=app_name
    if not desc.get('Name'):
        raise Exception('app_name is required')

    if cmd:
        desc['CommandLine'] = cmd
    if not desc.get('CommandLine'):
        raise Exception('cmd is required')


    if description:
        desc['description'] = description or ''
    if daemonize:
        desc['Daemonize'] = daemonize or False

    if not desc.get('Config'):
        desc['Config']={}


    if docker:
        desc['Docker'] = trans_docker(docker)

    if not file and image:
        desc['VM'] = {}
        desc['VM']['ECSImageId']=image if image else config.get_default_image()


    if env:
        desc['EnvVars'] = env

    if inputs:
        desc['InputParameters'] = inputs
    if outputs:
        desc['OutputParameters'] = outputs

    ########
    if resource_type:
        desc['Config']['ResourceType'] = trans_config_item('ResourceType',resource_type)
    if type:
        desc['Config']['InstanceType'] = trans_config_item('InstanceType',type)

    if nodes:
        desc['Config']['InstanceCounts'] = trans_config_item('InstanceCounts',nodes)
    if min_disk_size:
        desc['Config']['MinDiskSize'] = trans_config_item('MinDiskSize',min_disk_size)
    if disk_type:
        desc['Config']['DiskType'] = trans_config_item('DiskType',disk_type)
    if max_retry_count:
        desc['Config']['MaxRetryCount'] = trans_config_item('MaxRetryCount',max_retry_count)
    if timeout:
        desc['Config']['Timeout'] = trans_config_item('Timeout',timeout)


    if show_json:
        print(json.dumps(desc, indent=4))
    else:
        result = client.create_app(desc)

        if result.StatusCode==201:
            print(green('App created: %s' % desc['Name']))

def trans_docker(docker=None, ignoreErr=False):
    info = util.trans_docker(docker, ignoreErr)
    return {
        'Image': info.get('BATCH_COMPUTE_DOCKER_IMAGE'),
        'RegistryOSSPath': info.get('BATCH_COMPUTE_DOCKER_REGISTRY_OSS_PATH')
    }

def trans_env(s):
    if not s:
        return {}
    arr = s.split(',')
    env = {}
    for item in arr:
        if item.strip() == '':
            continue
        #kv=re.split(r'=|:',item,1)
        kv=item.split(':',1)
        env[kv[0].strip()] = kv[1].strip() if len(kv) == 2 else ''
    return env

#  {defaultValue}:{overwritable}
def trans_config_item(name, item):
    if name in ['InstanceCounts','MinDiskSize','MaxRetryCount','Timeout']:
        return formater.trans_app_config_item(item, int)
    else:
        return formater.trans_app_config_item(item)


def trans_outputs_params(params):
    return formater.trans_app_outputs_params(params)

def trans_inputs_params(params):
    return formater.trans_app_inputs_params(params)