

import os
from ..util import client, zip,oss_client,config
from terminal import green,white
import re
import json
import tarfile
from batchcompute_cli.const import CMD
import shutil


def trans_jobId(job=None):
    if not job or not job.startswith('job-'):
        raise Exception('Invalid job_id: %s' % job)
    return job

def trans_type(type=None):
    if not type:
        return 'empty'

    arr = ['java','python','shell','empty','gatk','wdl']
    if(type.lower() in arr):
        return type.lower()

    raise Exception('Invalid type: %s, it must be in [%s] or an available oss path' % (type, '|'.join(arr) ))


def gen(location=None, type="empty"):

    dist = __get_location(location)

    cur_path = os.path.split(os.path.realpath(__file__))[0]

    src = os.path.join(cur_path, '../templates/%s' % type)

    print('init with [%s] template at: %s' % ( 'python' if type=='empty' else type, dist))

    zip.unzip_file('%s.zip' % src, dist)

    if type=='empty' or type=='python':
        # add oss2 to src
        add_oss2(cur_path, dist)

    if type in ('gatk', 'wdl'):
        try:
            ins_type = config.get_default_instance_type()
        except:
            ins_types = (client.list_instance_types() or [])
            ins_type = ins_types[0] if len(ins_types)>0 else ''
        with open(os.path.join(dist,'main.sh')) as f:
            str = f.read().replace('${instance_type}', ins_type)
        with open(os.path.join(dist,'main.sh'),'w') as f:
            f.write(str)

    else:
        # update job.json set imageId: m-28sm4m6ez
        update_image_n_instype(os.path.join(dist,'job.json'))

    print(green('Done'))




def update_image_n_instype(p):
    obj = {}
    with open(p, 'r') as f:
        obj = json.loads(f.read())

    if obj.get('Type') == 'DAG':
        with open(p, 'w') as f:
            ts = obj['DAG']['Tasks']

            img_id = config.get_default_image()
            ins_type = config.get_default_instance_type()

            for k in ts:
                ts[k]['AutoCluster']['ImageId']=img_id
                ts[k]['AutoCluster']['InstanceType']=ins_type

            f.write(json.dumps(obj, indent=2))



def download_worker(packageUri, dist):
    src = os.path.join(dist, 'src')
    os.mkdir(src)
    tarpath = os.path.join(dist,'worker.tar.gz')

    oss_client.download_file(packageUri, tarpath)

    with tarfile.open(tarpath, 'r|gz') as f:
        f.extractall(src)

def add_oss2(cur_path, dist):
    src = os.path.join(cur_path, '../lib/oss2')
    target = os.path.join(dist,'src/oss2')
    if not os.path.exists(target):
        shutil.copytree(src, target, True)




def __parse_type_from_cmd_line(cmd_line):
    if 'java ' in cmd_line:
        return 'java'
    elif 'python ' in cmd_line:
        return 'python'
    elif 'wdl' in cmd_line:
        return 'wdl'
    else:
        return 'shell'



def __get_location(location):

    if not location:
        return os.getcwd()

    elif location.startswith('/') or location.startswith('~') or re.match(r'^\w\:',location):
        return location
    else:
        return os.path.join(os.getcwd(), location)
