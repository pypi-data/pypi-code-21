from ..util import util,oss_client,client,validator,config
import json
import os
from terminal import blue,green
from ..const import CMD
import uuid

def submit():
    util.check_is_job_project()

    with open('job.json') as f:
        obj = json.loads(f.read())


    validate_job(obj)

    keep_m = {}

    for k in obj['DAG']['Tasks']:
        pkg_path = obj['DAG']['Tasks'][k]['Parameters']['Command'].get('PackagePath')
        if not pkg_path:
            pre_oss_path = config.get_oss_path()
            jobid = gen_rand_id()
            pkg_path = '%s%s/worker.tar.gz' % (pre_oss_path, jobid)
            obj['DAG']['Tasks'][k]['Parameters']['Command']['PackagePath'] = pkg_path
            if not obj['DAG']['Tasks'][k]['Parameters'].get('StderrRedirectPath'):
                obj['DAG']['Tasks'][k]['Parameters']['StderrRedirectPath']='%s%s/logs/' % (pre_oss_path, jobid)
                obj['DAG']['Tasks'][k]['Parameters']['StdoutRedirectPath']='%s%s/logs/' % (pre_oss_path, jobid)
        print('upload worker.tar.gz to oss...')

        if not keep_m.get(pkg_path):
            keep_m[pkg_path] = 1
            oss_client.upload_file( os.path.join(os.getcwd(), 'worker.tar.gz'), pkg_path)

    with open('job.json', 'w') as f:
        f.write(json.dumps(obj,sort_keys=True,indent=4))

    print('creating job..')
    s = client.create_job(obj)
    print(green('Job created: %s' % s.Id))


def validate_job(job):
    result = validator.validate_job(job)

    if result:
        raise Exception('Invalid job.json:\n%s\n\n    %s' % (result, blue('type "%s st -v" for more' % CMD)))

def gen_rand_id():
    return uuid.uuid1()