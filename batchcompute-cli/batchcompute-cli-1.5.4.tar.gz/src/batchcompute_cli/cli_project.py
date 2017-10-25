
from .externals.command import Command
from .action import project_create,project_build,project_submit,project_status,\
    project_update
from . import i18n_util

from .const import CMD,COMMAND

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'


MSG=i18n_util.msg()


def init(cmd_project):


    # create project
    cmd_project_create = Command('create',
                             arguments=['project_name','location'],
                             description=MSG['project']['create']['description'],
                             usage='''Usage: %s project|p <project_name> [location] [option]

    Examples:

        1. %s p create log-count                   # create an empty python type project
        2. %s p create log-count ./ -t python      # create an python type project with template
        3. %s p create log-count -j job-000020212  # create a project from exists job, witch jobId is job-000020212''' % (
                             COMMAND, CMD, CMD, CMD),
                             func=project_create.create)
    cmd_project_create.option("-t, --type [type]",
                          MSG['project']['create']['option']['type'], resolve=project_create.transform_type)
    cmd_project_create.option("-j, --job [job_id]",
                          MSG['project']['create']['option']['job'], resolve=project_create.transform_job_id)
    cmd_project.action(cmd_project_create)






    # build_project
    cmd_build_project = Command('build',
                                description=MSG['project']['build']['description'],
                                func=project_build.build)
    cmd_project.action(cmd_build_project)


    # submit
    cmd_project_submit = Command('submit', description=MSG['project']['submit']['description'],
                             func=project_submit.submit)
    cmd_project.action(cmd_project_submit)


    # status
    cmd_project_status = Command('status',alias=['st'],
                            description=MSG['project']['status']['description'],
                            func=project_status.status,
    usage="""Usage: %s project|p status|st [option]

    Example:

        1. %s p st                 # show job descriptions, dag, and all task description
        2. %s p st -d              # show dag only
        3. %s p st -t [task_name]  # show the task description""" % (COMMAND, CMD, CMD, CMD) )
    cmd_project_status.option('-t, --task [task_name]', 'show description of a task')
    cmd_project_status.option('-d, --dag_only', 'show dag only')
    cmd_project.action(cmd_project_status)



    # update project
    cmd_project_update = Command('update',
                                 arguments=['task'],
                             description=MSG['project']['update']['description'],
                             usage='''Usage: %s project|p update [task] [option]

    Examples:

        1. %s p update -c img=%s:type=%s                   # update all tasks, set AutoCluster
        2. %s p update -c cls-000010102                                       # update all tasks, set ClusterId
        3. %s p update find -c cls-000010102                                  # update find task only
        4. %s p update --docker oss://your-bucket/dockers/:localhost:5000/myubuntu  # update all task use docker ''' % (
                             COMMAND, CMD, IMG_ID, INS_TYPE, CMD, CMD, CMD),
                             func=project_update.update)
    cmd_project_update.option("-c, --cluster [cluster]", MSG['project']['update']['option']['cluster'],
                              resolve=project_update.trans_cluster)
    cmd_project_update.option("--docker [docker_path]", MSG['project']['update']['option']['docker'],
                              resolve=project_update.trans_docker)
    cmd_project.action(cmd_project_update)



    # add task
    # cmd_add_task = Command('add_task', alias=['at'],
    #                         arguments=['task','cmdline'],
    #                        description=MSG['project']['add_task']['description'],
    #                        detail=MSG['project']['add_task']['detail'],
    #                        usage="""Usage: %s project|p add_task|at <task_name> [option]
    #
    #   Examples:
    #       1. %s p at Map 'python map.py'                          # add a task named Map
    #       2. %s p at Map 'python map.py' -d localhost:5000/myubuntu               # add a task named Map, use docker image
    #       3. %s p at Map 'python map.py' -c img=%s:type=ecs.s3.large     # set Auto Cluster
    #       4. %s p at Map 'python map.py' -c cls-000010102                         # use Cluster Id""" % (COMMAND, CMD, CMD,CMD,IMG_ID, CMD),
    #
    #                        func=project_task_add.add_task)
    # cmd_add_task.option('-d, --docker [docker_image]', MSG['project']['add_task']['option']['docker'])
    # cmd_add_task.option("-c, --cluster [cluster]", MSG['project']['add_task']['option']['cluster'])
    # cmd_project.action(cmd_add_task)



    # # remove task
    # cmd_remove_task = Command('rm_task', alias=['rt'], description='remove a task',
    #                           detail="remove tasks from job.json, and remove the promgram files from src folder. multiple task_name should seperated by ','.(%s)" % (RUN_IN_PROJECT_FOLDER),
    #                           usage="""Usage: %s remove_task|rt [task_name] [option]
    #
    #   Examples:
    #       1. %s rt Map  #remove task: Map
    #       2. %s rt Map,Reduce  #remove tasks: Map and Reduce""" % (COMMAND, CMD, CMD),
    #                           arguments=['task_name'],
    #                           func=remove_task.remove)
    # cmd_remove_task.option('-y, --yes', 'without confirm')
    # program.action(cmd_remove_task)
    #
    #
    #
    # # update task
    # cmd_update_task = Command('update_task', alias=['ut'], description='update a task',
    #                        detail="update a task in job.json, if argument task_name is null, it will update properties for all tasks. (%s)" % (RUN_IN_PROJECT_FOLDER),
    #                        usage="""Usage: %s update_task|ut [task_name] [option]
    #
    #   Examples:
    #       1. %s ut Map -d localhost:5000/myubuntu                                         # use docker
    #       2. %s ut Map -d false                                                           # do not use docker
    #       3. %s ut Map -i img-00000000561CB0FE000061CC00000411                            # set image id
    #       4. %s ut -i img-00000000561CB0FE000061CC00000411                                # if task_name is null, set image id for all tasks
    #       5. %s ut Map -o oss://my-bucket/my-key/                                         # set oss oss_path for Map task
    #       6. %s ut Map -m oss://my-bucket/my-key/=/home/admin/d1,oss://my-bucket/my-key2/    # set OssMapping for Map task, add oss://my-bucket/my-key/ and remove oss://my-bucket/my-key2/""" % (COMMAND, CMD, CMD, CMD, CMD, CMD, CMD),
    #                        arguments=['task_name'],
    #                        func=update_task.update)
    # cmd_update_task.option('-i, --image_id [image_id]', 'set image_id for task, type "%s img" for more' % CMD,
    #                        resolve=update_task.transform_image_id)
    # cmd_update_task.option('-d, --docker_image [docker_image_name]', 'use docker image or not, type "docker images" to show avaliable docker_image_name, if set docker_image_name to false, this task will not use docker')
    # cmd_update_task.option('-o, --oss_path [oss_path]', 'set oss path, and it will update value of PackageUri,StdoutRedirectPath and StderrRedirectPath',
    #                       resolve=update_task.transform_oss_path)
    # cmd_update_task.option('-m, --mount [oss_mapping]', 'set OssMapping for task, format: [oss_path1=directory1,...], multiple pairs should seperated by ",". if you wanna remove a item, just set empty value like: oss_path1=')
    # program.action(cmd_update_task)
    #
    #
    #
    #
    # # add dependency
    # cmd_add_dep = Command('add_dep', alias=['ad'], description='add dependencies between tasks',
    #                           detail="add dependencies to job.json.(%s)" % RUN_IN_PROJECT_FOLDER,
    #                           usage="""Usage: %s add_dep|ad [dep_pairs, multiple delimiters:','] [option]
    #
    #   Examples:
    #       1. %s ad task1:task2             #add dependency: task1-->task2
    #       2. %s ad task1:task2,task3:task4 #add dependencies: task1-->task2 and task3-->task4 """ % (COMMAND, CMD, CMD),
    #                           arguments=['dep_pairs'],
    #                           func=add_dep.add)
    # program.action(cmd_add_dep)
    #
    #
    # # remove dependency
    # cmd_remove_dep = Command('rm_dep', alias=['rd'], description='remove dependencies between tasks',
    #                           detail="remove dependencies from job.json.(%s)" % RUN_IN_PROJECT_FOLDER,
    #                           usage="""Usage: %s remove_dep|rd [dep_pairs, multiple delimiters:','] [option]
    #
    #   Examples:
    #       1. %s rd task1:task2             #remove dependency: from task1 to task2
    #       2. %s rd task1:task2,task3:task4 #remove dependencies: from task1 to task2, and from task3 to task4
    #       3. %s rd task1                   #remove dependencies from task1 to any other task""" % (COMMAND, CMD, CMD, CMD),
    #                            arguments=['dep_pairs'],
    #                           func=remove_dep.remove)
    # cmd_remove_dep.option('-y, --yes', 'without confirm')
    # program.action(cmd_remove_dep)




    # debug
    # cmd_debug_task = Command('debug_task', alias=['debug'],
    #                          description='debug task with docker image locally.',
    #                          detail='debug task with docker image locally.(%s)' % RUN_IN_PROJECT_FOLDER,
    #                          usage="""Usage: %s debug [task_name] [docker_image] [option]
    #
    #   Examples:
    #       1. %s debug Find myubuntu                                                     # debug Find task, with local docker image: myubuntu
    #       2. %s debug Find myubuntu -m /home/local/:/home/admin/d1/,/home/local2/:/home/admin/d2/   # debug task, with mock OssMapping""" % (COMMAND, CMD, CMD),
    #                          arguments=['task_name','docker_image'],
    #                          func=debug_task.debug)
    # cmd_debug_task.option('-m, --mount [mock_oss_mapping]', 'mock OssMapping, replace oss_path to a local path. multiple pairs should seperated by ",".')
    # program.action(cmd_debug_task)

