import json
import os
import platform

import requests
from django.conf import settings

from SweetPy.extend.zookeeper_plus import ZookeeperPlus, ZookeeperPlusWatch

# 设置项
# SWEET_CLOUD_ENABLED = True
# SWEET_CLOUD_JOINT_RUL = 'http://10.86.87.180:19999/'
# SWEET_CLOUD_APPNAME = 'python-sweet'
# SWEET_CLOUD_VERSION = '1.0'
# SWEET_CLOUD_TICKET = 'c0882ecd-5c6f-4a03-b8e9-c45b556e14dc'
# SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST = '10.200.144.127'
# SWEET_CLOUD_APPPORT = '8000'

sweet_settings = None
sweet_py_version = '1.0'

settings.MIDDLEWARE.insert(0,'SweetPy.django_middleware.tracker.request_tracker')

def get_local_ip():
    import socket
    localIP = socket.gethostbyname(socket.gethostname())
    # localIP = socket.gethostname()
    return localIP

def get_http_port():
    result = 80
    global sweet_settings
    if not sweet_settings:
        return result
    if not sweet_settings.get('applicationInstanceConfigurations',None):
        return result
    else:
        return sweet_settings['applicationInstanceConfigurations'].get('sweet.framework.socket.server.tcp.port',result)

def get_sweet_settings_local_filename():
    app_name = settings.SWEET_CLOUD_APPNAME
    app_port = settings.SWEET_CLOUD_APPPORT
    app_host = get_local_ip()#settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
    sysstr = platform.system()
    if sysstr.lower() == 'windows':
        filename = os.environ["TMP"] + '\\' + app_name + app_host + str(app_port) + '.json'
    else:
        filename = '/tmp/' + app_name + app_host + str(app_port) + '.json'
    return filename

def get_sweet_settings():
    global sweet_settings
    if sweet_settings:
        return sweet_settings
    filename = get_sweet_settings_local_filename()
    if not os.path.exists(filename):
        return {}
    with open(filename,'r') as f:
        sweet_settings = json.loads(f.read())
        return sweet_settings

def write_sweet_settings(setting):
    filename = get_sweet_settings_local_filename()
    with open(filename, 'w') as f:
        f.write(json.dumps(setting,ensure_ascii=False))

def get_sweet_params_from_evun_colud():
    global sweet_settings
    if sweet_settings:
        return
    if (hasattr(settings,'SWEET_CLOUD_ENABLED')) and settings.SWEET_CLOUD_ENABLED:
        url = settings.SWEET_CLOUD_JOINT_RUL + '?' + \
              'application=' + settings.SWEET_CLOUD_APPNAME + \
              '&index=' + settings.SWEET_CLOUD_APPPORT + \
              '&version=' + settings.SWEET_CLOUD_VERSION + \
              '&ticket=' + settings.SWEET_CLOUD_TICKET

        try:
            result = requests.get(url)
            result_dict = json.loads(result.text)
            if result_dict['code'] == 'success':
                print('evun cloud connected!')
                sweet_settings = result_dict['data']
                write_sweet_settings(sweet_settings)
            else:
                print('evun cloud error:' + result_dict['message'])
                quit(0)
        except Exception as e:
            print("can't connect to the evun cloud!")
            quit(0)
    else:
        pass

def set_django_connection(sweet_settings):
    if sweet_settings['applicationInstanceConfigurations'].get('spring.datasource.db-type', None) == None:
        return
    default = None
    try:
        _driver_name = sweet_settings['applicationInstanceConfigurations']['spring.datasource.db-type'].lower()
        _url = sweet_settings['applicationInstanceConfigurations']['spring.datasource.url']
        if _url.find(':') != -1:
            _ip = _url[:_url.find(':')]
            _port = _url[_url.find(':') + 1:]
        if _driver_name == 'postgres':
            default = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': sweet_settings['applicationInstanceConfigurations']['spring.datasource.name'],
                'USER': sweet_settings['applicationInstanceConfigurations']['spring.datasource.username'],
                'PASSWORD': sweet_settings['applicationInstanceConfigurations']['spring.datasource.password'],
                'HOST': _ip,
                'PORT': _port,
                'CONN_MAX_AGE': int(sweet_settings['applicationInstanceConfigurations']['spring.datasource.maxActive'])
            }
        elif _driver_name == 'mysql':
            default = {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': sweet_settings['applicationInstanceConfigurations']['spring.datasource.name'],
                'USER': sweet_settings['applicationInstanceConfigurations']['spring.datasource.username'],
                'PASSWORD': sweet_settings['applicationInstanceConfigurations']['spring.datasource.password'],
                'HOST': _ip,
                'PORT': _port,
                'CONN_MAX_AGE': int(sweet_settings['applicationInstanceConfigurations']['spring.datasource.maxActive'])
            }
        elif _driver_name == 'sqlite':
            default = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': _url,
            }
        if default:
            settings.DATABASES['default'] = default
    except Exception as e:
        print("数据配置错误,请配置以下字段:["
              "'spring.datasource.db-type':'数据库类型postgres,mysql,sqlite等',"
              "'spring.datasource.username':'用户名',"
              "'spring.datasource.password':'密码',"
              "'spring.datasource.url':'IP地址和端口号以:号分隔',"
              "'spring.datasource.maxActive':'连接池大小',"
              "'spring.datasource.name':'要连接的仓库名',"
              "'spring.datasource.minIdle':'连接池回收时间(暂时未启用)']")
        quit(0)

zk_plus = None

def add_data_watch(node_path,func):
    result = False
    global zk_plus
    if zk_plus == None:
        return result
    zpw = ZookeeperPlusWatch(zk_plus)
    if zpw.add_data_watch(node_path,func):
        ZookeeperPlusWatch.watch_list.append(zpw)
        result = True
    return result

def add_node_watch(node_path,func):
    result = False
    global zk_plus
    if zk_plus == None:
        return result
    zpw = ZookeeperPlusWatch(zk_plus)
    if zpw.add_node_watch(node_path, func):
        ZookeeperPlusWatch.watch_list.append(zpw)
        result = True
    return result



def zookeeper_on_line(sweet_settings):
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]

    global zk_plus
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)

    app_name = settings.SWEET_CLOUD_APPNAME
    app_host = get_local_ip()#settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
    app_port = settings.SWEET_CLOUD_APPPORT
    app_version = settings.SWEET_CLOUD_VERSION
    app_info_appliacations = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, sweet_py_version)
    app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, sweet_py_version,
                                                    state='Running')  # Running  Stoped
    app_runtime_data = zk_plus.create_runtime_data()

    # zk_plus.delete_app_path(app_name)
    zk_plus.set_configuration(app_name, app_port)
    zk_plus.set_dependencies(app_name, app_port)
    zk_plus.set_information(app_name, app_port, app_info_appliacations)
    zk_plus.set_metadata(app_name, app_port)
    zk_plus.set_runtime_data(app_name, app_port, app_runtime_data)
    zk_plus.set_realms(app_name, app_port, app_info_realms)
    print('APP['+ app_name + ']已注册到应用云平台!')

    # def p_8888(*args):
    #     print('p_8888')
    # def p_8889(*args):
    #     print('p_8889')
    # add_data_watch('/realms/python-sweet/8888',p_8888)
    # add_data_watch('/realms/python-sweet/8889', p_8889)
    # add_node_watch('/realms',p_8888)
    # add_node_watch('/applications', p_8889)



def zookeeper_off_line():
    global sweet_settings
    if sweet_settings == None:
        return
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)

    app_name = settings.SWEET_CLOUD_APPNAME
    app_host = get_local_ip()#settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
    app_port = settings.SWEET_CLOUD_APPPORT
    app_version = settings.SWEET_CLOUD_VERSION

    app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, '1.0',
                                                    state='Stoped')  # Running  Stoped
    zk_plus.set_realms(app_name, app_port, app_info_realms)
    print('APP[' + app_name + ']已从应用云平台离线!')
    filename = get_sweet_settings_local_filename()
    if os.path.exists(filename):
        with open(filename,'w') as f:
            f.write(json.dumps({},ensure_ascii=False))

def zookeeper_delete_self(sweet_settings):
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
    app_name = settings.SWEET_CLOUD_APPNAME
    app_port = settings.SWEET_CLOUD_APPPORT
    zk_plus.delete_app_path(app_name,app_port)
    print('APP[' + app_name + ']已从应用云平台删除!')

def check_force_off_line_zookeeper():
    from sys import argv
    _argv_count = len(argv)
    if _argv_count > 1:
        for i in range(1, _argv_count):
            _argv = argv[i].lower()
            if _argv.startswith('--quitzookeeper'):
                print('--quitzookeeper')
                _sweet_settings = get_sweet_settings()
                zookeeper_delete_self(_sweet_settings)
                quit(0)

def isrun():
    filename = get_sweet_settings_local_filename()
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            sweet_settings = json.loads(f.read())
            return not sweet_settings
    else:
        return True

# check_force_off_line_zookeeper()
get_sweet_settings()

import signal

def stop(sig, former):
    zookeeper_off_line()
    quit(0)
signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)
sysstr = platform.system()
if sysstr.lower() != 'windows':
    signal.signal(signal.SIGHUP, stop)

def set_http_port():
    global sweet_settings
    if not sweet_settings:
        return
    from django.core.management.commands.runserver import Command
    Command.default_port = settings.SWEET_CLOUD_APPPORT#get_http_port()

set_http_port()

def set_colud_base_url():
    global zk_plus
    global sweet_settings
    if not zk_plus:
        if sweet_settings:
            _zk_info = sweet_settings['zk']['zkConnectionString']
            _n_p = sweet_settings['zk']['zkDigestAuthString']
            _zk_username = _n_p[:_n_p.find(':')]
            _zk_password = _n_p[_n_p.find(':') + 1:]
            zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
        else:
            return
    urls = zk_plus.get_available_node('app-cloud-log-data-acquisition')
    if urls:
        base_url = urls[0]
    else:
        base_url = None

set_colud_base_url()
# if os.environ.get("RUN_MAIN") == "true":
if isrun():
    get_sweet_params_from_evun_colud()

    if sweet_settings:
        #设置django数据库
        set_django_connection(sweet_settings)
        #向应用云注册
        zookeeper_on_line(sweet_settings)
        # 云基础信息
        set_colud_base_url()

#
# {
#   "code": "success",
#   "data": {
#     "zk": {
#       "zkConnectionString": "10.86.87.180:2181",
#       "zkDigestAuthString": "sweetCloud:sweetCloud123"
#     },
#     "mqLogEnabled": true,
#     "mq": {
#       "connectionString": "10.86.87.118:5672",
#       "user": "sweet",
#       "password": "sweet123",
#       "traceLogQueueName": "request.trace.log",
#       "apmLogQueueName": "apm.log"
#     },
#     "gatewayUrl": "[disabled]",
#     "cloudSharedConfigurations": {
#       "sweet.framework.core.mvc.dynamic-resource.pattern": "/*",
#       "spring.datasource.validationQuery": "select '1' from dual",
#       "sweet.framework.redis.host": "10.86.87.179",
#       "management.contextPath": "/endpoints",
#       "sweet.event.redis.sentinel.master": "masterName",
#       "sweet.framework.session.redis.hosts.type": "sentinel",
#       "sweet.framework.session.redis.password": "",
#       "sweet.framework.session.parse-request.enabled": "true",
#       "spring.datasource.minIdle": "1",
#       "sweet.framework.rabbitmq.metrics.report.interval": "3000",
#       "sweet.framework.redis.hosts": "",
#       "sweet.framework.storage.fastdfs.connection-timeout": "5",
#       "spring.datasource.filters": "stat",
#       "sweet.framework.rabbitmq.userName": "guest",
#       "mybatis.typeAliasesPackage": "",
#       "spring.datasource.testOnReturn": "false",
#       "mybatis.mapperLocations": "classpath*:sql-mappers/**/*.xml,classpath*:sql-mappers-${spring.datasource.db-type:mysql}/**/*.xml",
#       "sweet.framework.core.mvc.error.handler.outputStackTrace": "false",
#       "spring.datasource.db-type": "mysql",
#       "spring.data.mongodb.repositories.enabled": "true",
#       "druid.stat.slowSqlMillis": "5000",
#       "spring.datasource.url": "jdbc:mysql://127.0.0.1:3306/test?useUnicode=true&characterEncoding=UTF-8",
#       "sweet.framework.core.mvc.error.handle.json": "true",
#       "sweet.cloud.service.client.native-service-first.policy": "enabled",
#       "sweet.event.redis.host": "10.86.87.179",
#       "server.context-path": "/",
#       "spring.datasource.driver-class-name": "com.mysql.jdbc.Driver",
#       "sweet.framework.core.i18n.resources.encoding": "utf-8",
#       "sweet.event.redis.password": "",
#       "sweet.framework.session.redis.namespace": "",
#       "sweet.framework.core.mvc.api.pattern": "/*",
#       "spring.freemarker.check-template-location": "false",
#       "sweet.framework.session.header-token.name": "sweet-token",
#       "sweet.framework.session.redis.pool.maxIdle": "8",
#       "sweet.cloud.apm.log.cron": "0/30 * * * * *",
#       "spring.freemarker.settings.template_update_delay": "0",
#       "spring.freemarker.settings.classic_compatible": "true",
#       "hystrix.command.default.execution.isolation.thread.timeoutInMilliseconds": "10000",
#       "sweet.framework.storage.fastdfs.http.anti-steal-token": "false",
#       "sweet.framework.redis.sentinel.master": "masterName",
#       "sweet.framework.session.redis.database": "1",
#       "spring.freemarker.content-type": "text/html",
#       "spring.freemarker.settings.default_encoding": "UTF-8",
#       "spring.freemarker.expose-spring-macro-helpers": "true",
#       "sweet.cloud.apm.update.cron": "0/5 * * * * *",
#       "sweet.framework.socket.server.udp.server-name": "Sweet-UDP-Server",
#       "sweet.framework.rabbitmq.serialize.type": "1",
#       "sweet.framework.socket.server.tcp.enabled": "false",
#       "sweet.framework.socket.server.udp.port": "9999",
#       "sweet.event.redis.pool.maxWait": "-1",
#       "sweet.framework.core.http.request.trace": "true",
#       "sweet.framework.core.rest.invocation.connectTimeout": "3000",
#       "sweet.framework.redis.keys.normalize": "true",
#       "spring.freemarker.allow-session-override": "false",
#       "sweet.framework.core.rest.invocation.warning.limit": "2000",
#       "sweet.framework.socket.server.udp.session.timeout.check-interval": "60",
#       "spring.datasource.minEvictableIdleTimeMillis": "30000",
#       "sweet.framework.socket.server.udp.session.timeout": "120",
#       "springfox.documentation.swagger.v2.path": "/v2/api-docs",
#       "sweet.event.redis.database": "2",
#       "sweet.framework.core.mybatis.page-helper.offsetAsPageNum": "true",
#       "spring.datasource.password": "",
#       "sweet.framework.core.mybatis.mapper.scan.annotation": "org.apache.ibatis.annotations.Mapper",
#       "sweet.framework.redis.timeout": "2000",
#       "sweet.event.redis.pool.maxActive": "50",
#       "sweet.framework.rabbitmq.port": "5672",
#       "spring.datasource.maxActive": "5",
#       "spring.freemarker.expose-session-attributes": "true",
#       "server.session.timeout": "1800",
#       "logging.level.root": "INFO",
#       "sweet.event.redis.pool.minIdle": "0",
#       "sweet.framework.session.redis.port": "6379",
#       "sweet.framework.core.mvc.api.i18n.basename": "classpath*:i18n/api",
#       "spring.output.ansi.enabled": "ALWAYS",
#       "mybatis.typeHandlersPackage": "",
#       "sweet.framework.socket.server.udp.enabled": "false",
#       "sweet.framework.storage.type": "fastdfs",
#       "sweet.framework.redis.pool.maxActive": "50",
#       "sweet.framework.core.i18n.locale.param": "lang",
#       "sweet.framework.redis.pool.maxWait": "-1",
#       "sweet.framework.core.mvc.upload.maxFileSize": "10MB",
#       "spring.datasource.testOnBorrow": "false",
#       "sweet.framework.core.http.restful.doc.swagger.licenseUrl": "http://www.apache.org/licenses/LICENSE-2.0",
#       "hystrix.threadpool.default.coreSize": "20",
#       "sweet.framework.core.i18n.enabled": "true",
#       "sweet.framework.core.http.restful.doc.swagger.title": "${spring.application.name:sweet-application} Restful API Documentation",
#       "sweet.framework.storage.fastdfs.network-timeout": "30",
#       "sweet.event.redis.pool.maxIdle": "8",
#       "spring.profiles.active": " configuration,dev",
#       "sweet.framework.redis.namespace": "",
#       "sweet.event.redis.hosts.type": "sentinel",
#       "sweet.framework.socket.server.tcp.server-name": "Sweet-TCP-Server",
#       "sweet.framework.core.http.defence.csrf": "false",
#       "spring.freemarker.order": "1",
#       "spring.freemarker.cache": "false",
#       "sweet.framework.redis.hosts.type": "sentinel",
#       "sweet.framework.core.http.restful.doc.swagger.termsOfServiceUrl": "http://swagger.io/terms/",
#       "sweet.framework.rabbitmq.host": "10.86.86.13",
#       "logging.pattern.file": "%d{yyyy-MM-dd HH:mm:ss.SSS} ${LOG_LEVEL_PATTERN:-%5p} ${PID:- } %appId %rid --- [%t] %-40.40logger{39} : %m%n${LOG_EXCEPTION_CONVERSION_WORD:%wEx}",
#       "sweet.framework.core.mybatis.page-helper.rowBoundsWithCount": "true",
#       "sweet.framework.session.redis.pool.maxActive": "50",
#       "sweet.framework.storage.fastdfs.tracker-domain": "http://www.igap.cc/",
#       "logging.file": "${user.home:./}/sweet-logs/${spring.application.name:sweet-application}-${spring.application.index:${server.port:8080}}.log",
#       "hystrix.threadpool.default.queueSizeRejectionThreshold": "-1",
#       "sweet.framework.rabbitmq.addresses": "",
#       "sweet.event.redis.namespace": "",
#       "sweet.framework.session.redis.host": "10.86.87.179",
#       "sweet.framework.redis.pool.minIdle": "0",
#       "sweet.framework.session.redis.hosts": "",
#       "sweet.event.redis.consumer.thread-pool-size": "10",
#       "sweet.framework.redis.monitor.output.interval": "300",
#       "spring.datasource.testWhileIdle": "true",
#       "logging.level.cn.evun.sweet.common.tracer.ThreadLocalProcessTracer": "INFO",
#       "sweet.framework.core.http.restful.doc.api.groups": " ",
#       "sweet.framework.storage.fastdfs.tracker-servers": "10.86.87.208:22122,10.86.87.208:22122,10.86.87.208:22122",
#       "sweet.framework.rabbitmq.vhost": "/",
#       "spring.freemarker.enabled": "true",
#       "sweet.framework.core.mvc.error.handle": "true",
#       "sweet.framework.rabbitmq.password": "guest",
#       "spring.data.mongodb.uri": "mongodb://127.0.0.1:27017/test",
#       "sweet.framework.socket.server.tcp.session.timeout.check-interval": "600",
#       "hystrix.threadpool.default.maxQueueSize": "-1",
#       "sweet.cloud.service.client.packages": "",
#       "sweet.framework.redis.password": "",
#       "spring.freemarker.request-context-attribute": "",
#       "server.address": "0.0.0.0",
#       "sweet.framework.core.http.restful.doc.swagger.license": "Apache 2.0",
#       "sweet.framework.core.freemarker.auto-escape-enabled": "false",
#       "sweet.event.redis.log.queue.mame": "sweet:event:bus:log:queue",
#       "sweet.framework.redis.pool.maxIdle": "8",
#       "spring.datasource.maxOpenPreparedStatements": "-1",
#       "sweet.framework.core.i18n.defaultLocale": "zh_CN",
#       "spring.datasource.username": "root",
#       "sweet.framework.session.sso.enabled": "true",
#       "sweet.framework.core.rest.invocation.readTimeout": "-1",
#       "sweet.framework.core.http.defence.xss": "true",
#       "sweet.framework.storage.fastdfs.http.secret-key": "FastDFS1234567890",
#       "sweet.event.redis.hosts": "",
#       "sweet.framework.core.http.restful.doc.modelPackages": "",
#       "spring.datasource.timeBetweenEvictionRunsMillis": "10000",
#       "sweet.framework.socket.server.tcp.session.timeout": "120",
#       "sweet.framework.core.mvc.upload.storageLocation": "",
#       "hystrix.command.default.fallback.enabled": "false",
#       "spring.datasource.type": "com.alibaba.druid.pool.DruidDataSource",
#       "sweet.framework.rabbitmq.autoListen": "true",
#       "spring.datasource.initialSize": "2",
#       "logging.pattern.console": "%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr(${PID:- }){magenta} %appId %rid %clr(---){faint} %clr([%15.15t]){faint} %clr(%-40.40logger{39}){cyan} %clr(:){faint} %m%n${LOG_EXCEPTION_CONVERSION_WORD:%wEx}",
#       "sweet.framework.storage.fastdfs.charset": "UTF-8",
#       "sweet.framework.auth.path-matching.performance.log": "true",
#       "sweet.framework.core.mvc.api.i18n.locale": "zh_CN",
#       "sweet.framework.core.mybatis.mapper.scan.basePackages": "",
#       "sweet.cloud.routing.map": " ",
#       "sweet.framework.redis.database": "0",
#       "sweet.framework.core.i18n.resources.baseName": "i18n/messages",
#       "sweet.framework.session.request-param.name": "__ticket__",
#       "management.address": "0.0.0.0",
#       "sweet.framework.session.redis.sentinel.master": "masterName",
#       "spring.freemarker.allow-request-override": "false",
#       "sweet.framework.redis.port": "6379",
#       "mybatis.configuration.auto-mapping-behavior": "FULL",
#       "hystrix.command.default.circuitBreaker.enabled": "true",
#       "sweet.framework.core.mvc.data-binder.date.useGMTTimeZone": "false",
#       "sweet.framework.session.parse-header.enabled": "true",
#       "sweet.framework.redis.keys.namespace": "",
#       "management.port": "-1",
#       "sweet.framework.core.mybatis.page-helper.reasonable": "true",
#       "server.tomcat.max-threads": "300",
#       "sweet.framework.core.http.restful.doc": "true",
#       "spring.datasource.name": "21",
#       "server.port": "${spring.application.index}",
#       "sweet.framework.auth.mode": "MIXED",
#       "spring.freemarker.charset": "UTF-8",
#       "sweet.framework.core.http.restful.doc.swagger.description": "",
#       "spring.freemarker.suffix": ".ftl",
#       "spring.datasource.poolPreparedStatements": "false",
#       "spring.datasource.maxWait": "-1",
#       "sweet.event.redis.topic.mame": "sweet:event:bus:topic",
#       "sweet.framework.session.redis.pool.maxWait": "-1",
#       "spring.freemarker.template-loader-path": "classpath*:templates/",
#       "sweet.event.redis.port": "6379",
#       "sweet.framework.storage.fastdfs.http.port": "80",
#       "sweet.framework.socket.server.tcp.port": "9999",
#       "spring.freemarker.expose-request-attributes": "false",
#       "spring.freemarker.prefer-file-system-access": "false",
#       "sweet.framework.core.mvc.upload.maxRequestSize": "100MB",
#       "sweet.event.redis.timeout": "2000",
#       "sweet.framework.core.http.restful.doc.swagger.contract": "sweet-group@geely.com",
#       "spring.mvc.throw-exception-if-no-handler-found": "true",
#       "sweet.framework.session.redis.pool.minIdle": "0",
#       "sweet.framework.session.cross-context.enabled": "true"
#     },
#     "applicationInstanceConfigurations": {
#       "spring.datasource.db-type": "",
#       "spring.datasource.username": "postgres",
#       "spring.datasource.password": "postgres",
#       "sweet.framework.socket.server.tcp.port": "9999",
#       "spring.datasource.url": "127.0.0.1:5432",
#       "spring.datasource.name": "sdlc",
#       "spring.datasource.maxActive": "5",
#       "spring.datasource.minIdle": "1"
#     },
#     "attributes": {}
#   },
#   "message": "API调用成功"
# }