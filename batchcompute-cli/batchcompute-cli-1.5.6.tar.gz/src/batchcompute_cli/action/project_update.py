
from terminal import green,white
import json
from ..util import util

def update(task=None, cluster=None, docker=None):

    util.check_is_job_project()

    with open( 'job.json') as f:
        job_desc = json.loads(f.read())

    desc_map = job_desc.get('DAG').get('Tasks')

    if task:
        if not desc_map.get(task):
            raise Exception('Not found task: %s' % task)
        else:
            if cluster:
                desc_map[task] = update_cluster(task, desc_map[task], cluster)
            if docker:
                desc_map[task] = update_docker(task, desc_map[task], docker)


    else:
        for taskname in desc_map:
            if cluster:
                desc_map[taskname] = update_cluster(taskname, desc_map[taskname], cluster)
            if docker:
                desc_map[taskname] = update_docker(taskname, desc_map[taskname], docker)

    with open('job.json','w') as f:
        f.write(json.dumps(job_desc, indent=4 ))
    print(green('Done'))


def update_cluster(taskname, task, cluster):
    print('task[%s] use cluster:%s' % (taskname,cluster))

    if cluster.get('ClusterId'):
        task['ClusterId'] = cluster.get('ClusterId')
        if task.get('AutoCluster'):
            del task['AutoCluster']
    else:
        task['AutoCluster'] = cluster.get('AutoCluster')
        if task.get('ClusterId'):
            del task['ClusterId']
    return task

def update_docker(taskname, taskInfo, docker):
    print('task[%s] use docker: %s' % (taskname,docker) )
    if not taskInfo['Parameters']['Command'].get('EnvVars'):
        taskInfo['Parameters']['Command']['EnvVars'] = {}
    if docker:
        for (k,v) in docker.items():
            taskInfo['Parameters']['Command']['EnvVars'][k]=v
    return taskInfo


def trans_cluster(cluster=None):
    return util.parse_cluster_cfg(cluster)

def trans_docker(docker=None):
    return util.trans_docker(docker)
