# -*- coding: utf-8 -*-
from terminal import green
import re
import os
from ..util import client, config, formater, oss_client, qsub_config
import json
import uuid
import base64
import tarfile
from ..const import  PY3
import socket
import getpass


def qsub(script_name, work_path=None, stderr_path=None, join='n',
         job_name=None, resource_list=None, stdout_path=None, env=False,


         zz=False, xx=False,XX=False,additional_attributes=None,wpath=None,
         variable_list=None,user_list=None,
         prescript=None, array_request=None, path_list=None, rerunable=None, queue=None,
         proxy_user=None, priority=None, mail_user_list=None, mail_optinos=None, keep=None,
         interactively=False, hold=False, ff=False, root_path=None, directive_prefix=None,checkpoint_options=None,
         seconds=None, account_string=None, date_time=None,


         show_json=False, show_opt=False):

    # 参数
    opt = {
        'shell': '/bin/bash',
        'job_name': job_name or 'job',
        'script_name': script_name,
        'work_path': work_path,
        'stderr_path': stderr_path,
        'stdout_path': stdout_path,
        #'queue': queue,
        'join': join,
        #'timeout': 0,
        'resource_list': parse_resource_list(resource_list or ''),
        'env': {
            'PBS_O_HOME': os.environ.get('HOME') or '',
            'PBS_O_LANG': os.environ.get('LANG') or '',
            'PBS_O_LOGNAME': os.environ.get('LOGNAME') or '',
            'PBS_O_PATH': os.environ.get('PATH') or '',
            'PBS_O_MAIL': os.environ.get('MAIL') or '',
            'PBS_O_SHELL': os.environ.get('SHELL') or '',
            'PBS_O_TZ': os.environ.get('TZ') or '',
        }
    }

    opt['env'].update(os.environ if env else {})

    #print(json.dumps(opt, indent=4))

    # 文件
    opt2 = parseScript(script_name)
    #print(json.dumps(opt2, indent=4))



    # 参数 覆盖 文件
    for (k,v) in opt.items():
        if v:
            if k=='resource_list':
                if opt2.get(k):
                    opt2[k].update(opt.get(k) or {})
                else:
                    opt2[k]=opt.get(k) or {}
            else:
                opt2[k]=v

    # 路径
    if opt2.get('work_path'):
        cwd = getAbsPath(opt2['work_path'])
    else:
        cwd = os.getcwd()
    opt2['work_path']=cwd

    opt2['stdout_path'] = getAbsPath(opt['stdout_path']) if opt.get('stdout_path') else os.path.join(cwd, '%s.stdout' % (opt['job_name']))
    opt2['stderr_path'] = getAbsPath(opt['stderr_path']) if opt.get('stderr_path') else os.path.join(cwd, '%s.stderr' % (opt['job_name']))

    if show_opt:
        print(json.dumps(opt2, indent=4))
        return


    #################################
    desc = to_job_desc(opt2)
    qsubuser = config.get_qsubuser()
    desc['Name'] = 'qsub-%s-%s' % (qsubuser, opt2['job_name'] )


    ## 打包上传
    pack_upload(desc, opt2, show_json)

    if show_json:
        print(json.dumps(desc, indent=4))
    else:
        # submit
        result = client.create_job(desc)

        if result.StatusCode == 201:
            print(green('%s' % formater.hex_job_id(result.Id) ))



def pack_upload(desc, opt, show_json):

    pre_oss_path = config.get_oss_path()
    rand = uuid.uuid1()

    task_desc = desc['DAG']['Tasks']['task']

    task_desc['Parameters']['StdoutRedirectPath'] = '%s%s/logs/' % (pre_oss_path, rand)
    task_desc['Parameters']['StderrRedirectPath'] = '%s%s/logs/' % (pre_oss_path, rand)

    package_path = '%s%s/worker.tar.gz' % (pre_oss_path, rand)
    task_desc['Parameters']["Command"]['PackagePath'] = package_path

    opt_str=  json.dumps(opt)
    base64Str = (base64.b64encode(opt_str.encode(encoding='utf-8'))).decode() if PY3 else base64.b64encode(opt_str)
    task_desc['Parameters']["Command"]['CommandLine'] = 'python qsub.py %s' % base64Str

    # logs
    task_desc['LogMapping'] = {}
    task_desc['LogMapping'][opt['stdout_path']] = '%s%s/logs/' % (pre_oss_path, rand )
    task_desc['LogMapping'][opt['stderr_path']] = '%s%s/logs/' % (pre_oss_path, rand )


    # pack upload
    if not show_json:
        # upload
        dirname = os.path.dirname(os.path.abspath(__file__))
        build_tar_from_arr_and_upload([
            os.path.join(dirname, '../lib/pbs/qsub.py'),
            os.path.join(os.getcwd(), opt['script_name'])
        ], package_path)


def build_tar_from_arr_and_upload(arr, oss_path):
    dist = os.path.join(os.getcwd(), 'worker.tar.gz')

    if os.path.exists(dist):
        os.remove(dist)

     # tar
    #print('pack %s' % dist)
    with tarfile.open(dist, 'w|gz') as tar:
        for file in arr:
            fullpath = formater.get_abs_path(file)
            #print('add %s' % file)
            tar.add(fullpath, arcname=os.path.basename(fullpath))

    # upload
    #print('Upload: %s ==> %s' % (dist, oss_path))
    oss_client.upload_file( dist, oss_path)



def to_job_desc(opt):
    m = opt['resource_list']

    '''
    :param m: { cpu, mem, timeout, nodes}
    :return:
    '''
    job = _gen_job_desc()

    task = _gen_task_desc()

    job['DAG']['Tasks']['task'] = task

    # nodes
    task['InstanceCount'] = m.get('nodes') or 1

    # timeout
    if m.get('timeout'):
      task['Timeout'] = m.get('timeout')


    clusterId = ''
    # que = opt.get('queue')
    # if que:
    #     clusterId = getClusterIdFromQueue(opt.get('queue'))

    # if que and clusterId:
    #     task['ClusterId'] = clusterId

    #else:

    ## cpu mem
    cpu = m.get('cpu') or 0
    mem = m.get('mem') or 0

    if cpu == 0 and mem == 0:
        task['AutoCluster']['InstanceType'] = config.get_default_instance_type()
    else:
        task['AutoCluster']['InstanceType'] = get_instance_type(cpu, mem)

    #########
    task['AutoCluster']["ResourceType"] = "OnDemand"
    task['AutoCluster']['ImageId'] = config.get_default_image()

    return job


def getClusterIdFromQueue(q):
    if not q:
        return None
    if '@' in q:
        (k,v) = q.split('@',1)
        return v
    else:
        return None



def get_instance_type(cpu, mem):
    availableTypes = client.list_instance_types()
    for tp in availableTypes:
        #print(tp)
        if tp['cpu'] >= cpu and tp['memory'] >= mem:
            return tp['name']
    raise Exception('Can not found suitable instance type for the cpu and mem you request')

def _gen_task_desc():
    m = qsub_config.get()

    return {
        "OutputMapping": {},
        #"Timeout": 0,
        "InputMapping": {},
        "LogMapping": {},
        "InstanceCount": 1,
        "ClusterId": "",
        "Mounts": ( m.get('Mounts') or {} ) if m else {},
        "AutoCluster": {
            'ReserveOnFail': False,
            'Configs': {

            }
        },
        "MaxRetryCount": 0,
        "Parameters": {
            "StderrRedirectPath": "",
            "InputMappingConfig": {
                # "Locale": "GBK",
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

def _gen_job_desc():
    return {
        "DAG": {
            "Tasks": { },
            "Dependencies": {}
        },
        "Description": json.dumps({'type':'qsub','host':socket.gethostname(), 'user':getpass.getuser()}),
        "JobFailOnInstanceFail": True,
        "AutoRelease": False,
        "Priority": 1,
        "Type": "DAG",
        "Name": "qsub-job",
        "Notification": {'Topic':{}}
    }



def parseScript(script_name):
    pp = os.path.join(os.getcwd(), script_name)
    with open(pp, 'r') as f:
        lines = f.readlines()

    shell=''
    try:
        if len(lines)>0 and lines[0].startswith('#!'):
            shell = lines[0].strip()
    except:
        pass

    m = {'resource_list':{}, 'shell': shell}
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            line = line[1:].strip()
            if line.startswith('PBS'):
                parsePBS(m ,line[4:])
    return m


def parsePBS(m, line):
    '''
    :param line: -d /home/admin/
    :return m: dict
    '''

    line = line.strip()
    if line.startswith('-N'):
        m['job_name']=line[3:].strip()
    elif line.startswith('-l'):
        m['resource_list'].update(parse_resource_list(line[3:].strip()))
    elif line.startswith('-d'):
        m['work_path']= line[3:].strip()
    elif line.startswith('-o'):
        m['stdout_path'] = line[3:].strip()
    elif line.startswith('-e'):
        m['stderr_path'] = line[3:].strip()
    elif line.startswith('-n'):
        m['join'] = line[3:].strip()
    elif line.startswith('-V'):
        m['env'] = os.environ



def parse_resource_list(s):

    '''
    资源请求的两种方式：

    a、资源块方式：资源块是将任务所需的资源作为一个整体，这个整体中说明了所需要的各种资源的数目。
      其格式为：-l select=[N:]chunk[+[N:]chunk…]，
      如qsub –l select=2:ncpus=3:mem=4gb:arch=linux ，

    select=2表示需要2个这样的资源块，一个资源块包括3个cpu，4gb的内存，系统结构要求是linux，
    即总共需要6个cpu，8gb的内存。

    再如：-l select=2:ncpus=1:mem=10GB+3:ncpus=2:mem=8GB:arch=solaris
    注意中间的+号，是两个资源块的分隔符

    b、请求全任务(job-wide)资源：
      格式为 –l  keyword=value[,keyword=value ...]
      如：qsub -l ncpus=4,mem=123mb,arch=linux


    '''

    if not s:
        return {}

    s = s.strip()
    if s == '':
        return {}

    #  –l  keyword=value[,keyword=value ...]
    kvp = s.split(',')


    m = {}
    for kv in kvp:
        m2 = parseSelect(kv[7:]) if  kv.startswith('select=') else parseKV(kv)
        m.update(m2)
    return m


def parseKV(kv):

    (k,v) = kv.split('=',1)

    if k == 'walltime' or k == 'pcput':
        v = parseWalltime(v)
        return {
            'timeout': v
        }
    elif k=='nodes':
        return {
            'nodes': parseNodes(v)
        }
    elif k=='ncpus':
        return {
            'cpu': parseInt(v)
        }
    elif k=='mem':
        return {
            'mem': parseMem(v)
        }


def parseSelect(sel):
  '''
  :param sel:   2:cpu=2:mem=4gb+4:cpu=3:mem=8gb
  :return: dict
  '''

  if '+' in sel:
      chunks = sel.split('+')
  else:
      chunks = [sel]

  # chunks =[], chunk: 2:cpu=2:mem=4gb

  m = {}
  for chunk in chunks:
      if chunk.strip() == '': continue

      items = chunk.split(':')

      try:
          num = float(items[0])
          items = items[1:]
      except:
          num = 1

      for item in items:
          kv = item.split('=')
          parseSelectItem(m, kv[0], kv[1] if len(kv)==2 else '', num)
  return m


def parseSelectItem(m,k,v, num):

    '''
    LINUX系统可以设置的资源有:

        arch 所需要的系统结构，只用在资源块中 -l arch=linux
        cput 任务的所有进程拥有的最大 cpu 执行时间 -l cput=1:00:00
        file 任务能够创建的文件的大小 -l file=45mb
        host 指定执行主机的名称 -l nodes=X:host 分配 X个主机名称 中含有 host的执行节点
        mem 任务的所有进程能够分配到的最大物理内存数 -l mem=100mb
        ncpus 请求的 cpu数 -l ncup=5
        nice 任务运行时的 nice 优先级值 -l nice=3
        pcput 任务的任何一个进程拥有的最大 cpu 执行时间 -l pcput=1:00:00
        pmem 任务的任何一个进程能够分配到的最大物理内存数 -l pmem=45mb
        pvmem 任务的任何一个进程能够使用的虚拟内存的最大数 -l pvmem=100mb
        vmem 任务的所有并发进程能够使用的最大虚存数 -l pvmem=100mb
        walltime 任务可以处于运行态的最大 wall-clock 时间 -l walltime=1:00:00
        custom resources 用户自定义资源
        nodes指定作业独占使用的结点数目和属性，使用“+”可以连接多种结点的定义。

       结点的属性和主机名或数目之间通过“：”分隔。如果不指定结点数，则缺省为1。
       结点的属性包括ppn（每个结点上的进程数,缺省为1）
       和系统管理员设置的属性（如batch、bigmem）

    :param m: dict
    :param k: str
    :param v:
    :param num:
    :return:
    '''
    if k=='ncpus':
        v= parseInt(v)
        addTo(m, 'cpu', v, num)

    elif k=='mem':
        v= parseMem(v)
        addTo(m, k,v, num)
    elif k == 'nodes':
        v = parseInt(v)
        addTo(m, k, v, num)


def addTo(m,k,v, num):
    if m.get(k):
        m[k] = m[k] + v * num
    else:
        m[k] = v * num

def parseWalltime(v):
    (h,m,s) = v.split(':')
    return int(h)*3600+int(m)*60+int(s)

def parseMem(v):
   if v.lower().endswith('mb'):
       return float(v[:-2])/1024
   elif v.lower().endswith('gb'):
       return float(v[:-2])
   else:
       raise Exception('Unsupported mem format')


def parseNodes(v):
    if '+' in v:
        arr = map(lambda n: parseInt(n), v.split('+'))
        return reduce(lambda x, y: x + y, arr)

    else:
        return parseInt(v)

def getAbsPath(s):
    return s if s.startswith('/') else os.path.join(os.getcwd(), s)

def parseInt(s):
    return int(re.match(r'\d+',s).group(0))
def parseFloat(s):
    return float(re.match(r'[\d\.]+',s).group(0))
