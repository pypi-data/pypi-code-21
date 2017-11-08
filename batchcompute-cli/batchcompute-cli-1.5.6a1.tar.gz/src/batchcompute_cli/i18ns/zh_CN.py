# -*- coding: utf-8 -*-
from ..util import smart_unicode
from ..const import STRING
from ..const import CMD
from terminal import magenta

IMG_ID = 'img-ubuntu'
INS_TYPE = 'ecs.s3.large'

def getJSON():
    o = __get_json()

    for (k,v) in o.items():
        if isinstance(v, STRING):
            o[k]=smart_unicode.format_utf8(v)
        if isinstance(v, dict):
            for k2,v2 in v.items():
                if isinstance(v2, STRING):
                    v[k2]=smart_unicode.format_utf8(v2)
                if isinstance(v2, dict):
                    for k3,v3 in v2.items():
                        if isinstance(v3,STRING):
                            v2[k3]=smart_unicode.format_utf8(v3)
    return o

def __get_json():
    return {
        "changed": '有改动',
        "login": {
            "description": "使用阿里云AccessKey登录"
        },
        "logout": {
            "description": "退出登录,将删除本地保存的AK配置等"
        },
        "config": {
            "description": "配置管理",
            "detail": "修改配置, 不带参数则查看配置",
            "option": {
                "region": '设置区域, 如:cn-qingdao',
                "osspath": '设置默认OSS路径',
                "locale": '设置语言地域, 可选范围:[zh_CN|en]',
                "image": "设置默认镜像Id, 运行 '%s i' 可以列出可用的Image" % CMD,
                "type": "设置默认InstanceType, 运行 '%s t' 可以看到本区域支持的instanceType" % (CMD),
                "cluster": "设置默认集群, 运行 '%s c' 可以看到已经创建的集群" % (CMD),
                'version': "设置版本, 支持预发环境使用,版本如: 2015-10-01",
                'god': "使用上帝模式, 可选范围:[true|false]",
                'ssl': '使用https访问BatchCompute, 可选范围:[true|false]',
                'qsubuser': '设置qsub用户名, 如果不设置,默认:root',
                'vpc_cidr_block': '设置默认使用VPC的CIDR IP段, 一般设置为: 192.168.0.0/16, 如果不设置或者设置为false, 则使用经典网络',
            }
        },
        'info': {
            "description": "显示关于batchcompute-cli的信息",
            "latest_version": "最新版本",
            "current_version": "当前版本",
            "has_upgrade": "你可以执行 'pip install -U batchcompute-cli' 来升级",
            "has_upgrade2": "如果提示没有权限, 请使用 'sudo pip install -U batchcompute-cli'"
        },
        "image": {
            "description": '显示可用镜像列表, 查看镜像详情.',
            'option': {
                'description': '获取集群描述JSON',
                'show_json': '显示json信息'
            }
        },
        "app": {
            "description": '显示App列表, 查看App详情',
            "option": {
                "public": '获取Scope为Public的App, 只在获取App详情时有效',
                "description": "只显示json"
            }
        },
        "disk_type": {
            "description": '显示可用磁盘类型列表.',
            'option': {
                'show_json': '显示json信息'
            }
        },
        "instance_type": {
            "description": '显示实例类型列表.',
            'option': {
                'show_json': '显示json信息'
            }
        },
        "resource_type": {
            "description": '显示资源类型列表.',
            'option': {
                'show_json': '显示json信息'
            }
        },
        "event": {
            "description": '显示支持的事件.',
            'option': {
                'show_json': '显示json信息'
            }
        },
        "cluster": {
            "description": '获取集群列表, 获取集群详情.',
            "option": {
                'description': '获取集群描述JSON',
                'oplog': '显示操作日志, 获取集群详情有效',
                'show_json': '显示json信息'
            }
        },
        "job": {
            "description": '获取作业列表, 获取作业,任务详情等.',
            "option": {
                'top': '显示结果集行数, 只在获取作业列表时生效',
                'all': '显示所有结果',
                'state': '获取作业列表时, 按状态过滤, 取值范围: [Running|Stopped|Waiting|Finished|Failed]',
                "id": '获取作业列表时, 按 JobId 模糊查询',
                'name': '获取作业列表时, 按 JobName 模糊查询',
                'description': '获取作业描述JSON',
                'show_json': '显示json信息'
            }
        },
        'log': {
            'description': '显示作业日志, 或者从oss下载日志保存到本地',
            'option': {
                'dir_path': '指定本地目录用以保存oss日志, 如果没有指定,则显示日志到屏幕',
                'stderr': '只显示stderr日志',
                'stdout': '只显示stdout日志',
                'log_mapping': '只显示log_mapping日志'
            }
        },
        'create_image': {
            'description': '注册镜像',
            'option': {
                'platform': "可选, 平台范围[Linux|Windows] 默认: Linux",
                'description': "可选, 描述信息, string",
                'show_json': '只显示 image json不创建'
            }
        },
        'delete_image': {
            'description': '注销镜像, 支持批量删除',
            'option': {
                'yes': "可选, 不要询问直接注销"
            }
        },
        'create_cluster': {
            'description': '创建集群',
            'option': {
                'image': "可选, imageId, 更多信息输入 %s i 查看" % CMD,
                'type': "可选, instanceType, 更多信息输入 %s t 查看" % (CMD),
                'nodes': "可选, int类型, default: 1",
                'description': "可选, 描述信息, string",
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'resource_type': '可选, 默认 "OnDemand(按需)", 可选范围:[OnDemand|Spot]',
                'spot_price_limit': '可选, resource_type为Spot时有效(单位为元,可以为小数). 设置为0表示使用系统自动出价(但不会超过按量付费价格)',
                'user_data': "可选, 用户数据, k:v 对,多个逗号隔开, 格式: k:v,k2:v2",
                'disk': """可选, 挂载磁盘, 支持系统盘配置和一块数据盘(可选)的配置,
                                             使用方法如: "--disk system:default:40,data:cloud:50:/home/disk1".
                                             默认只挂载一个系统盘:类型为 default,大小40GB.
                                             系统盘配置格式: system:<default|cloud|ephemeral...>:<40-500>,
                                             举例: system:cloud:40, 表示系统盘挂载40GB的云盘.
                                             数据盘配置格式: data:<default|cloud|ephemeral...>:<5-2000>:<mount-point>,
                                             举例: data:cloud:5:/home/disk1, 表示挂载一个5GB的云盘作为数据盘, window下只能挂载到驱动,如E盘:"data:cloud:5:E".
                                             (注意: 数据盘使用ephemeral的时候,size取值范围限制为:[5-1024]GB).
                                             (运行 '%s d' 可以看到本区域支持的diskType).
                 """ % CMD,

                'notification_events': "消息通知的事件,可以用'%s e'查看。" % CMD,
                'notification_topic': "消息通知的Topic名称,可以在mns创建。",
                'notification_endpoint': "消息通知的Endpoint, 可以在mns控制台查看。",
                'mount': """可选,读写模式挂载NAS配置或者只读方式挂载OSS, 格式: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                             如: nas://path/to/mount/:/home/admin/nasdir/ 表示将NAS路径挂载到本地目录。
                                             使用NAS挂载还需配置nas_access_group和nas_file_system。
                                             如: oss://path/to/mount/:/home/admin/nasdir/ 表示将OSS路径挂载到本地目录,
                                             也支持直接挂载文件, 如:oss://path/to/mount/a.txt:/home/admin/nasdir/a.txt。""",
                'nas_access_group': 'NAS 权限组',
                'nas_file_system': 'NAS 文件系统',
                'no_cache_support': '可选, 取消OSSMounter缓存',
                'vpc_cidr_block': 'IP网段,如: 192.168.0.0/16',
                'vpc_id': '设置 VPC id',
                'show_json': '只显示cluster json不创建',
                'filePath': '通过集群描述json文件提交,其他options将失效'
            }
        },
        'delete_cluster': {
            'description': '删除集群, 支持批量删除',
            'option': {
                'yes': "可选, 不要询问直接删除"
            }
        },
        'update_cluster': {
            'description': '修改集群信息, 目前只支持修改期望机器数',
            'option': {
                'yes': "可选, 不要询问直接修改",
                'nodes': "必选, 期望修改的机器数, 必须为正整数",
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'spot_price_limit': '可选, resource_type为Spot时有效(单位为元,可以为小数). 设置为0表示使用系统自动出价(但不会超过按量付费价格)',
                'user_data': "可选, 用户数据, k:v 对,多个逗号隔开, 格式: k:v,k2:v2",
                'mount': """可选,读写模式挂载NAS配置, 格式: <nas_path>:<dir_path>[,<nas_path2>:<dir_path2>...],
        如: nas://path/to/mount:/home/admin/nasdir 表示将NAS路径挂载到本地目录。
        使用NAS挂载还需配置nas_access_group和nas_file_system""",
                'image': "可选, imageId, 更多信息输入 %s i 查看" % CMD,
                'show_json': '只显示cluster json不创建'
            }

        },
        "create_app": {
           'description': '创建 App',
            'option': {
                'file': '可选, 根据app描述json文件创建app, 其他option可以覆盖json中的配置。',
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'docker': """可选, docker选项和image选项必选一个, 使用docker镜像运行,
                                          格式: <image_name>@<storage_oss_path>,
                                          如: localhost:5000/myubuntu@oss://bucket/dockers/
                                          或者: myubuntu@oss://bucket/dockers/""",
                'image': "可选, docker选项和image选项必选一个, 使用VM容器,指定imageId",

                'type': "可选, instanceType, 更多信息输入 %s t 查看, 格式: {defaultValue}:{overwritable}:{desc}" % (CMD),
                'resource_type': '可选, 类型默认 "OnDemand(按需)", 可选范围:[OnDemand|Spot], 格式: {defaultValue}:{overwritable}:{desc}',
                'nodes': "可选, 实例个数, 格式: {defaultValue}:{overwritable}:{desc}",
                'disk_type': '''可选, 系统盘类型(运行 '%s d' 可以看到本区域支持的diskType), 格式: {defaultValue}:{overwritable}:{desc}''' % CMD,
                'min_disk_size': '可选, 系统盘最小限制, 单位: GB, 格式: {defaultValue}:{overwritable}:{desc}',
                'max_retry_count': '可选, 某个Instance失败后，最大重试次数, 格式: {defaultValue}:{overwritable}:{desc}',
                'timeout': "可选,超时时间(如果实例运行时间超时则失败), 默认: 86400(单位秒,表示1天), 格式: {defaultValue}:{overwritable}:{desc}",

                'inputs': '''可选, 输入参数配置,格式: item1,item2.., 每个item格式: {name}[:{type}][:{localpath}][:{desc}][:{defaultValue}]''',
                'outputs': '''可选, 输出参数配置,格式: item1,item2.., 每个item格式: {name}[:{type}][:{localpath}][:{desc}]''',
                
                'daemonize': '应用在执行时，是否每次都要重新启动。默认值：False',
                'description': '可选, App的描述信息',

                'show_json': '只显示cluster json不创建',
            }
        },
        "update_app": {
            'description': '修改一个App资源。每次修改会增加一个新的版本，已有的版本保持不变。',
            'option': {
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'docker': """可选, 使用docker镜像运行, 格式: <image_name>@<storage_oss_path>,
                                       如: localhost:5000/myubuntu@oss://bucket/dockers/
                                       或者: myubuntu@oss://bucket/dockers/""",
                'image': "可选, AutoCluster使用的imageId, 优先级高于cluster中的AutoCluster字符串配置, 设置cluster为clusterId时该项无效",

                'daemonize': '应用在执行时，是否每次都要重新启动。默认值：False',
                'description': '可选, App的描述',
                'yes': "可选, 不要询问直接修改",
                'show_json': '只显示cluster json不创建',
            }
        },
        'delete_app': {
           'description': '删除 App',
            'option': {
                'yes': '可选,直接删除 App 无需询问'
            }
        },
        "asub": {
            'description': '快速提交一个 App 作业',
            'option': {
                'type': "可选, instanceType, 更多信息输入 %s t 查看" % (CMD),
                'resource_type': '可选, 类型默认 "OnDemand(按需)", 可选范围:[OnDemand|Spot]',
                'nodes': "可选, 实例个数",
                'disk_type': '''可选, 系统盘类型(运行 '%s d' 可以看到本区域支持的diskType)''' % CMD,
                'min_disk_size': '可选, 系统盘最小限制, 单位: GB',
                'max_retry_count': '可选, 某个Instance失败后，最大重试次数',
                'timeout': "可选, 超时时间(如果实例运行时间超时则失败), 默认: 86400(单位秒,表示1天)",
                'description': '可选, 作业描述',
                'config': '可选, 配置项,格式:k=v[,k2=v2][,k3=v3]...',
                'show_json': '''只显示 json 不创建作业\n''',

                'param_desc': '''**********************************************
    以下是此 App 特有的参数
    以 --input_ 开头的表示 App 的输入参数, 输入参数默认都可以改成 --input_from_file_ 开头, 表示同时上传到OSS。
    **********************************************
                ''',
                'inputs': '''如果后缀为//:oss, 表示自动生成oss路径,
                                             如果是文件则自动上传到oss相应的路径下, 如: --iWDL hello.wdl//:oss''',
                'outputs': '''如果后缀为//:oss, 表示自动生成oss路径,  如: --iWDL ./demo///:oss'''
            }
        },
        'create_job': {
            'description': '通过 JSON 创建作业',
            'option': {
                'filePath': '本地 JSON 路径'
            }
        },
        'restart_job': {
            'description': '重新启动作业, 支持批量操作',
            'option': {
                'yes': "可选,直接重启作业无需询问"
            }
        },
        'stop_job': {
            'description': '停止作业, 支持批量操作',
            'option': {
                'yes': "可选,直接停止作业无需询问"
            }
        },
        'delete_job': {
            'description': '删除作业, 支持批量操作',
            'option': {
                'yes': "可选,直接删除作业无需询问"
            }
        },
        'update_job': {
            'description': '修改作业, 目前只支持修改优先级',
            'option': {
                'yes': "可选,直接修改无需询问",
                'priority': "必选, 取值范围: 1-1000"
            }
        },
        'submit': {
            'description': '快速提交单个任务的作业',
            'option': {
                'cluster': """可选,可以使一个集群ID或者AutoCluster配置字符串.
                                             默认是一个AutoCluster配置字符串: img=%s:type=%s.
                                             你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                                             或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                                             (运行 '%s i' 可以列出可用的Image, 其他的可用查看官网文档)
                                             (运行 '%s t' 可以看到本区域支持的instanceType). """ % (
                IMG_ID, INS_TYPE, CMD, CMD, CMD),
                'pack': "可选,打包指定目录下的文件,并上传到OSS, 如果没有指定这个选项则不打包不上传",
                'priority': '可选,int类型,指定作业优先级,默认:0\n',
                'timeout': "可选,超时时间(如果实例运行时间超时则失败), 默认: 86400(单位秒,表示1天)",
                'image': "可选, AutoCluster使用的imageId, 优先级高于cluster中的AutoCluster字符串配置, 设置cluster为clusterId时该项无效",
                'type': "可选, AutoCluster使用的instanceType, 优先级高于cluster中的AutoCluster字符串配置, 设置cluster为clusterId时该项无效",
                'nodes': "可选,需要运行程序的机器数, 默认: 1",
                'description': '可选,设置作业描述',
                'force': "可选,当instance失败时job不失败, 默认:当instance失败时job也失败",
                'auto_release': "可选,当job运行成功(state=='Finished')后自动被释放(删除)掉",
                'env': "可选,设置环境变量, 格式: <k>:<v>[,<k2>:<v2>...]",
                'read_mount': """可选,只读模式挂载配置, 格式: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                             挂载目录例子: oss://bucket/key/:/home/admin/ossdir/ 表示将oss的路径挂载为本地目录,
                                             挂载文件例子: oss://bucket/key1:/home/admin/key1 表示将oss的文件挂载为本地文件""",
                'write_mount': """可选,可写模式挂载配置(任务结束后写到本地目录的文件会被上传到相应的oss_path下),
                                             格式: <oss_path>:<dir_path>[,<oss_path2>:<dir_path2>...],
                                             如: oss://bucket/key:/home/admin/ossdir 表示将oss的路径挂载到本地目录""",
                'mount': """可选,读写模式挂载NAS配置或者只读方式挂载OSS, 格式: <nas_path|oss_path>:<dir_path>[,<nas_path2|oss_path2>:<dir_path2>...],
                                             如: nas://path/to/mount/:/home/admin/nasdir/ 表示将NAS路径挂载到本地目录。
                                             使用NAS挂载还需配置nas_access_group和nas_file_system。
                                             如: oss://path/to/mount/:/home/admin/nasdir/ 表示将OSS路径挂载到本地目录,
                                             也支持直接挂载文件, 如:oss://path/to/mount/a.txt:/home/admin/nasdir/a.txt。""",
                'docker': """可选, 使用docker镜像运行, 格式: <image_name>@<storage_oss_path>,
                                             如: localhost:5000/myubuntu@oss://bucket/dockers/
                                             或者: myubuntu@oss://bucket/dockers/""",
                'file': """可选,使用配置文件提交作业,如果你显示指定其他选项,配置文件中的选项会被覆盖""",
                'user_data': "可选, 用户数据, k:v 对,多个逗号隔开, 格式: k:v,k2:v2",
                'disk': """可选,挂载磁盘, 只在使用AutoCluster时有效, 支持系统盘配置和一块数据盘(可选)的配置,

                                             使用方法如: "--disk system:default:40,data:cloud:50:/home/disk1".
                                             默认只挂载一个系统盘:类型为default,由服务端自动指定, 大小40GB.
                                             系统盘配置格式: system:<default|cloud|ephemeral...>:<40-500>,
                                             举例: system:cloud:40, 表示系统盘挂载40GB的云盘.
                                             数据盘配置格式: data:<default|cloud|ephemeral...>:<5-2000>:<mount-point>,
                                             举例: data:cloud:5:/home/disk1, 表示挂载一个5GB的云盘作为数据盘, window下只能挂载到驱动,如E盘:"data:cloud:5:E".
                                             (注意: 数据盘使用ephemeral的时候,size取值范围限制为:[5-1024]GB).
                                             (运行 '%s d' 可以看到本区域支持的diskType).
                        """ % CMD,
                'lock': """OSS挂载是否支持网络文件锁。""",
                'locale': """OSS Object挂载到本地时使用的字符集。可选范围包括GBK、GB2312-80、BIG5、UTF-8、ANSI、EUC-JP、EUC-TW、EUC-KR、SHIFT-JIS、KSC5601等。""",
                'notification_events': "消息通知的事件,可以用'%s e'查看。" % CMD,
                'notification_topic': "消息通知的Topic名称,可以在mns创建。",
                'notification_endpoint': "消息通知的Endpoint, 可以在mns控制台查看。",
                'nas_access_group': 'NAS 权限组',
                'nas_file_system': 'NAS 文件系统,多个逗号隔开',
                'resource_type': '可选, 默认 "OnDemand(按需)", 可选范围:[OnDemand|Spot]',
                'spot_price_limit': '可选, resource_type为Spot时有效(单位为元,可以为小数). 设置为0表示使用系统自动出价(但不会超过按量付费价格)',
                'reserve_on_fail': '可选, 作业失败不会释放autoCluster, 便于调查问题',
                'no_cache_support': '可选, 取消OSSMounter缓存',
                'vpc_cidr_block': 'IP网段,如: 192.168.0.0/16',
                'vpc_id': '设置 VPC id',
                'show_json': '只显示json不提交作业',
                'show_dag': '只显示DAG图不提交作业'
            }
        },
        'check': {
            'description': "检查job状态以及失败原因"
        },
        'project': {
            'description': '作业工程命令,包括: create, build, submit 等',
            'create': {
                'description': '创建作业工程',
                'option': {
                    'type': """可选, 创建作业工程类型, 默认: empty(python), 取值范围:[empty|python|java|shell|wdl]""",
                    'job': '可选, 从一个已有 job_id 创建一个作业工程'
                }
            },
            'build': {
                'description': '编译, 打包 src/ 为 worker.tar.gz.'

            },
            'update': {
                'description': '修改job.json, 可以指定task名称修改, 不指定则修改全部task',
                'option': {
                    'cluster': """可以使一个集群ID或者AutoCluster配置字符串.
                              默认是一个AutoCluster配置字符串: img=%s:type=%s.
                              你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                              或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                              (运行 '%s i' 可以列出可用的Image, 其他的可用查看官网文档)
                              (运行 '%s t' 可以看到本区域支持的instanceType). """
                               % (IMG_ID, INS_TYPE, CMD, CMD, CMD),
                    "docker": """可选,使用docker镜像运行, 格式如:<oss_docker_storage_path>:<docker_name>"""
                }
            },
            'submit':{
                'description': '上传worker.tar.gz, 并提交作业'
            },
            'status': {
                'description': '显示工程状态.'
            },
            'add_task': {
                'description': '增加一个任务',
                'detail': "在job.json中增加一个任务节点, 并且在src目录创建一个程序文件(目前只支持python)",
                'option': {
                    'cluster': """可以使一个集群ID或者AutoCluster配置字符串.
                                  默认是一个AutoCluster配置字符串: img=%s:type=%s.
                                  你可以使用一个已经存在的集群ID(type '%s c' for more cluster id),
                                  或者可以使用AutoCluster配置字符串, 格式: img=<imageId>:type=<instanceType>
                                  (运行 '%s i' 可以列出可用的Image, 其他的可用查看官网文档)
                                  (运行 '%s t' 可以看到本区域支持的instanceType). """
                               % (IMG_ID, INS_TYPE, CMD, CMD, CMD),

                    'docker': 'Docker镜像名, 需要以前缀"localhost:5000/"打tag'
                }
            }
        },
        'oss': {
            'description': 'OSS相关命令: upload, download, mkdir, ls 等.',
            'login': {
                'description': '登录OSS',
            },
            'logout': {
                'description': '登出OSS',
            },
            'pwd': {
                'description': '显示当前osspath',
            },
            'ls': {
                'description': '列出一个osspath下面的目录和文件',
                'option': {
                    'name': '模糊搜索',
                    'top': '显示结果集行数',
                }
            },
            'cat': {
                'description': '打印文件内容',
                'option': {
                    'byte_range': '请求获取的范围,格式: 100:1024, 如果为一个数字,如: -b 100,表示-b 0:100'
                }
            },
            'copy': {
                'description': '复制OSS文件或目录',
                'detail': '复制OSS文件或目录, 可以跨域复制, 使用osspath格式: <region>#<osspath>'
            },
            'upload': {
                'description': '上传文件或目录到OSS',
                'option': {
                    'use_put_object': '强制使用 PutObject 方法上传 (默认情况下超过4GB将使用multi upload方式上传)'
                }
            },
            'download': {
                'description': '下载文件或目录',
                'option': {
                    'recursion': '下载整个目录'
                }
            },
            'delete': {
                'description': '删除OSS上的目录或文件',
                'option': {
                    'yes': '可选,直接删除无需询问'
                 }
            }
        },
        'qsub': {
            #https://linux.die.net/man/1/qsub-torque
            'description': '对qsub的兼容支持,可快速将qsub迁移至批量计算',
            'detail': '''对qsub的兼容支持,可快速将qsub迁移至批量计算,部分不支持的option自动忽略。
                      其他字段可以在用户目录下配置 ~/.qsub-task-description.json''',
            'option': {
                'd': '指定工作路径, 并添加到环境变量中, key 为 PBS_O_INITDIR.',
                'e': '定义标准错误日志的路径. 如果不设置, 默认使用批量计算生成的路径.',
                'j': '合并stderr日志到stdout, 可选:[oe|eo|n], 默认为:n,不合并',
                'l': '''声明计算需要的资源, 不设置则使用默认的。
                                         格式: resource_name[=[value]][,resource_name[=[value]],...]''',
                'N': '声明作业名称',
                'o': '定义标准输出日志的路径. 如果不设置, 默认使用批量计算生成的路径.',
                'q': '''批量计算集群有自动调度的队列,无需也无法指定queue, 可以指定集群, 如:"-q @cls-xxxx",
                                         如果指定了queue, 如:"-q 118@cls-xxx", @前面的字符串会被忽略。''',
                'V': '''将当前qsub命令运行环境中的环境变量全部设置到job运行环境中。''',
                'show_json': '只显示json不提交作业',
                'show_opt': '只显示opt json不提交作业',
            }
        },
        'qstat': {
            'description': '用于查询作业状态信息',
            'option': {
                'f': '''列出指定作业的信息''',
                'a': '''列出系统所有作业''',
                'i': '''列出不在运行的作业''',
                'r': '''列出所有正在运行的作业''',
                'u': '列出指定用户的作业'
            }
        },
        'qdel': {
            'description': '删除作业',
            'option': {
                'W': '''不支持'''
            }
        },
        'qhost': {
            'description': '暂不支持',
            'option': {

            }
        },
        'template_gen': {
            'description': '使用特定模板生成代码工程',
            'option': {
                'type': '必选, 指定模板类型来生成, 可选值: [gatk|wdl]'
            }
        }
    }
