import os
from ..util import client, zip,oss_client,config
from terminal import green,white
import re
import json
import tarfile
from batchcompute_cli.const import CMD
import shutil

def create(project_name, location=None, type='empty',job=None ):

    dist = __get_location(location)
    dist = os.path.join(dist, project_name)

    if job:
        # create from job id
        jobDesc = client.get_job_description(job)
        if not jobDesc:
            raise Exception('Cannot get job description: %s ' % job)

        print(str(jobDesc))
        os.mkdir(dist)

        with open(os.path.join(dist, 'job.json') , 'w') as f:
            f.write(str(jobDesc))

        desc_map = jobDesc.get('DAG').get('Tasks')
        type = ''
        for (k,v) in desc_map.items():
            cmd_line = v.get('Parameters').get('Command').get('CommandLine')
            pkg_path = v.get('Parameters').get('Command').get('PackagePath')

            type = __parse_type_from_cmd_line(cmd_line)


            if pkg_path:
                project_json = {'type':type, 'tar_src':{"base":'src','files':['*','*/*']}}

                with open(os.path.join(dist, 'project.json') , 'w') as f:
                    f.write(json.dumps(project_json, indent=2))

                download_worker(pkg_path, dist)
                break

        print('create %s project [%s] at: %s' % (project_name, type, dist))

    else:
        cur_path = os.path.split(os.path.realpath(__file__))[0]

        src = os.path.join(cur_path, '../templates/%s' % type)

        print('create %s project [%s] at: %s' % (project_name, 'python' if type=='empty' else type, dist))

        zip.unzip_file('%s.zip' % src, dist)

        if type=='empty' or type=='python':
            # add oss2 to src
            add_oss2(cur_path, dist)

        # update job.json set imageId: m-28sm4m6ez
        update_image_n_instype(os.path.join(dist,'job.json'))

    print(green('Done'))
    print(white('Type "cd %s && %s p st" to show project detail\n' % (project_name,CMD)))

def update_image_n_instype(p):
    obj = {}
    with open(p, 'r') as f:
        obj = json.loads(f.read())

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


def transform_job_id(job=None):
    if not job or not job.startswith('job-'):
        raise Exception('Invalid job_id: %s' % job)
    return job

def transform_type(type=None):
    if not type:
        return 'empty'

    arr = ['java','python','shell','empty']
    if(type.lower() in arr):
        return type.lower()

    raise Exception('Invalid type: %s' % type)


def __parse_type_from_cmd_line(cmd_line):
    if 'java ' in cmd_line:
        return 'java'
    elif 'python ' in cmd_line:
        return 'python'
    else:
        return 'shell'



def __get_location(location):

    if not location:
        return os.getcwd()

    elif location.startswith('/') or location.startswith('~') or re.match(r'^\w\:',location):
        return location
    else:
        return os.path.join(os.getcwd(), location)
