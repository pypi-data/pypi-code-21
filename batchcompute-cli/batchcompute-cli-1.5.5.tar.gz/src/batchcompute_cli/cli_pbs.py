# -*- coding: utf-8 -*-
from terminal import blue,magenta
from .externals.command import Command

from . import const,i18n_util
from .action import job_qsub,job_qstat,job_qdel,job_qhost



COMMAND = const.COMMAND
CMD = const.CMD

IMG_ID = 'img-xxxxxx'
INS_TYPE = 'ecs.s3.large'

VERSION = const.VERSION

IS_GOD = const.IS_GOD


# SPLITER = '\n    --%s' + ('-' * 40)

MSG=i18n_util.msg()


def qsub():
    cmd = Command('qsub', visible=IS_GOD,
                       arguments=['script_name'],
                       detail=MSG['qsub']['detail'],
                  spliter='\n    -----%s%s----------------' % ( blue('PBS cmd'), magenta('(Lab)')),
                       description=MSG['qsub']['description'],
                       usage='''Usage: %s qsub [-d work_path] [-e stderr_path]
                 [-j oe|eo|n] [-l resource_list] [-N job_name]
                 [-o stdout_path] [-V]
                 <script_name>

        Examples:

            1. %s qsub -l select=2:ncpus=2:mem=4gb run.pbs

            ''' % (COMMAND, CMD),

                       func=job_qsub.qsub)

    cmd.option("-d,--work_path [work_path]", MSG['qsub']['option']['d'])
    cmd.option("-e,--stderr_path [stderr_path]", MSG['qsub']['option']['e'])
    cmd.option("-j,--join [join]", MSG['qsub']['option']['j'])
    cmd.option("-l,--resource_list [resource_list]", MSG['qsub']['option']['l'])
    cmd.option("-N,--job_name [job_name]", MSG['qsub']['option']['N'])
    cmd.option("-o,--stdout_path [stdout_path]", MSG['qsub']['option']['o'])


    # unsupported
    cmd.option("-z,--zz", '', visible=False)
    cmd.option("-X,--XX", '', visible=False)
    cmd.option("-x,--xx", '', visible=False)
    cmd.option("-W,--additional_attributes [additional_attributes]", '',visible=False)
    cmd.option("-w,--wpath [path]", '',visible=False)
    cmd.option("-v,--variable_list [variable_list]", '',visible=False)
    cmd.option("-u,--user_list [user_list]", '', visible=False)
    cmd.option("-T,--prescript [pre_script_name]", '',visible=False)
    cmd.option("-t,--array_request [array_request]", '',visible=False)
    cmd.option("-S,--path_list [path_list]", '',visible=False)
    cmd.option("-r,--rerunable [rerunable]", '',visible=False)
    cmd.option("-q,--queue [destination]", '', visible=False)
    cmd.option("-P,--proxy_user [proxy_user]", '',visible=False)
    cmd.option("-p,--priority [priority]", '',visible=False)
    cmd.option("-M,--mail_user_list [mail_user_list]", '',visible=False)
    cmd.option("-m,--mail_options [mail_options]", '',visible=False)
    cmd.option("-k,--keep [keep]", '',visible=False)
    cmd.option("-I,--interactively", '',visible=False)
    cmd.option("-h,--hh", '',visible=False)
    cmd.option("-f,--ff", '',visible=False)
    cmd.option("-D,--root_path [root_path]", '',visible=False)
    cmd.option("-C,--directive_prefix", '',visible=False)
    cmd.option("-c,--checkpoint_options", '',visible=False)
    cmd.option("-b,--seconds [seconds]", '',visible=False)
    cmd.option("-A,--account_string [account_string]", '',visible=False)
    cmd.option("-a,--date_time [date_time]", '',visible=False)



    cmd.option("-V,--env", MSG['qsub']['option']['V'])
    cmd.option("--show_json",
                          MSG['qsub']['option']['show_json'])
    cmd.option("--show_opt",
                    MSG['qsub']['option']['show_opt'], visible=False)
    return cmd


def qstat():
    cmd = Command('qstat', visible=IS_GOD,
                       description=MSG['qstat']['description'],
                       usage='''Usage: %s qstat [-f][-a][-i][-r] [jobId]


        Examples:

            1. %s qstat -a  # show all jobs
            2. %s qstat -i  # show waiting jobs
            3. %s qstat -r  # show running jobs

            4. %s qstat -f 9237182319912.node32 # show job detail
            5. %s qstat -i 9237182319912.node32 # show job status
            6. %s qstat -r 9237182319912.node32 # show job status

            7. %s qstat -u user1,user2

            ''' % (COMMAND, CMD, CMD, CMD, CMD, CMD, CMD, CMD),

                       func=job_qstat.qstat)

    cmd.option("-f,--for_job_id [jobId]", MSG['qstat']['option']['f'])
    cmd.option("-a,--all", MSG['qstat']['option']['a'])
    cmd.option("-i,--waiting", MSG['qstat']['option']['i'])
    cmd.option("-r,--running", MSG['qstat']['option']['r'])
    cmd.option("-u,--user_list [user_list]", MSG['qstat']['option']['u'])  # 列出指定用户的所有作业

    cmd.option("-j,--job_id [jobId]", '', visible=False)


    cmd.option("-n,--nodes [nodes]", '',visible=False) # 列出分配给此作业的结点
    cmd.option("-s,--ss", '', visible=False) #列出队列管理员与scheduler 所提供的建议
    cmd.option("-R,--RR", '', visible=False) #列出磁盘预留信息
    cmd.option("-Q,--QQ", '', visible=False) #操作符是destination id，指明请求的是队列状态
    cmd.option("-q,--qq", '', visible=False) #列出队列状态，并以alternative 形式显示

    cmd.option("-B,--PBS", '', visible=False) #列出PBS Server 信息

    cmd.option("-x,--xx", '', visible=False)  # output xml
    cmd.option("-l,--ll", '', visible=False)  # long job name
    cmd.option("-t,--tt [tt]", '', visible=False)  # long job name
    cmd.option("-M,--mm", '', visible=False)
    cmd.option("-G,--gg", '', visible=False)
    cmd.option("-1,--one", '', visible=False)
    cmd.option("-e,--ee", '', visible=False) # PBS_QSTAT_EXECONLY


    return cmd

def qdel():
    cmd = Command('qdel', visible=IS_GOD,
                  arguments=['job_id'],
                  description=MSG['qdel']['description'],
                  usage='''Usage: %s qdel <jobId>

        Examples:

            1. %s qdel 82379939293243
            ''',
                  func=job_qdel.qdel)
    cmd.option("-W,--wait", MSG['qdel']['option']['W'])
    return cmd

def qhost():
    cmd = Command('qhost', visible=IS_GOD,
                  description=MSG['qhost']['description'],
                  usage='''unsupported yet
            ''',
                  func=job_qhost.qhost)
    return cmd

