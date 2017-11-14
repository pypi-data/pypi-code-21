# -*- coding: utf-8 -*-

from terminal import red, blue, bold, magenta, white
from .externals.command import Command


from . import const,i18n_util,cli_template,cli_oss,cli_pbs,cli_apps,cli_jobs,cli_clusters,cli_images,cli_project
from .action import login, config, info,events, instance_type,log_fetch,checker,disk_type,resource_type

import sys
import os

####################
## for debug
# from batchcompute.utils.log import get_logger
# logger = get_logger('batchcompute.test', level='DEBUG', file_name='batchcompute_python_sdk.LOG')
#####################



COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()


class Cli:
    def __help(self):
        self.program.print_help()

    def __init__(self):
        self.program = Command(COMMAND, version=VERSION,
                          title=bold(magenta('AliCloud BatchCompute CLI')),
                          usage="Usage: %s <command> [option]" % COMMAND,
                          func=self.__help,
                          help_footer=white('  type "%s [command] -h" for more' % CMD))

        # login
        cmd_login = Command('login',
                            description=MSG['login']['description'],
                            func=login.login,
                            spliter='\n    -----%s---------------------------' % blue('config'),
                            arguments=['region', 'accessKeyId', 'accessKeySecret'],
                            usage='''Usage: %s login <region> [accessKeyId] [accessKeySecret] [option]

    Examples:

        1. %s login cn-qingdao kywj6si2hkdfy9 las****bc=
        2. %s login cn-qingdao ''' % (COMMAND, CMD, CMD))
        self.program.action(cmd_login)

        # logout
        cmd_logout = Command('logout',
                                 description=MSG['logout']['description'],
                                 func=login.logout)
        self.program.action(cmd_logout)






        # set config
        cmd_config = Command('config', alias=['me','set'], description=MSG['config']['description'],
                             detail=MSG['config']['detail'],
                             usage='''Usage: %s <command> config|me|set [option]

    Examples:

        1. %s config     # show configurations
        2. %s set -r cn-qingdao -o oss://my-bucket/bcscli/ -l zh_CN
        3. %s set -i %s -t %s
        4. %s set --vpc_cidr_block 192.168.0.0/16''' % (COMMAND, CMD, CMD,CMD ,IMG_ID, INS_TYPE, CMD),
                             func=config.all)
        cmd_config.option('-r,--region [region]', MSG['config']['option']['region'])
        cmd_config.option('-o,--osspath [osspath]', MSG['config']['option']['osspath'] )
        cmd_config.option('-l,--locale [locale]', MSG['config']['option']['locale'])
        cmd_config.option('-i,--image [imageId]', MSG['config']['option']['image'])
        cmd_config.option('-t,--type [instance_type]', MSG['config']['option']['type'])
        #cmd_config.option('-c,--cluster [clusterId]', MSG['config']['option']['cluster'])
        cmd_config.option('-s,--ssl [ssl]', MSG['config']['option']['ssl'], visible=IS_GOD)
        cmd_config.option('-v,--version [version]', MSG['config']['option']['version'], visible=IS_GOD)
        cmd_config.option('-u,--qsubuser [qsubuser]', MSG['config']['option']['qsubuser'], visible=IS_GOD)
        cmd_config.option('--vpc_cidr_block [vpc_cidr_block]', MSG['config']['option']['vpc_cidr_block'])
        cmd_config.option('-g,--god [god]', MSG['config']['option']['god'], visible=IS_GOD)
        self.program.action(cmd_config)

        # info
        cmd_info = Command('info',alias=['about'], description=MSG['info']['description'],
                           visible=IS_GOD,
                             func=info.info)
        self.program.action(cmd_info)

        # resource type
        cmd_resource_type = Command('resource_type', alias=['rt', 'r'],
                                    description=MSG['resource_type']['description'],
                                    usage='''Usage: %s resource_type|rt|r [option]

            Examples:

                1. %s r ''' % (COMMAND, CMD),
                                    spliter='\n    -----%s---------------------------' % blue('query, show'),
                                    func=resource_type.list)
        cmd_resource_type.option('--show_json', MSG['resource_type']['option']['show_json'], visible=IS_GOD)
        self.program.action(cmd_resource_type)

        # instance type
        cmd_instance_type = Command('instance_type', alias=['it', 't'],
                                    description=MSG['instance_type']['description'],
                                    usage='''Usage: %s instance_type|it|t [option]

        Examples:

            1. %s it ''' % (COMMAND, CMD),
                                    func=instance_type.list)
        cmd_instance_type.option('--show_json', MSG['instance_type']['option']['show_json'], visible=IS_GOD)
        self.program.action(cmd_instance_type)


        # disk type
        cmd_disk_type = Command('disk_type', alias=['d'],
                                    description=MSG['disk_type']['description'],
                                    usage='''Usage: %s disk_type|d [option]

        Examples:

            1. %s d ''' % (COMMAND, CMD),
                                    func=disk_type.list)
        cmd_disk_type.option('--show_json', MSG['disk_type']['option']['show_json'], visible=IS_GOD)

        self.program.action(cmd_disk_type)

        # events
        cmd_events = Command('event', alias=['e'],
                                description=MSG['event']['description'],
                                usage='''Usage: %s event|e [option]

            Examples:

                1. %s e ''' % (COMMAND, CMD),
                                func=events.list)
        cmd_events.option('--show_json', MSG['event']['option']['show_json'], visible=IS_GOD)

        self.program.action(cmd_events)




        # images
        cmd_images = cli_images.images()
        self.program.action(cmd_images)

        # apps
        cmd_apps = cli_apps.apps()
        self.program.action(cmd_apps)


        ####################################
        ####################################
        ########################################
        # clusters
        cmd_clusters = cli_clusters.clusters()
        self.program.action(cmd_clusters)




        # jobs
        cmd_job = cli_jobs.jobs()
        self.program.action(cmd_job)



        # log
        cmd_log = Command('log',alias=['l'],
                          arguments=['jobId', 'taskName', 'instanceId'],
                          description=MSG['log']['description'],
                          usage='''Usage:

            %s log <jobId> [taskName] [instanceId] [options]

          Examples:
              1. %s log <jobId>                                                # show logs for all instances in a job
              2. %s log <jobId> -e                                             # show stderr log only
              3. %s log <jobId> -d /path/to/save/logs/                         # download logs for all instances in a job
              4. %s log <jobId> <taskName> -d /path/to/save/logs/              # download logs for all instances in a task
              5. %s log <jobId> <taskName> <intanceId> -d /path/to/save/logs/  # download logs for a instance
              6. %s log <No.> <No.> <intanceId> -d /path/to/save/logs/         # use <No.> instead of jobId and taskName''' % (
                          COMMAND, CMD, CMD, CMD, CMD, CMD, CMD),
                          func=log_fetch.fetch)
        cmd_log.option('-d, --dir_path [dir_path]', MSG['log']['option']['dir_path'])
        cmd_log.option('-e, --stderr', MSG['log']['option']['stderr'])
        cmd_log.option('-o, --stdout', MSG['log']['option']['stdout'])
        cmd_log.option('-m, --log_mapping', MSG['log']['option']['log_mapping'])
        self.program.action(cmd_log)

        ##################################################

        # create image
        cmd_create_image = cli_images.create()
        self.program.action(cmd_create_image)


        # delete image
        cmd_del_image = cli_images.delete()
        self.program.action(cmd_del_image)



        ##################################################

        # create cluster
        cmd_create_cluster = cli_clusters.create()
        self.program.action(cmd_create_cluster)

        # delete cluster
        cmd_del_cluster = cli_clusters.delete()
        self.program.action(cmd_del_cluster)

        # update cluster
        cmd_update_cluster = cli_clusters.update()
        self.program.action(cmd_update_cluster)

        ######################

        cmd_create_app = cli_apps.create()
        self.program.action(cmd_create_app)

        cmd_update_app = cli_apps.update()
        self.program.action(cmd_update_app)

        cmd_del_app = cli_apps.delete()
        self.program.action(cmd_del_app)

        ######################


        # create job
        cmd_create_job = cli_jobs.create()
        self.program.action(cmd_create_job)

        # restart job
        cmd_restart_job = cli_jobs.restart()
        self.program.action(cmd_restart_job)

        # stop job
        cmd_stop_job = cli_jobs.stop()
        self.program.action(cmd_stop_job)

        # delete job
        cmd_del_job = cli_jobs.delete()
        self.program.action(cmd_del_job)

        # update job
        cmd_update_job = cli_jobs.update()
        self.program.action(cmd_update_job)

        ########################################












        ##############################################

        ##############################################

        # submit job
        cmd_submit_job = cli_jobs.submit()
        self.program.action(cmd_submit_job)


        self.cmd_asub = cli_apps.asub()
        self.program.action(self.cmd_asub)

        ##############
        def cmd_oss_print_help():
            cmd_oss.print_help()

        # oss
        cmd_oss = Command('oss', alias=['o'],
                          description=MSG['oss']['description'],
                          func=cmd_oss_print_help,
                          #spliter='\n    -----%s----------------' % blue('sub-cmd')
                          )
        self.program.action(cmd_oss)

        # sub command for oss
        cli_oss.init(cmd_oss)






        # check debug
        cmd_check = Command('check', alias=['ch'],
                            arguments=['jobId'],
                            description=MSG['check']['description'],
                            usage='''Usage: %s check|ch <jobId|No.> [option]

        Examples:
            1. %s check job-0000000056D7FE9A0000368000000661
            2. %s ch 2       # use No. instead of jobId''' % (
                                COMMAND, CMD, CMD),
                            func=checker.check)
        self.program.action(cmd_check)

        ##############################################


        #################### template ###################

        cmd_template_gen = cli_template.gen()
        self.program.action(cmd_template_gen)




        #### project ##########################
        def cmd_project_print_help():
            cmd_project.print_help()

        # project
        cmd_project = Command('project', alias=['p'],
                              visible=IS_GOD,
                              description=MSG['project']['description'],
                              func=cmd_project_print_help)
        self.program.action(cmd_project)

        # sub command for project
        cli_project.init(cmd_project)
        ##########################################




        ##############################################

        # qsub
        cmd_qsub = cli_pbs.qsub()
        self.program.action(cmd_qsub)


        # qstat
        cmd_qstat = cli_pbs.qstat()
        self.program.action(cmd_qstat)

        # qdel
        cmd_qdel = cli_pbs.qdel()
        self.program.action(cmd_qdel)

        # # qhost
        cmd_qhost = cli_pbs.qhost()
        self.program.action(cmd_qhost)


    # hack: append options
    def append_options(self,arr=None):
        arr = arr or sys.argv
        if len(arr) > 1:
            if arr[1]=='asub':
                ## for asub
                if len(arr)>2 and not arr[2].startswith('-'):
                    app_name = arr[2]
                    cli_apps.asub_app_options(app_name, self.cmd_asub)
                else:
                    self.cmd_asub.option("--show_json", MSG['asub']['option']['show_json'])


        ##############################################
    def go(self, arr=None):

        if os.getenv('DEBUG'):
            self.append_options(arr)
            self.program.parse(arr)
        else:
            try:
                self.append_options(arr)
                self.program.parse(arr)
            except Exception as e:
                msg = format(e)
                print(red('\n  ERROR: %s\n' % msg))
                if '()' in msg and 'argument' in msg:
                    print(red('  add "-h" for more information\n'))


def main():

    try:
        Cli().go()
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt')

if __name__ == '__main__':
    main()


