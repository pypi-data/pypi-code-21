"""
Task database support module.

A database which react with the following JSON format data.
JSON Format:
{
    'id': int, task id;
    'desc': str, task description;
    'data': dict, any data of specific task, e.g. sid, .sh file;
    'time_stamp': dict with:
        'create': str, time of task creation
        'start': str, time of start running
        'end': str, time of complete
    'state': str, task state
    'is_root': bool, is task is a root task, i.e. which is automitically submitted by run deamon
    'worker': str, worker of action, one of 'NoAction', 'Multithreading', 'Slurm'
    'type': str, type of task, ['Regular', 'Command', 'Script']
    'workdir': str, path of workdir,
    'dependency': list, dependency ids;    
}
"""
from .api import *
