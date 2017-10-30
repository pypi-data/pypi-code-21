from batchcompute import Client
from ..const import IT_MAP,VERSION
from .config import getConfigs,COMMON
from batchcompute.utils import set_log_level
from . import formater,it_config
import platform

set_log_level("ERROR")

def _get_endpoint(region):
    domain = 'batchcompute.%s.aliyuncs.com' % region
    Client.register_region(region, domain)
    return domain


def _get_client(opt=None):
    opt = opt or getConfigs(COMMON, ['region', 'accesskeyid','accesskeysecret','version','ssl'])
    if not opt or not opt.get('accesskeyid'):
        raise Exception('You need to login first')

    headers = {
       'x-client-name': 'batchcompute-cli',
       'x-client-version':VERSION,
       'User-Agent':'Platform/%s Python/%s batchcompute-cli/%s' % (platform.platform(), platform.python_version(), VERSION)
    }

    c = Client(_get_endpoint(opt.get('region')),
        opt.get('accesskeyid'), opt.get('accesskeysecret'),security_conn=not opt.get('ssl'),
        **headers)

    if opt.get('version'):
        c.version = opt.get('version')
    return c

def check_client(opt):
    client = _get_client(opt)
    client.list_jobs("",1)


def list_clusters():
    client = _get_client()
    arr = __list_clusters(client)
    return {'Items':arr,'Marker':''}

def __list_clusters(client, marker='', maxItemCount=100):
    t = []
    result = client.list_clusters(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_clusters(client,result.NextMarker,maxItemCount)
        t = t + arr
    return t

def get_cluster(cluster_id):
    client = _get_client()
    return client.get_cluster(cluster_id)

def delete_cluster(cluster_id):
    client = _get_client()
    return client.delete_cluster(cluster_id)

def create_cluster(clusterDesc):
    client = _get_client()
    return client.create_cluster(clusterDesc)

def change_cluster_vmcount(cluster_id, groupName, vmCount):
    client = _get_client()
    return client.change_cluster_desired_vm_count(cluster_id, **{groupName: int(vmCount)})

def update_cluster(cluster_id, clusterDesc):
    client = _get_client()
    client.modify_cluster(cluster_id, clusterDesc)

    if clusterDesc.get('Groups'):
        for (k,v) in clusterDesc['Groups'].items():
            if v.get('SpotStrategy'):
                client.change_cluster_spot_config(cluster_id, k, strategy=v.get('SpotStrategy'),
                                                  price_limit=v.get('SpotPriceLimit'))



def list_jobs():
    client = _get_client()
    arr = __list_jobs(client)
    return {'Items':arr,'Marker':''}

def __list_jobs(client, marker='', maxItemCount=100):
    t = []
    result = client.list_jobs(marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_jobs(client, result.NextMarker, maxItemCount)
        t = t + arr
    return t




def get_job(job_id):
    client = _get_client()
    return client.get_job(job_id)

def get_job_description(job_id):
    client = _get_client()
    return client.get_job_description(job_id)

def list_tasks(job_id):
    client = _get_client()
    arr = __list_tasks(client, job_id)
    return {'Items':arr,'Marker':''}

def __list_tasks(client,job_id, marker='', maxItemCount=100):
    t = []
    result = client.list_tasks(job_id, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_tasks(client, job_id, result.NextMarker, maxItemCount)
        t = t + arr
    return t



def list_instances(job_id, task_name):
    client = _get_client()
    arr = __list_instances(client, job_id, task_name)
    return {'Items':arr,'Marker':''}

def __list_instances(client, job_id, task_name, marker='', maxItemCount=100):
    t = []
    result = client.list_instances(job_id, task_name, marker, maxItemCount)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_instances(client, job_id, task_name, result.NextMarker, maxItemCount)
        t = t + arr
    return t


def get_task(job_id, task_name):
    client = _get_client()
    return client.get_task(job_id, task_name)


def get_instance(job_id, task_name, instance_id):
    client = _get_client()
    return client.get_instance(job_id, task_name, instance_id)




def change_job_priority(job_id, priority):
    client = _get_client()
    return client.change_job_priority(job_id, priority)


def start_job(job_id):
    client = _get_client()
    return client.start_job(job_id)


def stop_job(job_id):
    client = _get_client()
    return client.stop_job(job_id)

def delete_job(job_id):
    client = _get_client()
    return client.delete_job(job_id)

def create_job(jobDesc):
    client = _get_client()
    return client.create_job(jobDesc)

############################
def list_apps():
    client = _get_client()

    sysArr = __list_apps(client, '', 100, scope='Public')
    for n in sysArr:
        n['Scope'] = 'Public'

    arr = __list_apps(client, '', 100, scope='Private')
    for n in arr:
        n['Scope'] = 'Private'


    formater.order_by(sysArr, ['CreationTime'], True)
    formater.order_by(arr, ['CreationTime'], True)
    return {'Items': sysArr + arr, 'Marker': ''}

def __list_apps(client, marker='', maxItemCount=100, scope="Private"):
    t = []
    result = client.list_apps(scope, marker, maxItemCount)
    if result.Items:
        tt = __items2list(result.Items)
        if scope=='Public':
            for n in tt:
                n['Name'] = ":%s" % n['Name']
        t = t + tt

    if result.NextMarker and result.NextMarker!='':
        arr = __list_apps(client, result.NextMarker, maxItemCount, scope)
        t = t + arr
    return t

def get_app(appName, scope="Private"):
    client = _get_client()
    info = client.get_app(appName, scope)
    return info


def get_app_revisions(appName):
    client = _get_client()
    return client.get_app_revisions(appName)


def get_app_detail(appName, qualifier=""):
    client = _get_client()
    return client.get_app_detail(appName, qualifier)


def delete_app(appName, revision):
    client = _get_client()
    return client.delete_app(appName, revision)

def create_app(desc):
    client = _get_client()
    return client.create_app(desc)

def update_app(appName, desc):
    client = _get_client()
    return client.modify_app(appName, desc)


#############################
def list_images():
    client = _get_client()

    sysArr = __list_images(client,'',100,type_='System')
    arr = __list_images(client)
    return {'Items': sysArr + arr,'Marker':''}

def __list_images(client, marker='', maxItemCount=100, type_=''):
    t = []
    result = client.list_images(marker, maxItemCount, type_)
    if result.Items:
        t = t + __items2list(result.Items)

    if result.NextMarker and result.NextMarker!='':
        arr = __list_images(client,result.NextMarker,maxItemCount,type_)
        t = t + arr
    return t


def get_image(image_id):
    client = _get_client()
    return client.get_image(image_id)

def delete_image(image_id):
    client = _get_client()
    return client.delete_image(image_id)

def create_image(imageDesc):
    client = _get_client()
    return client.create_image(imageDesc)

def get_quotas():
    client = _get_client()
    return client.get_quotas()

def list_instance_types():
    quotas = get_quotas()
    arr = quotas.AvailableClusterInstanceType

    itmap = it_config.get()
    t=[]
    for n in arr:
        t.append( itmap[n] if itmap.get(n) else {'name':str(n),'cpu': -1,'memory':-1} )
    t = formater.order_by(t, ['cpu','memory'],False)

    return t

def list_spot_instance_types():
    quotas = get_quotas()
    arr = quotas.AvailableSpotInstanceType

    itmap = it_config.get()
    t = []
    for n in arr:
        t.append(itmap[n] if itmap.get(n) else {'name': str(n), 'cpu': -1, 'memory': -1})
    t = formater.order_by(t, ['cpu', 'memory'], False)
    return t


def get_ins_type_map():
    arr = list_instance_types() or []
    arr2 = list_spot_instance_types() or []
    m = {}
    for item in arr:
        m[item['name']] = item
    for item in arr2:
        m[item['name']] = item
    return m


def __items2list(items):
    t=[]
    for item in items:
        m = {}
        for k in item.keys():
            m[k] = item.get(k)
        t.append(m)
    return t