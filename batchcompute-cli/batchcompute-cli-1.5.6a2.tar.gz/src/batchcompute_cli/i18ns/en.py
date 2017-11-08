# -*- coding: utf-8 -*-
from ..const import CMD
from terminal import magenta

IMG_ID = 'img-ubuntu'
INS_TYPE = 'ecs.s3.large'

def getJSON():
    return {
        "changed": 'changed',
        "login": {
            "description": "login with Aliyun AccessKey"
        },
        "logout": {
            "description": "logout, will delete accessKey and secret in local config file"
        },
        "config": {
            "description": "read and write configurations",
            "detail": "set configurations, show configurations if no options",
            "option": {
                "region": 'set region, example: cn-qingdao',
                "osspath": 'set default oss path',
                "locale": 'set locale, scope:[zh_CN|en]',
                "image": "set default image Id, type '%s i' for more image" % CMD,
                "type": "set default InstanceType, type '%s t' for more instanceType" % (CMD),
                'cluster': '''set default cluster, type '%s c' for more clsuter.''' % (CMD),
                'version': "set version for stg environment, example: 2015-10-01",
                "god": "use god mode, scope:[true|false]",
                'ssl': 'requesting with https, scope:[true|false]',
                'qsubuser': 'set user for qsub, if unspecified, default:root',
                'vpc_cidr_block': '''specify CIDR IP block for VPC, usually: 192.168.0.0/16,
                                       if you don't specify or it is set to false, then use the classic network'''
            }
        },
        'info': {
            "description": "show information of batchcompute-cli",
            "latest_version": "Latest version",
            "current_version": "Current version",
            "has_upgrade": "Type 'pip install -U batchcompute-cli' to upgrade",
            "has_upgrade2":  "If fails with permission deny, try 'sudo pip install -U batchcompute-cli'"
        },
         "image": {
            "description": 'show available images.',
             'option': {
                 'description': 'show description of the cluster',
                 'show_json': 'show json'
             }
        },
        "app": {
            "description": 'show available apps.',
            "option": {
                "public": 'get public Apps, it works only if you are getting App detail',
                "description": "show json only"
            }
        },
        "disk_type": {
            "description": 'show available disk types.',
             'option': {
                 'show_json': 'show json'
             }
        },
        "instance_type": {
            "description": 'show available instance types.',
             'option': {
                 'show_json': 'show json'
             }
        },
        "resource_type": {
            "description": 'show available resource types.',
             'option': {
                 'show_json': 'show json'
             }
        },
        "event": {
            "description": 'show available events.',
             'option': {
                 'show_json': 'show json'
             }
        },
        "cluster": {
            "description": 'show cluster list, show cluster detail.',
            "option": {
                'description': 'show description of the cluster',
                'oplog' :'show operation logs. It works for showing cluster detail only.',
                'show_json': 'show json',
            }
        },
        "job": {
            "description": 'show job list, show detail of job and task',
            "option": {
                'top': 'length of result-set to show, works only in list jobs',
                'all': 'show all jobs',
                'state': 'state filter for listing jobs, scope: [Running|Stopped|Waiting|Finished|Failed]',
                "id": 'jobId filter for listing jobs',
                'name': 'jobName filter for listing jobs',
                'description': 'show description of the job',
                'show_json': 'show json'
            }
        },
        'log': {
            'description': 'print logs, or download them from oss to local directory',
            'option': {
                'dir_path': 'directory path to save logs, if your don\'t set this option, just print logs',
                'stderr': 'show stderr log only',
                'stdout': 'show stdout log only',
                'log_mapping': 'show log_mapping logs only'
            }
        },
        'create_image': {
            'description': 'register image',
            'option': {
                'platform': "optional, scope:[Linux|Windows], default: Linux",
                'description': "optional, descriptino, string",
                'show_json': 'optional, just output image json, won\'t create a image, default: false'
            }
        },
        'delete_image': {
            'description': 'unregister image, multi-supported',
            'option': {
                'yes': "optional, do it in silent mode"
            }
        },
        'create_cluster': {
            'description': 'create cluster',
            'option': {
                'image': "optional, imageId, type '%s t' for more" % CMD,
                'type': "optional, instanceType, type '%s t' for more" % (CMD),
                'nodes': "optional, int, default: 1",
                #'groups': "optional, format: <groupName>[:type=<instanceType>][:nodes=<instanceCount>], default:group1",
                'description': "optional, description, string",
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'user_data': "optional, user data k-v pairs, exp: a:b,c:e",
                'resource_type': 'optional, default "OnDemand", scope: [OnDemand|Spot]',
                'spot_price_limit': 'optional, it\'s available when resource_type is Spot(unit: yuan,works to three decimal places). Set to 0 means using the system automatically bid(But lower than the "OnDemand" price)',
                'disk': """optional, mount system disk and a data disk(optional)Usage: "--disk system:default:40,data:cloud:50:/home/disk1".
                                             Default: system:default:40, mount 40GB default disk as system disk.
                                             System disk config format: system:<default|cloud|ephemeral...>:<40-500>,
                                             example: system:cloud:40, mount 40GB ephemeral disk as system disk.
                                             Data disk config format: data:<default|cloud|ephemeral...>:<5-2000>:<mount-point>,
                                             example: data:cloud:5:/home/disk1, mount a 5GB cloud disk as data disk,
                                             in windows must mount to driver, such as E driver, like: "data:cloud:5:E".
                                             (Attention please: Using ephemeral disk as data disk, the size scope should limit to [5-1024]GB).
                                             (type '%s d' for more available diskTypes).
        """ % CMD,
                'notification_events': "Events for notification, type '%s e' for more." % CMD,
                'notification_topic': "Topic name in MNS.",
                'notification_endpoint': "MNS Endpoint, see in MNS web console.",
                'mount': """optional,mount nas path to local file system in read/write mode,
                                             or mount oss path to local file system in read mode.
                                             format: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                             example: nas://path/to/mount/:/home/admin/dir/.
                                             and it is always using with nas_access_group and nas_file_system.
                                             example2: oss://path/to/mount/:/home/admin/dir/,
                                             and file is also supported: oss://path/to/mount/a.txt:/home/admin/dir/a.txt.""",
                'nas_access_group': 'NAS access groups, multiple items should be separated by comma',
                'nas_file_system': 'NAS file system, multiple items should be separated by comma',
                'no_cache_support': 'optional, cancel the cache for ossmounter',
                'vpc_cidr_block': 'CIDR, such as: 192.168.0.0/16',
                'vpc_id': 'set VPC id',
                'show_json': 'optional, just output cluster json, won\'t create a cluster, default: false',
                'filePath': 'submit with a cluster description json file, other options are invalid'
            }
        },
        'delete_cluster': {
            'description': 'delete cluster, multi-supported',
            'option': {
                'yes': "optional, delete in silent mode"
            }
        },
        'update_cluster': {
            'description': 'update cluster, only support updating DesiredVMCount currently',
            'option': {
                'yes': "optional, update in silent mode",
                'nodes': "required, should be positive integer",
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'user_data': "optional, user data k-v pairs, exp: a:b,c:e",
                'spot_price_limit': 'optional, it\'s available when resource_type is Spot(unit: yuan,works to three decimal places). Set to 0 means using the system automatically bid(But lower than the "OnDemand" price)',
                'mount': """optional,mount nas path to local file system in read/write mode,
                                             or mount oss path to local file system in read mode.
                                             format: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                             example: nas://path/to/mount/:/home/admin/dir/.
                                             and it is always using with nas_access_group and nas_file_system.
                                             example2: oss://path/to/mount/:/home/admin/dir/,
                                             and file is also supported: oss://path/to/mount/a.txt:/home/admin/dir/a.txt.""",
                'image': "optional, imageId, type '%s t' for more" % CMD,
                'show_json': 'optional, just output cluster json, won\'t create a cluster, default: false'
            }
        },
        "create_app": {
            'description': 'create App',
            "option": {
                'file': 'optional, create an app with app description json file',
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'docker': """optional,optional, use docker, format: <docker_image_name>@<docker_storage_oss_path>,
                                          example: localhost:5000/myubuntu@oss://bucket/dockers/
                                          or for short: myubuntu@oss://bucket/dockers/ """,
                'image': "optional, imageId, type '%s t' for more" % CMD,


                'type': "optional, instanceType, type '%s t' for more , format:  {defaultValue}:{overwritable}:{desc}" % (CMD),
                'resource_type': 'optional, default: "OnDemand", scope:[OnDemand|Spot] , format: {defaultValue}:{overwritable}:{desc}',
                'nodes': "optional, instance counts, format:  {defaultValue}:{overwritable}:{desc}",
                'disk_type': '''optional, system disk type(type '%s d' for more), format: {defaultValue}:{overwritable}:{desc}''' % CMD,
                'min_disk_size': 'optional, System disk minimum limit, unit: GB, format: {defaultValue}:{overwritable}:{desc}',
                'max_retry_count': 'optional, After an Instance failed, the maximum number of retries, format: {defaultValue}:{overwritable}:{desc}',
                'timeout': "optional,job would failed if it had expired, default: 86400(1 days).format: {defaultValue}:{overwritable}:{desc}",

                'inputs': '''optional, input parameters, format: item1,item2..,
                                          eash item format: {name}[:{type}][:{localpath}][:{desc}][:{defaultValue}]''',
                'outputs': '''optional, outout parameters, format: item1,item2..,
                                          eash item format: {name}[:{type}][:{localpath}][:{desc}]''',

                'daemonize': 'When the application is executed, whether to restart each time. default：false',
                'description': 'optional, description of the App',

                'show_json': 'optional, just output App json, won\'t create an App, default: false'
            }
        },
        "update_app": {
            'description': 'update App. ',
            "option": {
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'docker': """optional,optional, use docker, format: <docker_image_name>@<docker_storage_oss_path>,
                                      example: localhost:5000/myubuntu@oss://bucket/dockers/
                                      or for short: myubuntu@oss://bucket/dockers/ """,
                'image': "optional, imageId, type '%s t' for more" % CMD,

                'daemonize': 'When the application is executed, whether to restart each time. default：false',
                'description': 'optional, description of the App',
                'yes': "optional, update in silent mode",

                'show_json': 'optional, just output App json, won\'t create an App, default: false'
            }
        },
        'delete_app': {
           'description': 'Delete App',
            'option': {
                'yes': 'optional, delete apps in silent mode'
            }
        },
        "asub": {
            'description': 'submit an App job',
            "option": {
                'type': "optional, instanceType, type '%s t' for more" % ( CMD),
                'resource_type': 'optional, default: "OnDemand", scope:[OnDemand|Spot]',
                'nodes': "optional, instance counts",
                'disk_type': '''optional, system disk type(type '%s d' for more)''' % CMD,
                'min_disk_size': 'optional, System disk minimum limit, unit: GB ',
                'max_retry_count': 'optional, After an Instance failed, the maximum number of retries ',
                'timeout': "optional, job would failed if it had expired, default: 86400(1 days) ",
                'description': 'optional, description for the job',
                'config': 'optional, k-v pairs in config, format: k=v[,k2=v2][,k3=v3]...',
                'show_json': '''optional, just output the json, won\'t create a job, default: false\n''',
                'param_desc': '''**********************************************
        These options bellow are special parameters of this App
        Input parameter starts with --input_, and you can change to --input_from_file_ if necessary.
        Ouput parameter starts with --output_.
        **********************************************
                    ''',
                'inputs': '''If suffix is //:oss, it will generate oss path automaticly,
                                 and file will be upload to oss automaticly to, such as: --iWDL hello.wdl//:oss''',
                'outputs': '''If suffix is //:oss, it will generate oss path automaticly, such as: --iWDL ./demo///:oss'''
            }
        },
        'create_job': {
            'description': 'create job from description json or a json file path.',
            'option': {
                'filePath': 'local job description json file path'
            }
        },
        'restart_job': {
            'description': 'restart jobs, multi-supported',
            'option': {
                'yes': "optional, restart jobs in silent mode"
            }
        },
        'stop_job': {
            'description': 'stop jobs, multi-supported',
            'option': {
                'yes': "optional, stop jobs in silent mode"
            }
        },
        'delete_job': {
            'description': 'delete jobs, multi-supported',
            'option': {
                'yes': "optional, delete jobs in silent mode"
            }
        },
        'update_job': {
            'description': 'update job, only support update priority currently',
            'option': {
                'yes': "optional, update in silent mode",
                'priority': "required, should be in scope [1..1000]"
            }
        },
        'submit': {
            'description': 'submit a single task job quickly',
            'option': {
                'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                                             default value is an auto_cluster string: img=%s:type=%s.
                                             you can use a exists cluster(type '%s c' for more cluster id),
                                             or use auto cluster, format: img=<imageId>:type=<instanceType>
                                             (type '%s i' for more images)
                                             (type '%s t' for more available instanceTypes). """ % (
                IMG_ID, INS_TYPE, CMD, CMD, CMD),
                'pack': "optional,pack the files in the program_folder into worker.tar.gz, and upload to oss, if you don't set this option, no pack, no upload",
                'priority': 'optional,int,job priority,default:0\n',
                'timeout': "optional,job would failed if it had expired, default: 86400(1 days)",
                'image': """optional, set autoCluster image id, priority is higher than auto_cluster string set by cluster option,
                                             and it doesn't work when clusterId is set by cluster option""",
                'type': """optional, set autoCluster instance type, priority is higher than auto_cluster string set by cluster option,
                                             and it doesn't work when clusterId is set by cluster option""",
                'nodes': "optional,the number of machines you needed to run the program, default: 1",
                'description': 'optional,set job description',
                'force': "optional,job don't fail when instance were failed, default: job fail when even one instance were failed",
                'auto_release': "optional, job will be released (deleted) when finished(job.state=='finished')",
                'env': "optional,set environment variables, format: <k>:<v>[,<k2>:<v2>...]",
                'read_mount': """optional,mount a oss path to local file system in read-only mode, kv-pairs, multi-supported,
                                             format: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                             mount folder example: oss://bucket/key/:/home/admin/ossdir/,
                                             mount file example: oss://bucket/key1:/home/admin/key1 """,
                'write_mount': """optional,mount a oss path to local file system in writable mode
                                             (files in the mounted folder will be upload to oss_path after the task is finished),
                                             kv-pairs, multi-supported, format: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                             example: oss://bucket/key:/home/admin/ossdir """,

                'mount': """optional,mount nas path to local file system in read/write mode,
                                             or mount oss path to local file system in read mode.
                                             format: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                             example: nas://path/to/mount/:/home/admin/dir/.
                                             and it is always using with nas_access_group and nas_file_system.
                                             example2: oss://path/to/mount/:/home/admin/dir/,
                                             and file is also supported: oss://path/to/mount/a.txt:/home/admin/dir/a.txt.""",
                'docker': """optional,optional, use docker, format: <docker_image_name>@<docker_storage_oss_path>,
                                             example: localhost:5000/myubuntu@oss://bucket/dockers/
                                             or for short: myubuntu@oss://bucket/dockers/ """,
                'file': """optional,submit job from a config file, if you give options explicitly, options from this file will be override""",
                'user_data': "optional, user data k-v pairs, exp: a:b,c:e",
                'disk': """optional, mount system disk and a data disk(optional), only works with AutoCluster.
                                             Usage: "--disk system:default:40,data:cloud:50:/home/disk1".
                                             Default: system:default:40, mount 40GB default disk as system disk.
                                             System disk config format: system:<default|cloud|ephemeral...>:<40-500>,
                                             example: system:cloud:40, mount 40GB ephemeral disk as system disk.
                                             Data disk config format: data:<default|cloud|ephemeral...>:<5-2000>:<mount-point>,
                                             example: data:cloud:5:/home/disk1, mount a 5GB cloud disk as data disk,
                                             in windows must mount to driver, such as E driver, like: "data:cloud:5:E".
                                             (Attention please: Using ephemeral disk as data disk, the size scope should limit to [5-1024]GB).
                                             (type '%s d' for more available diskTypes).
        """ % CMD,
                'lock': """Using file lock for OSS Mount. default: false""",
                'locale': """Locale for OSS Mount. options: GBK,GB2312-80,BIG5,UTF-8,ANSI,EUC-JP,EUC-TW,EUC-KR,SHIFT-JIS,KSC5601...""",
                'notification_events': "Events for notification, type '%s e' for more." % CMD,
                'notification_topic': "Topic name in MNS.",
                'notification_endpoint': "MNS Endpoint, see in MNS web console.",
                'nas_access_group': 'NAS access groups, multiple items should be separated by comma',
                'nas_file_system': 'NAS file system, multiple items should be separated by comma',
                'resource_type': 'optional, default "OnDemand", scope: [OnDemand|Spot]',
                'spot_price_limit': 'optional, it\'s available when resource_type is Spot(unit: yuan,works to three decimal places). Set to 0 means using the system automatically bid(But lower than the "OnDemand" price)',
                'reserve_on_fail': 'optional, won\'t release auto-cluster when job failed',
                'no_cache_support': 'optional, cancel the cache for ossmounter',
                'vpc_cidr_block': 'CIDR, such as: 192.168.0.0/16',
                'vpc_id': 'set VPC id',
                'show_json': 'optional,just output job.json, won\'t submit a job, default: false',
                'show_dag': 'optional,just output dag graph, won\'t submit a job, default: false'
            }
        },
        'check': {
            'description': "check job status and failed reasons"
        },
        'project': {
            'description': 'project commanders: create, build, submit, etc.',
            'create': {
                'description': 'create a job project',
                'option': {
                    'type': """optional, job project type, default: empty(python), scope: [empty|python|java|shell|wdl]""",
                    'job': 'optional, create job project from an exists job_id'
                }
            },
            'build': {
                'description': 'build project, package src/ to worker.tar.gz.'

            },
            'update': {
                'description': 'update job.json',
                'option': {
                    'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                              default value is an auto_cluster string: img=%s:type=%s.
                              you can use a exists cluster(type '%s c' for more cluster id),
                              or use auto cluster, format: img=<imageId>:type=<instanceType>
                              (type '%s i' for more images)
                              (type '%s t' for more instanceType). """
                    % (IMG_ID, INS_TYPE, CMD, CMD, CMD),
                    "docker": """optional, use docker image to run, format:<oss_docker_storage_path>:<docker_name>"""
                }
            },
            'submit':{
                'description': 'upload worker.tar.gz and create a job'
            },
            'status': {
                'description': 'show project status.'
            },
            'add_task': {
                'description': 'add a task',
                'detail': "add a task node into job.json, and create a promgram(python) file in src folder.",
                'option': {
                    'cluster': """optional, should be a cluster_id, or an auto_cluster string.
                                 default value is an auto_cluster string: img=%s:type=%s.
                                 you can use a exists cluster(type '%s c' for more cluster id),
                                 or use auto cluster, format: img=<imageId>:type=<instanceType>
                                 (type '%s i' for more images)
                                 (type '%s t' for more instanceType).  """
                    % (IMG_ID, INS_TYPE, CMD, CMD, CMD),

                    'docker': 'docker image name, must tag with prefix:"localhost:5000/", type "docker images" for more'
                }
            }
        },
        'oss': {
            'description': 'oss commanders: upload, download, ls, etc.',
            'login': {
                'description': 'login OSS',
            },
            'logout': {
                'description': 'logout OSS',
            },
            'pwd': {
                'description': 'show current osspath',
            },
            'ls': {
                'description': 'show folders and files in an osspath',
                'option': {
                    'name': 'search by name',
                    'top': 'length of result-set to show',
                }
            },
            'cat': {
                'description': 'print oss file content',
                'option': {
                    'byte_range': 'format: 100:1024, if just one number is given, such as: -b 100, it means: -b 0:100'
                }
            },
            'copy': {
                'description': 'copy oss file or folder',
                'detail': 'copy oss file or folder. across region support format: <region>#<osspath>, only if the AK is validated'
            },
            'upload': {
                'description': 'upload file or directory to oss',
                'option': {
                    'use_put_object': 'Forced use of the PutObject method to upload (By default, file sizes bigger than 4GB will be uploaded using multi upload)'
                }
            },
            'download': {
                'description': 'download file or directory from oss',
                'option': {
                    'recursion': "download directory and the entire subtree from oss"
                }
            },
            'delete': {
                'description': 'delete file or directory from oos',
                'option': {
                    'yes': 'delete in silent mode'
                 }
            }
        },
        'qsub': {
            'description': 'qsub supported. Now migrate you qsub command to BatchCompute is much easier than you think',
            'detail': 'qsub supported. Now migrate you qsub command to BatchCompute is much easier than you think',
            'option': {
                'd': '''Defines the working directory path to be used for the job. If the -d option is not specified,
                                         the default working directory is the home directory. This option sets the environment variable PBS_O_INITDIR.
                                         ''',
                'e': '''Defines the path to be used for the standard error stream of the batch job.
                                         For example: -e /home/logs/stderr.log
                                         ''',
                'j': '''Declares if the standard error stream of the job will be merged with the standard output stream of the job.
                                         An option argument value of oe directs that the two streams will be merged, intermixed,
                                         as standard output. An option argument value of eo directs that the two streams will be merged,
                                         intermixed, as standard error.

                                         If the join argument is n or the option is not specified, the two streams will be two separate files.
                      ''',
                'l': '''Defines the resources that are required by the job and establishes a limit to the amount of resource that can be consumed.
                                         If not set for a generally available resource, such as CPU time, it will be set to default one in bcs.
                                         The resource_list argument is of the form:
                                         resource_name[=[value]][,resource_name[=[value]],...]
                                         ''',
                'N': 'Declares a name for the job. ',
                'o': '''Defines the path to be used for the standard output stream of the batch job.'
                                         For example: -e /home/logs/stdout.log
                                         ''',
                'q': '''Batch compute queues with automatic scheduling, no need to specify a queue,
                                         but you can specify a cluster, such as:"-q @cls-xxxx",
                                         if you specify a queue, like:"-q 118@cls-xxx", the string before @ will be ignore.''',
                'V': '''Declares that all environment variables in the qsub command's environment are to be exported to the batch job.''',
                'show_json': 'optional,just output a BatchCompute job descrition json, won\'t submit a job',
                'show_opt': 'optional,just output an options json, won\'t submit a job',
            }
        },
        'qstat': {
            'description': 'show status of pbs batch jobs',
            'option': {
                'f': '''Specifies that a full status display be written to standard out.''',
                'a': '''"All" jobs are displayed in the alternative format, see the Standard Output section.
                                    If the operand is a destination id, all jobs at that destination are displayed.
                                    If the operand is a job id, information about that job is displayed.''',
                'i': '''Job status is displayed in the alternative format. For a destination id operand,
                                    status for jobs at that destination which are not running are displayed.
                                    This includes jobs which are queued, held or waiting.
                                    If an operand is a job id, status for that job is displayed regardless of its state.''',
                'r': '''If an operand is a job id, status for that job is displayed. For a destination id operand,
                                    status for jobs at that destination which are running are displayed,
                                    this includes jobs which are suspended.''',
                'u': '''list jobs for in user_list'''
            }
        },
        'qdel': {
            'description': 'Delete job',
            'option': {
                'W': '''Unsupported'''
            }
        },
        'qhost': {
            'description': 'Unsupported',
            'option': {

            }
        },
        'template_gen': {
            'description': 'Init a native job project using template',
            'option': {
                'type': 'required, generate with specify template, scope: [gatk|wdl]'
            }
        }
    }
