# -*- coding: utf-8 -*-
from terminal import blue,red
from .externals.command import Command

from . import const,i18n_util
from .action import job,job_create,job_restart,job_stop,job_delete,job_update,job_submit


COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()

def submit():
    cmd_submit_job = Command('submit', alias=['sub'],
                             arguments=['cmd', 'job_name'],
                             description=MSG['submit']['description'],
                             usage='''Usage: %s submit|sub <cmd> [job_name] [option]

        Examples:

            1. %s sub "echo 'hello'" -n 3 -f                                                    # run this cmd on 3 machines(instances) in force mode
            2. %s sub "echo 'hello'" -c img=%s                                         # use auto cluster, or -i %s
            3. %s sub "python main.py arg1 arg2" job_name -c cls-xxxxx -p ./my_program/         # set job name, use cluster id, pack a folder and upload
            4. %s sub "python /home/admin/test/main.py" -m oss://bucket/a/b/:/home/admin/test/  # mount an oss path to a local path
            5. %s sub "python test.py" -p test.py --docker myubuntu@oss://bucket/dockers/       # run in docker container
            6. %s sub --file job.cfg                    # submit a job from job.cfg
            7. %s sub --notification_topic my-mns-topic --notification_events OnTaskStopped,OnJobFailed  --notification_endpoint <your_mns_endpoint>          # set notification
            ''' % (
                                     COMMAND, CMD, CMD, IMG_ID, IMG_ID, CMD, CMD, CMD, CMD, CMD),
                                 spliter='\n    -----%s----------------' % blue('quick cmd'),
                                 func=job_submit.submit)


    cmd_submit_job.option("-n, --nodes [machine_number]", MSG['submit']['option']['nodes'])
    cmd_submit_job.option("-f, --force", MSG['submit']['option']['force'])
    cmd_submit_job.option("--auto_release", MSG['submit']['option']['auto_release'])
    cmd_submit_job.option("-d, --description [description]", MSG['submit']['option']['description'])

    cmd_submit_job.option("-p, --pack [folder_path]", MSG['submit']['option']['pack'])
    cmd_submit_job.option("--priority [priority]", MSG['submit']['option']['priority'])

    cmd_submit_job.option("--timeout [seconds]", MSG['submit']['option']['timeout'])

    cmd_submit_job.option("-c, --cluster [cluster]", MSG['submit']['option']['cluster'])
    cmd_submit_job.option('-i, --image [imageId]', MSG['submit']['option']['image'])
    cmd_submit_job.option('-t, --type [type]', MSG['submit']['option']['type'])
    cmd_submit_job.option("-e, --env [kv_pairs]", MSG['submit']['option']['env'])
    cmd_submit_job.option("-r, --read_mount [kv_pairs]", MSG['submit']['option']['read_mount'])
    cmd_submit_job.option("-w, --write_mount [kv_pairs]", MSG['submit']['option']['write_mount'])
    cmd_submit_job.option("-m, --mount [kv_pairs]", '(%s) %s' % (red(MSG['changed']), MSG['submit']['option']['mount']))

    cmd_submit_job.option("--nas_access_group [nas_access_group]",
                          MSG['submit']['option']['nas_access_group'])

    cmd_submit_job.option("--nas_file_system [nas_file_system]", MSG['submit']['option']['nas_file_system'])

    cmd_submit_job.option("--docker [docker]", MSG['submit']['option']['docker'])
    cmd_submit_job.option("-u,--user_data [kv_pairs]", MSG['submit']['option']['user_data'])

    cmd_submit_job.option("--resource_type [resource_type]",
                          MSG['submit']['option']['resource_type'])
    cmd_submit_job.option("--spot_price_limit [spot_price_limit]",
                          MSG['submit']['option']['spot_price_limit'])

    cmd_submit_job.option("--disk [disk_configs]",
                          MSG['submit']['option']['disk'],
                          resolve=job_submit.trans_disk)
    cmd_submit_job.option("--lock", MSG['submit']['option']['lock'])
    cmd_submit_job.option("--locale [locale]", MSG['submit']['option']['locale'])
    cmd_submit_job.option("--file [file]", MSG['submit']['option']['file'])
    cmd_submit_job.option("--notification_endpoint [mns_endpoint]", MSG['submit']['option']['notification_endpoint'])
    cmd_submit_job.option("--notification_topic [mns_topic]", MSG['submit']['option']['notification_topic'])
    cmd_submit_job.option("--notification_events [job_events]", MSG['submit']['option']['notification_events'],
                          resolve=job_submit.trans_notification_events)
    cmd_submit_job.option("--reserve_on_fail", MSG['submit']['option']['reserve_on_fail'])
    cmd_submit_job.option("--no_cache_support", MSG['submit']['option']['no_cache_support'])

    cmd_submit_job.option("--vpc_cidr_block [vpc_cidr_block]",
                          MSG['submit']['option']['vpc_cidr_block'])
    cmd_submit_job.option("--vpc_id [vpc_id]",
                          MSG['submit']['option']['vpc_id'])

    cmd_submit_job.option("--show_json",
                          MSG['submit']['option']['show_json'])
    cmd_submit_job.option("--show_dag",
                          MSG['submit']['option']['show_dag'])
    return cmd_submit_job



def update():
    # update job
    cmd_update_job = Command('update_job', alias=['uj'],
                             arguments=['jobId', 'groupName'],
                             description=MSG['update_job']['description'],
                             usage='''Usage: %s update_job|uj <jobId> [option]

    Examples:

        1. %s uj job-idxxx1 -p 2   #update job set priority=2''' % (COMMAND, CMD),
                             func=job_update.update)
    cmd_update_job.option("-y, --yes", MSG['update_job']['option']['yes'])
    cmd_update_job.option("-p, --priority <priority>", MSG['update_job']['option']['priority'])
    return cmd_update_job

def delete():
    cmd_del_job = Command('delete_job', alias=['dj'],
                          arguments=['jobId'],
                          description=MSG['delete_job']['description'],
                          usage='''Usage: %s delete_job|dj [jobId,jobId2,jobId3...] [option]

    Examples:

        1. %s dj job-idxxx1             # delete job with jobId
        2. %s dj job-idxxx1,job-idxxx2  # delete job with jobIds''' % (COMMAND, CMD, CMD),
                          func=job_delete.del_job)


    cmd_del_job.option("-y, --yes", MSG['delete_job']['option']['yes'])
    return cmd_del_job

def stop():
    cmd_stop_job = Command('stop_job', alias=['sj'],
                           arguments=['jobId'],
                           description=MSG['stop_job']['description'],
                           usage='''Usage: %s stop_job|sj [jobId,jobId2,jobId3...] [option]

    Examples:

        1. %s sj job-idxxx1             # stop job with jobId
        2. %s sj job-idxxx1,job-idxxx2  # stop job with jobIds''' % (COMMAND, CMD, CMD),
                           func=job_stop.stop_job)


    cmd_stop_job.option("-y, --yes", MSG['stop_job']['option']['yes'])
    return cmd_stop_job

def restart():
    # restart job
    cmd_restart_job = Command('restart_job', alias=['rj'],
                              arguments=['jobId'],
                              description=MSG['restart_job']['description'],
                              usage='''Usage: %s restart_job|rj [jobId,jobId2,jobId3...] [option]

    Examples:

        1. %s rj job-idxxx1             # restart job with jobId
        2. %s rj job-idxxx1,job-idxxx2  # restart job with jobIds''' % (COMMAND, CMD, CMD),
                              func=job_restart.restart_job)
    cmd_restart_job.option("-y, --yes", MSG['restart_job']['option']['yes'])
    return cmd_restart_job


def create():
    cmd_create_job = Command('create_job', alias=['cj'],
                             arguments=['jsonString'],
                             spliter=' ',
                             description=MSG['create_job']['description'],
                             usage='''Usage: %s create_job|cj [jsonString] [option]

    Examples:

        1. %s cj "{\\"Name\\":......}"    #create job from json string
        2. %s cj -f /path/to/job.json   #create job from json file path''' % (COMMAND, CMD, CMD),
                             func=job_create.create)


    cmd_create_job.option("-f, --filePath [filePath]", MSG['create_job']['option']['filePath'])
    return cmd_create_job

def jobs():
    cmd_job = Command('job', alias=['j'],
                      arguments=['jobId', 'taskName', 'instanceId', 'logType'],
                      description=MSG['job']['description'],
                      usage='''Usage:

    %s job|j [jobId|No.] [taskName|No.] [instanceId] [options]

    Examples:

        list jobs:
          1. %s job|j -t [num] -s [state] -i [jobId] -n [jobName]
          2. %s j                     # show top 10 (default)
          3. %s j -t 50               # show top 50
          4. %s j -a                  # show all
          5. %s j -s Running,Waiting  # show those state is Running or Waiting
          6. %s j -n abc              # show those jobName contains "abc"
          7. %s j -i 0018             # show those jobId contains "0018"

        get job detail:
          1. %s j <jobId>
          2. %s j <jobId> -d          # show job description only
          3. %s j <No.>               # use <No.> instead of <job-id>, this command must run after %s j

        get task detail:
          1. %s j <jobId> <taskName>
          2. %s j <No.> <No.>            #use <No.> instead of <jobId> and <taskName>

        get instance detail:
          1. %s j <jobId> <taskName> <instanceId>
          2. %s j <No.> <No.> <instanceId>         #use <No.> instead of <jobId> and <taskName>''' % (
                          COMMAND, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD, CMD),
                      func=job.all)


    cmd_job.option('-t, --top [num]', MSG['job']['option']['top'])
    cmd_job.option('-a, --all', MSG['job']['option']['all'])
    cmd_job.option('-s, --state [state]', MSG['job']['option']['state'])
    cmd_job.option('-i, --id [jobId]', MSG['job']['option']['id'])
    cmd_job.option('-n, --name [jobName]', MSG['job']['option']['name'])
    cmd_job.option('-d, --description', MSG['job']['option']['description'])
    cmd_job.option('--show_json', MSG['job']['option']['show_json'], visible=IS_GOD)
    return cmd_job



