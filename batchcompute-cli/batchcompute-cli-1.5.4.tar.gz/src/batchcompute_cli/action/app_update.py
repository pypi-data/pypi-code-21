from ..util import client,util, formater, result_cache
from terminal import confirm, green
import json

def update(app_name,cmd=None, description=None, docker=None, image=None, env=None, daemonize=None,
           show_json=False, yes=False):

    app_name = result_cache.get(app_name, 'apps')

    revisions = client.get_app_revisions(app_name).Items

    revisions = formater.order_by(revisions, ['Revision'],True)
    detail = client.get_app_detail(app_name, str(revisions[0].Revision))
    desc = json.loads(detail.dump())

    if daemonize!=None:
        desc['Daemonize'] = bool(daemonize)

    if cmd:
        desc['CommandLine'] = cmd
    if description:
        desc['Description'] = description

    if docker:
        desc['Docker'] = trans_docker(docker)
        if desc.get('VM'): del desc['VM']
    elif image:
        desc['VM'] = {}
        desc['VM']['ECSImageId']=image
        if desc.get('Docker'):del desc['Docker']

    if env:
        desc['EnvVars'] = env


    if show_json:
        print(json.dumps(desc, indent=4))
    else:
        if yes:
            client.update_app(desc['Name'], desc)
            print(green('done'))
        else:
            if confirm('Update app %s' % (app_name), default=False):
                client.update_app(desc['Name'], desc)
                print(green('done'))


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
        kv=item.split(':',1)
        env[kv[0].strip()] = kv[1].strip() if len(kv) == 2 else ''
    return env
