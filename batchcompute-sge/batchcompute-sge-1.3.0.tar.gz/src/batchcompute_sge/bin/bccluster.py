from terminal import red, blue, bold, magenta, white
from ..externals.command import Command
from ..actions import login, lists, cluster,config
from .. import const
from ..lib import bccluster_json
import os
import sys
from ..util.debugger import *

COMMAND = const.COMMAND
CMD = const.CMD
VERSION = const.VERSION



IS_GOD =  bccluster_json.get().get('god') or False


class Cli:
    def __help(self):
        self.program.print_help()

    def __init__(self):
        self.program = Command(CMD, version=VERSION,
                          title=bold(magenta('Alibaba Cloud BatchCompute SGE')),
                          usage='''Usage: %s|%s <command> [option]''' % (COMMAND , CMD),
                          func=self.__help,
                          help_footer=white('  type "%s [command] -h" for more' % CMD))

        ####### login #####################
        cmd_login = Command('login',
                            description='''login with accessKey''',
                            func=login.login,
                            #spliter='\n',
                            arguments=['region', 'accessKeyId', 'accessKeySecret','oxsRegion', 'oxsAccessKeyId', 'oxsAccessKeySecret'],
                            usage='''Usage: %s login <region> [accessKeyId] [accessKeySecret] [option]

    Examples:

        1. %s login cn-qingdao kywj6si2hkdfy9 las****bc=
        2. %s login cn-qingdao kywj6si2hkdfy9
        3. %s login cn-qingdao ''' % (CMD, CMD, CMD, CMD))
        self.program.action(cmd_login)

        ####### config #####################
        cmd_config = Command('config', alias=[],
                            description='''show config''',
                            func=config.config)

        cmd_config.option('-p,--bcs_port [bcs_port]',
                          '''optional, set port for BatchCompute endpoint''' , visible=IS_GOD)
        cmd_config.option('-g,--god [god]',
                          '''optional, in god mod''', visible=IS_GOD)
        self.program.action(cmd_config)




        ####### create #####################
        cmd_create = Command('start',
                             description='''start cluster''',
                             func=cluster.start,
                             usage='''Usage: %s create [option]

    Examples:

        1. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx
        2. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx --vpc_cidr_block 192.168.1.0/24
        3. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx -d system:ephemeral:40,data:cloud:50:/home/disk1
        4. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx -d system:ephemeral:40
        5. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx -d data:cloud:50:/home/disk1
        6. %s start -n 2 -t ecs.sn1.medium -i img-xxxxxx -m nas://a/b/c:/home/nas/,oss://bucket/key:/home/oss/''' % (CMD, CMD, CMD, CMD, CMD, CMD, CMD))
        cmd_create.option('-n,--nodes <vm_count>', 'required, the number of worker VM to be started', resolve=cluster.trans_nodes)
        cmd_create.option('-t,--type <instance_type>', '''required, available instance-type, type '%s t' for more''' % CMD)
        cmd_create.option('-i,--image <image_id>', '''required, available image id''')

        cmd_create.option('-d,--disk [disk_config]', '''optional, mount system disk and a data disk(optional), only works with AutoCluster.
                                              Usage: "--disk system:default:40,data:cloud:50:/home/disk1".
                                              Default: system:default:40, mount 40GB default disk as system disk.
                                              System disk config format: system:<default|cloud|ephemeral...>:<40-500>,
                                              example: system:cloud:40, mount 40GB ephemeral disk as system disk.
                                              Data disk config format: data:<default|cloud|ephemeral...>:<5-2000>:<mount-point>,
                                              example: data:cloud:5:/home/disk1, mount a 5GB cloud disk as data disk,
                                              in windows must mount to driver, such as E driver, like: "data:cloud:5:E".
                                              (Attention please: Using ephemeral disk as data disk, the size scope should limit to [5-1024]GB).
                                              (type 'bcc d' for more available diskTypes).''', resolve=cluster.trans_disk)
        cmd_create.option('-m,--mount [kv_pairs]', '''optional,mount nas path to local file system in read/write mode,
                                              or mount oss path to local file system in read mode.
                                              format: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                              example: nas://path/to/mount/:/home/admin/dir/.
                                              and it is always using with nas_access_group and nas_file_system.
                                              example2: oss://path/to/mount/:/home/admin/dir/,
                                              and file is also supported: oss://path/to/mount/a.txt:/home/admin/dir/a.txt.''', resolve=cluster.trans_mount)

        cmd_create.option("--nas_access_group [nas_access_group]", '''optional, NAS access groups, multiple items should be separated by comma''')

        cmd_create.option("--nas_file_system [nas_file_system]", '''optional, NAS file system, multiple items should be separated by comma''')
        cmd_create.option("--no_cache_support", '''optional, cancel the cache for ossmounter''')
        cmd_create.option("--vpc_cidr_block [vpc_cidr_block]", '''CIDR, such as: 192.168.1.0/24. if you are in a VPC environment, this option is required''')
        cmd_create.option("--show_json", 'optional, just show json', visible=IS_GOD)

        self.program.action(cmd_create)

        ####### status #####################
        cmd_status = Command('status',
                           description='''Show cluster status''',
                           func=cluster.status)
        cmd_status.option("-l,--log", 'optional, show oplog', visible=IS_GOD)
        self.program.action(cmd_status)

        ####### resize #####################
        cmd_resize = Command('resize',
                             arguments=['nodes'],
                              description='''resize cluster''',
                             usage='''Usage: %s resize <nodes> [option]

    Examples:

        1. %s resize 0   # resize to 0
        2. %s resize 12  # resize to 12
                             ''' % (CMD, CMD, CMD),
                              func=cluster.resize)
        self.program.action(cmd_resize)

        ####### create #####################
        cmd_release = Command('stop',
                             description='''stop cluster''',
                             func=cluster.stop)
        self.program.action(cmd_release)





        ####### instance type #####################
        cmd_type = Command('type',
                           alias=['t'],
                           spliter='    -------------',
                           description='''Show available instance types''',
                           func=lists.list_instance_types)
        self.program.action(cmd_type)

        ####### disk types #####################
        cmd_disk = Command('disk',
                           alias=['d'],
                           description='''Show available disk types''',
                           func=lists.list_disks)
        self.program.action(cmd_disk)

    ##############################################

    def go(self, arr=None):

        try:
            self.program.parse(arr)
        except Exception as e:
            dstack()

            msg = format(e)
            print(red('\n  ERROR: %s\n' % msg))
            if '()' in msg and 'argument' in msg:
                print(red('  add "-h" for more information\n'))
            sys.exit(1)




def main():
    try:
        Cli().go()
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt')
        sys.exit(1)

if __name__ == '__main__':
    main()


