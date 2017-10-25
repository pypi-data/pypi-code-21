
from ..util import util
import json


def add_task(task, docker_image=None, cluster=None):
    util.check_is_job_project()

    with open('job.json') as f:
        job_desc = json.loads(f.read())

    desc_map = job_desc.get('DAG').get('Tasks')

    desc_map[task] = genTask(task, docker_image, cluster)
    print(desc_map)


def genTask(task_name, docker_image, cluster):

    return {
        "ClusterId": "",
        "InstanceCount": 1,
        "MaxRetryCount": 0,
        "Parameters": {
          "Command": {
            "CommandLine": "python %s.py" % task_name,
            "PackagePath": ""
          },
          "InputMappingConfig": {
            "Lock": True
          },
          "StderrRedirectPath": "",
          "StdoutRedirectPath": ""
        },
        "Timeout": 21600,
        "AutoCluster":cluster
    }

def trans_cluster(cluster=None):
    return util.parse_cluster_cfg(cluster)
