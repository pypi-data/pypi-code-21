from ..util import util, dag, validator,list2table,formater
import json

from terminal import bold, magenta, white, blue, green, red, yellow, confirm

def status(task=None,dag_only=False, validate=True):
    task_name = task
    util.check_is_job_project()

    with open('./job.json', 'r') as f:
        obj = json.loads(f.read())

    # job Description
    print_title('Job Description:')
    print_job_desc(obj)

    #dependencies:
    deps = obj.get('DAG').get('Dependencies')
    deps = merge_deps(obj.get('DAG').get('Tasks').keys(), deps)

    matric = dag.sortIndex(deps)

    if not task_name:
        print_deps(deps, matric)

    if not dag_only:

        if task_name:
            #one task
            v = obj.get('DAG').get('Tasks').get(task_name)
            if v:
                print_title('Task Description for [%s]:' % task_name)
                print_task_desc(task_name, v)
            else:
                raise Exception('Not found task %s' % task_name)

        else:

            if not dag_only:
                #all tasks
                print_title('Task Descriptions:')
                task_descs = obj.get('DAG').get('Tasks')

                c=0
                for n in matric:
                    for n2 in n:
                        c = c+1
                        if task_descs.get(n2):
                            print_task_desc('%d.%s'% (c, n2), task_descs[n2])


    #validate
    if validate:
        msg = validator.validate_job(obj)

        if msg:
            print(yellow(msg))
        else:
            print(green('OK'))
        print('')

def print_job_desc(desc):
    t = [{
        'a': '%s: %s' % (blue('Name'), desc.get('Name')),
        "b": '%s: %s' % (blue('JobFailOnInstanceFail'), desc.get('JobFailOnInstanceFail')),
        "c": '%s: %s' % (blue('Type'), desc.get('Type')),
        "d": '%s: %s' % (blue('Priority'), desc.get('Priority'))
    }]

    list2table.print_table(t, cols=['a', 'b', 'c','d'], show_no=False, show_header=False)


    # description
    if desc.get('Description'):
        print('  %s: %s' % (blue('Description'), desc.get('Description') or ''))

def print_task_desc(task_name, taskDesc):

    # task description
    print('\n%s' % bold(magenta(task_name)))

    command = formater.to_dict(taskDesc['Parameters']['Command'])

    print('%s: %s    %s: %s    %s: %s    %s: %s' % (blue('InstanceCount'), taskDesc.get('InstanceCount'),
                                          blue('MaxRetryCount'), taskDesc.get('MaxRetryCount'),
                                          blue('Timeout'), taskDesc.get('Timeout'),
                                          blue('Cluster'), util.get_cluster_str(taskDesc)))


    print(blue('Command:'))
    print('  %s: %s' % (blue('CommandLine') , command.get('CommandLine')))
    if command.get('PackagePath'):
        print('  %s: %s' % (blue('PackagePath') , command.get('PackagePath')))
    if command.get('EnvVars'):
        print(blue('  EnvVars:'))
        for (k,v) in command['EnvVars'].items():
            print('    %s: %s' % (bold(k),v))


    print('%s: %s' % ( blue('InputMappingConfig:'),formater.to_dict( taskDesc['Parameters'].get('InputMappingConfig')) ))
    print('%s: %s' % ( blue('StdoutRedirectPath:'), taskDesc['Parameters'].get('StdoutRedirectPath') ))
    print('%s: %s' % ( blue('StderrRedirectPath:'), taskDesc['Parameters'].get('StderrRedirectPath') ))


    if taskDesc.get('InputMapping'):
        print(blue('InputMapping:'))
        for (k,v) in taskDesc['InputMapping'].items():
            print('  %s: %s' % (bold(k),v))

    if taskDesc.get('OutputMapping'):
        print(blue('OutputMapping:'))
        for (k,v) in taskDesc['OutputMapping'].items():
            print('  %s: %s' % (bold(k),v))

    if taskDesc.get('LogMapping'):
        print(blue('LogMapping:'))
        for (k,v) in taskDesc['LogMapping'].items():
            print('  %s: %s' % (bold(k),v))


def print_title(s):
    print('%s' % bold(magenta(s)))

def print_deps(deps, matric=None):
    print_title('DAG:')
    dag.draw(deps, matric)

def transform_task(task):
    if task:
        return task
    else:
        return None

def merge_deps(key_set, deps):
    uniq_set = set()
    for n in deps:
        uniq_set.add(n)
        for k in deps[n]:
            uniq_set.add(k)

    for k in key_set:
        if k not in uniq_set:
            deps[k]=[]
    return deps
