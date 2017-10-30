import re

from . import  oss_client

def validate_job(job):
    t = []

    job_name = job.get('Name')
    if not check_JobName(job_name):
        t.append('invalid job Name: %s' % job_name)

    priority = job.get('Priority')
    if not isinstance(priority, int) or priority > 1000 or priority < 0:
        t.append('invalid Priority, it should be an integer in [0,1000]')

    #tasks
    if not job.get('DAG') or not job['DAG'].get('Tasks'):
        t.append('Not found DAG.Tasks property')

    tasks = job['DAG'].get('Tasks')

    #IMG_ARR = [n['ImageId'] for n in client.list_images()]

    # ins_type_map = it.get_ins_type_map()

    for k in tasks:
        if not check_TaskName(k):
            t.append('Invalid TaskName: %s' % k)

        if not tasks[k].get('ClusterId'):
            if not tasks[k].get('AutoCluster'):
                t.append('Invalid ClusterId or AutoCluster')
            else:
                if not tasks[k]['AutoCluster'].get('ECSImageId') and  not tasks[k]['AutoCluster'].get('ImageId'):
                    t.append('Invalid %s.AutoCluster.ECSImageId: %s' % (k, tasks[k]['AutoCluster'].get('ECSImageId') or tasks[k]['AutoCluster'].get('ImageId') ))
                # if not ins_type_map.get(tasks[k]['AutoCluster'].get('InstanceType')):
                #     t.append('Invalid %s.AutoCluster.InstanceType: %s' % (k, tasks[k]['AutoCluster'].get('InstanceType')))

        if not check_InstanceCount(tasks[k].get('InstanceCount')):
            t.append('Invalid %s.InstanceCount: %s' % (k,tasks[k].get('InstanceCount')))

        if not check_oss_path_format_if_exists(tasks[k]['Parameters']['Command'].get('PackagePath')):
            t.append('Invalid %s.Parameters.Command.PackagePath: %s'% (k,  tasks[k]['Parameters']['Command'].get('PackagePath')) )

        if not check_oss_path_format_if_exists(tasks[k]['Parameters'].get('StdoutRedirectPath')):
            t.append('Invalid %s.Parameters.StdoutRedirectPath: %s'% (k,tasks[k]['Parameters'].get('StdoutRedirectPath')) )

        if not check_oss_path_format_if_exists(tasks[k]['Parameters'].get('StderrRedirectPath')):
            t.append('Invalid %s.Parameters.StderrRedirectPath: %s'% (k,tasks[k]['Parameters'].get('StderrRedirectPath')) )


        if tasks[k].get('InputMapping'):
            mappings = tasks[k].get('InputMapping')
            for k2 in mappings:
                if not check_oss_path(k2):
                    t.append('Invalid %s.InputMapping: %s'% (k, k2) )

        if tasks[k].get('OutputMapping'):
            mappings = tasks[k].get('OutputMapping')
            for (k2,v2) in mappings.items():
                if not check_oss_path(v2):
                    t.append('Invalid %s.OutputMapping: %s'% (k, v2) )

        if tasks[k].get('LogMapping'):
            mappings = tasks[k].get('LogMapping')
            for (k2,v2) in mappings.items():
                if not check_oss_path(v2):
                    t.append('Invalid %s.LogMapping: %s'% (k, v2) )


    if len(t)==0:
        return False
    else:
        return '%s\n%s' % ('WARNING:', '\n'.join(t))


def check_JobName(job_name):
    return re.match(r'[\w\-]{1,63}$', job_name)!=None


def check_TaskName(task_name):
    return re.match(r'[\w\-]{1,63}$', task_name)!=None

# def check_ImageId(image_id, IMG_ARR):
#     return image_id in IMG_ARR

def check_InstanceCount(c):
    return isinstance(c, int) and c > 0

def check_ProgramType(type):
    return type in ['native','python','java']

def check_oss_path_format(oss):
    return oss and oss.startswith('oss://') and oss.find('/', 7)

def check_oss_path_format_if_exists(oss):
    if not oss:
        return True
    else:
        return check_oss_path_format(oss)

def check_cpu(cpu):
    return isinstance(cpu, int) and cpu >= 800

def check_memory(mem):
    return isinstance(mem, int) and mem >= 1600

def check_oss_path(p):
    if not p:
        return False

    try:
        oss_client.get_data(p)
        return True
    except:
        return False


