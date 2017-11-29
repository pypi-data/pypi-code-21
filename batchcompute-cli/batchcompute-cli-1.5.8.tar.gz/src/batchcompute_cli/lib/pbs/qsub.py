# -*- coding: utf-8 -*-

'''
qsub命令:
--------------------------
bcs qsub [-d work_path] [-e stderr_path]
                 [-j oe|eo|n] [-l resource_list] [-N job_name]
                 [-o stdout_path] [-q cluster_id] [-V]
                 <script_name>
---------------------------

实际运行:
bcs sub "python qsub.py base64(str)"

opt = {
  shell: '',
  job_name: '',
  script_name: ''
  work_path: '/home/admin/',
  stderr_path: '/home/admin/stderr.log',
  stdout_path: '/home/admin/stdout.log',
  join: 'oe',
  resources: {
    cpu: 9, mem: 10,
  },
  env: {

  }
}
'''

import sys
import base64
import subprocess
import json
import os
import socket

PY3 = sys.version_info[0] == 3
WIN = sys.platform == 'win32'

def run(opt):
    opt = json.loads(opt)
    print('-->options:\n%s' % json.dumps(opt, indent=4))

    cwd = opt.get('work_path')
    if not os.path.exists(cwd):
        os.makedirs(cwd)

    print('-->work_path is %s' % cwd)

    # copy
    print('-->copy script file to work_path')

    with open(opt['script_name'], "rb") as f:
        script_content = f.read()
    with open(os.path.join(cwd, opt['script_name']), "wb") as fw:
        fw.write(script_content)

    shell = opt.get('shell') or ('' if WIN else '/bin/bash')
    cmd = '%s %s' % (shell,  os.path.join(cwd, opt['script_name']) )

    print('-->start run: %s' % cmd)


    opt['env'].update({
        'PBS_O_HOST': socket.gethostname(),
        'PBS_SERVER': 'Default Server',
        'PBS_O_QUEUE': '1',
        'PBS_O_WORKDIR': cwd,
        'PBS_ARRAYID': '1',
        'PBS_ENVIRONMENT': 'PBS_BATCH', # 不支持交互式: PBS_INTERACTIVE
        'PBS_JOBID': os.environ.get('BATCH_COMPUTE_DAG_JOB_ID') or '',
        'PBS_JOBNAME': opt.get('job_name'),
        'PBS_NODEFILE': '',
        'PBS_QUEUE': '1'
    })



    sub = subprocess.Popen(cmd,
                           cwd=cwd,
                           env=opt['env'],
                           #bufsize=1024,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=True)

    stdout_path = opt.get('stdout_path')# or os.path.join(cwd, '%s.stdout' % (opt['job_name']))
    stderr_path = opt.get('stderr_path')# or os.path.join(cwd, '%s.stderr' % (opt['job_name']))

    stdout_path_dir = os.path.dirname(stdout_path)
    if not os.path.exists(stdout_path_dir):
        os.makedirs(stdout_path_dir)

    stderr_path_dir = os.path.dirname(stderr_path)
    if not os.path.exists(stderr_path_dir):
        os.makedirs(stderr_path_dir)

    out = sub.stdout.read()
    err = sub.stderr.read()

    if opt['join'] == 'oe':
        print('-->join=oe, stdout path: %s' % stdout_path)
        with open(stdout_path, 'wb') as f:
            f.write('%s\n%s' % (out, err))
            f.flush()
    elif opt['join'] == 'eo':
        print('-->join=eo, stdout path: %s' % stdout_path)
        with open(stdout_path, 'wb') as f:
            f.write('%s\n%s' % (err,out))
            f.flush()
    else:
        print('-->join=n, stdout path: %s, stderr path: %s' % (stdout_path, stderr_path))
        with open(stdout_path, 'wb') as f:
            f.write(out)
            f.flush()
        with open(stderr_path, 'wb') as f:
            f.write(err)
            f.flush()



if __name__ == '__main__':
    if PY3:
        run(base64.decodestring(sys.argv[1].encode('utf-8')).decode())
    else:
        run(base64.decodestring(sys.argv[1]))
