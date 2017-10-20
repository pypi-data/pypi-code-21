
from .externals.command import Command
from .action import oss_pwd,oss_upload,oss_download,oss_ls,oss_delete,oss_cat,oss_copy,oss_login
from . import i18n_util
from .const import *


MSG=i18n_util.msg()


def init(cmd_oss):
    # login
    cmd_oss_login = Command('login',
                            visible=IS_GOD,
                        description=MSG['oss']['login']['description'],
                        func=oss_login.login,
                        arguments=['region', 'accessKeyId', 'accessKeySecret'],
                        usage='''Usage: %s login <region> [accessKeyId] [accessKeySecret] [option]

    Examples:

        1. %s o login cn-qingdao kywj6si2hkdfy9 las****bc=
        2. %s o login cn-qingdao ''' % (COMMAND, CMD, CMD))
    cmd_oss.action(cmd_oss_login)

    # logout
    cmd_oss_logout = Command('logout',
                            visible=IS_GOD,
                            description=MSG['oss']['logout']['description'],
                            func=oss_login.logout)
    cmd_oss.action(cmd_oss_logout)


    # pwd
    cmd_oss_pwd = Command('pwd',
                             description=MSG['oss']['pwd']['description'],
                             func=oss_pwd.pwd)
    cmd_oss.action(cmd_oss_pwd)


     # ls
    cmd_oss_ls = Command('ls',
                         arguments=['osspath'],
                             description=MSG['oss']['ls']['description'],
                         usage="""Usage: %s oss|o ls [osspath] [option]

    Examples:

        1. %s o ls                    # list <current_osspath>, current_osspath is set by "bcs config -o <current_osspath>"
        2. %s o ls oss://bucket/abc/
        3. %s o ls ca/                # list <current_osspath>/ca/
                         """,
                             func=oss_ls.ls)
    cmd_oss_ls.option('-t, --top [num]', MSG['oss']['ls']['option']['top'])
    cmd_oss_ls.option('-n, --name [name]', MSG['oss']['ls']['option']['name'])
    cmd_oss.action(cmd_oss_ls)


     # cat
    cmd_oss_cat = Command('cat',
                             arguments=['osspath'],
                             multi_args=True,
                             description=MSG['oss']['cat']['description'],
                          usage='''Usage: %s oss|o cat <osspath>[,osspath2...] [option]

    Examples:

        1. %s o cat oss://bucket/a/b.txt  # show file content
        2. %s o cat b.txt                 # show file content, under default osspath
        3. %s o cat a.txt b.txt           # multi-file supported
        4. %s o cat a.txt -r 100:1024     # get range
                          '''  % (COMMAND, CMD, CMD, CMD, CMD),
                             func=oss_cat.cat)
    cmd_oss_cat.option('-r, --byte_range [byte_range]', MSG['oss']['cat']['option']['byte_range'], resolve=oss_cat.trans_byte_range)
    cmd_oss.action(cmd_oss_cat)

    # copy
    cmd_oss_copy = Command('copy', alias=['cp'],
                          arguments=['source', 'target'],
                          description=MSG['oss']['copy']['description'],
                           detail=MSG['oss']['copy']['detail'],
                           usage='''Usage: %s oss|o copy|cp <source> <target> [option]

    Examples:

        1. %s o cp oss://bucket/a/b.txt oss://bucket/c/   # copy file into folder, result: oss://bucket/c/b.txt
        2. %s o cp b.txt d.txt                            # copy file, under default osspath
        3. %s o cp a/ cn-hangzhou#oss://bucket2/c/        # copy folder to another oss folder across region
                          ''' % (COMMAND, CMD, CMD, CMD),
                          func=oss_copy.copy)
    cmd_oss.action(cmd_oss_copy)

    # upload
    cmd_oss_upload = Command('upload', alias=['up'],
                             arguments=['localpath','osspath'],
                             description=MSG['oss']['upload']['description'],
                             usage='''Usage: %s oss|o upload|up <filename> <osspath> [option]

    Examples:

        1. %s o upload ./worker.tar.gz  oss://my-bucket/abc/worker.tar.gz # upload file
        2. %s o upload ./abc/  oss://my-bucket/abc/                       # upload folder''' % (
                             COMMAND,CMD,CMD),
                             func=oss_upload.upload)
    cmd_oss_upload.option("-p, --use_put_object",
                              MSG['oss']['upload']['option']['use_put_object'])
    cmd_oss.action(cmd_oss_upload)


    # download
    cmd_oss_download = Command('download',alias=['down'],
                             arguments=['osspath','localpath'],
                             description=MSG['oss']['download']['description'],
                             usage='''Usage: %s oss|o download|down <osspath> <filename> [option]

    Examples:

        1. %s o download oss://my-bucket/abc/worker.tar.gz # download to ./
        2. %s o download oss://my-bucket/abc/  ./abc/      # download to ./abc/''' % (
                             COMMAND,CMD,CMD),
                             func=oss_download.download)
    cmd_oss.action(cmd_oss_download)


     # remove
    cmd_oss_delete = Command('delete',alias=['del'],
                             arguments=['osspath'],
                             description=MSG['oss']['delete']['description'],
                             usage='''Usage: %s oss|o delete|del <osspath> [option]

    Examples:

        1. %s o del oss://my-bucket/abc/worker.tar.gz
        2. %s o del oss://my-bucket/abc/               # delete folder''' % (
                             COMMAND,CMD,CMD),
                             func=oss_delete.delete)
    cmd_oss_delete.option('-y, --yes', MSG['oss']['delete']['option']['yes'])
    cmd_oss.action(cmd_oss_delete)
