from requests.exceptions import StreamConsumedError

from ..util import result_cache, oss_client, formater, client,smart_unicode
from terminal import white,green,red,magenta,bold,yellow,blue
import os
from oss2.exceptions import NoSuchKey,NoSuchBucket
import json
from ..const import WIN,PY2
import time
SLEN = 60

def fetch(jobId, dir_path=None,stdout=False, stderr=False, log_mapping=False, taskName=None, instanceId=None):

    if jobId.startswith('-'):
        raise Exception('Invalid jobId')

    jobId = result_cache.get(jobId, 'jobs')

    t = [jobId]
    if taskName:
        taskName = result_cache.get(taskName, 'tasks')
        t.append(taskName)


    if instanceId!=None:
        t.append(instanceId)



    if dir_path:
        print(white('exec: bcs log %s --dir_path %s' %  (' '.join(t), dir_path) ))

        # mkdir
        dir_path = formater.get_abs_path(dir_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    else:
        print(white('exec: bcs log %s' %  ' '.join(t) ))


    if instanceId!=None:
        # get instance log
        ins = client.get_instance(jobId,taskName, instanceId)

        ins = formater.to_dict(ins)

        # log
        print_ins_log(jobId, taskName, ins, stdout, stderr, log_mapping, dir_path)

        # result
        print_inst_result(jobId, taskName, ins, dir_path)


    elif taskName!=None:
        # get task log
        ins_list_result = client.list_instances(jobId, taskName)
        ins_items = formater.items2arr(ins_list_result.get('Items'))

        for ins in ins_items:
            # log
            print_ins_log(jobId, taskName, ins, stdout, stderr, log_mapping, dir_path)

            # result
            print_inst_result(jobId, taskName, ins, dir_path)

    else:
        # get job log
        task_list_result = client.list_tasks(jobId)
        task_items = formater.items2arr(task_list_result.get('Items'))

        for task in task_items:
            taskName = task.get('TaskName')

            ins_list_result = client.list_instances(jobId, taskName)
            ins_items = formater.items2arr(ins_list_result.get('Items'))

            for ins in ins_items:
                # log
                print_ins_log(jobId, taskName, ins, stdout, stderr, log_mapping, dir_path)

                # result
                print_inst_result(jobId, taskName, ins, dir_path)


    if dir_path:
        print(green('done'))

def getLogMappingPaths(m):
    if not m:
        return []
    t = []
    for k,v in m.items():
        t.append('%s/%s' % (v, os.path.basename(k) ))
    return t


def print_inst_result(jobId, taskName, ins, dir_path):
    result = ins.get('Result')
    instId = ins.get('InstanceId')
    fileName = 'result.%s.%s.%s' % (jobId, taskName, instId)

    if dir_path:
        # write file
        print('Download %s' % white(fileName) )
        p  = os.path.join(dir_path, fileName)
        with open(p,'w') as f:
            f.write(result.dump())
    else:
        # print
        if result and (result.get('Detail')  ):
            #print(white('='*SLEN))
            print('%s [%s:%s, %s:%s]' % (bold(('Result')), blue('TaskName'), magenta(taskName), blue('InstanceId'), magenta(instId) ))
            print(white('-'*SLEN))
            if result.get('Detail') or result.get('ErrorCode'):
                print(red(result))
            else:
                print(blue(result))
            print(white('-'*SLEN))


def print_ins_log(jobId, taskName, ins, stdout, stderr, log_mapping, dir_path):

    oss_path_arr = __get_ins_oss_path(jobId, taskName, ins, stdout, stderr, log_mapping)

    if dir_path:
        for oss_path in oss_path_arr:
            download_log(oss_path, dir_path)
    else:
        for oss_path in oss_path_arr:
            print_log(taskName, ins.get('InstanceId'),oss_path)


def __get_ins_oss_path(jobId, taskName , ins, stdout, stderr, log_mapping):
    instanceId = ins['InstanceId']
    t = []

    if stdout or stderr or log_mapping:
        if stdout:
            stdout_path = formater.fix_log_path(ins['StdoutRedirectPath'],jobId,taskName, instanceId, 'stdout')
            t.append(stdout_path)
        elif stderr:
            stderr_path = formater.fix_log_path(ins['StderrRedirectPath'],jobId,taskName, instanceId, 'stderr')
            t.append(stderr_path)

        elif log_mapping:
            jobDesc = client.get_job_description(jobId)
            jobDesc = formater.to_dict(jobDesc)

            if jobDesc['Type']=='DAG':
                m = jobDesc['DAG']['Tasks'][taskName]['LogMapping']
                for localPath, ossDir in m.items():
                    t.append('%s%s.%s.%s.%s' % (ossDir, os.path.basename(localPath), jobId, taskName, instanceId))

            #else: App
    else:
        # all
        stdout_path = formater.fix_log_path(ins['StdoutRedirectPath'], jobId, taskName, instanceId, 'stdout')
        t.append(stdout_path)
        stderr_path = formater.fix_log_path(ins['StderrRedirectPath'], jobId, taskName, instanceId, 'stderr')
        t.append(stderr_path)

        jobDesc = client.get_job_description(jobId)
        jobDesc = formater.to_dict(jobDesc)

        if jobDesc['Type'] == 'DAG':
            m = jobDesc['DAG']['Tasks'][taskName]['LogMapping']
            for localPath, ossDir in m.items():
                t.append('%s%s.%s.%s.%s' % (ossDir, os.path.basename(localPath), jobId, taskName, instanceId))

    return t


def print_log(taskName, instId, oss_path):

    try:
        #file_name = oss_path[oss_path.rfind('/')+1:]
        h = oss_client.head_data(oss_path)

        if h.content_length > 1* 1024*1024:
            print('''\n  Log file is too large to preview(size=%s), you can use 'bcs o cat -h' to preview or download it manually\n  %s\n''' % (h.content_length, oss_path))
            return

        s = oss_client.get_data(oss_path)

        s = s.rstrip('\n\n')
        if len(s) > 0:
            if '/stderr.job-' in oss_path:
                type='Stderr'
                clor = yellow
            elif '/stdout.job-' in oss_path:
                type='Stdout'
                clor = green
            else:
                type = 'Log'
                clor = None

            #print(white('='*SLEN))
            print('%s [%s:%s, %s:%s]' % (bold((type)), blue('TaskName'),magenta(taskName),blue('InstanceId'), magenta(instId) ))
            print('%s' % white(oss_path))
            print(white('-'*SLEN))
            if WIN and PY2:
                print(smart_unicode.format_utf8(s))
            else:
                print(clor(s) if clor else s)
            print(white('-'*SLEN))

    except Exception as e:
        if e.status!=404 and not isinstance(e, NoSuchKey) and not isinstance(e, NoSuchBucket):
            raise e



def download_log(oss_path, dir_path):
    if not oss_path or oss_path=='':
        return
    file_name = oss_path[oss_path.rfind('/')+1:]
    print('Download %s' % white(oss_path) )

    try:
        oss_client.download_file(oss_path, os.path.join(dir_path,file_name))
    except Exception as e:
        if not isinstance(e, NoSuchKey) and not isinstance(e, NoSuchBucket):
            raise e