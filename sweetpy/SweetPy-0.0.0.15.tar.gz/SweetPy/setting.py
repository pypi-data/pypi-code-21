from django.conf import settings
import requests
import json
from SweetPy.zookeeper_plus import ZookeeperPlus
import platform
import os

sweet_settings = None
def get_sweet_settings():
    global sweet_settings
    if sweet_settings:
        return sweet_settings

    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    app_host = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST

    sysstr = platform.system()
    if sysstr.lower() == 'windows':
        filename = os.environ["TMP"] + '\\' + app_name + app_host + str(app_port) + '.json'
    else:
        filename = os.environ["TMP"] + '/' + app_name + app_host + str(app_port) + '.json'
    if not os.path.exists(filename):
        return {}
    with open(filename,'r') as f:
        sweet_settings = json.loads(f.read())
        return sweet_settings

def write_sweet_settings(setting):
    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    app_host = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST

    sysstr = platform.system()
    if sysstr.lower() == 'windows':
        filename = os.environ["TMP"] + '\\' + app_name + app_host + str(app_port) + '.json'
    else:
        filename = os.environ["TMP"] + '/' + app_name + app_host + str(app_port) + '.json'
    with open(filename, 'w') as f:
        f.write(json.dumps(setting,ensure_ascii=False))

def get_sweet_params():
    global sweet_settings
    if sweet_settings:
        return
    if (hasattr(settings,'SWEETPY_IS_CONNECTED_EVUN_CLOUD')) and settings.SWEETPY_IS_CONNECTED_EVUN_CLOUD:
        url = settings.SWEETPY_EVUN_CLOUD_REGISTER_URL + '?' + \
              'application=' + settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME + \
              '&index=' + settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT + \
              '&version=' + settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_VERSION + \
              '&ticket=' + settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_TICKET

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
              "'spring.datasource.db-type':'数据库类型postgres,mysql等',"
              "'spring.datasource.username':'用户名',"
              "'spring.datasource.password':'密码',"
              "'spring.datasource.url':'IP地址和端口号以:号分隔',"
              "'spring.datasource.maxActive':'连接池大小',"
              "'spring.datasource.name':'要连接的仓库名',"
              "'spring.datasource.minIdle':'连接池回收时间(暂时未启用)']")
        quit(0)

def zookeeper_on_line(sweet_settings):
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)

    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_host = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    app_version = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_VERSION
    app_info_appliacations = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, '1.0')
    app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, '1.0',
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

def zookeeper_off_line():
    global sweet_settings
    if sweet_settings == None:
        return
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)

    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_host = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    app_version = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_VERSION

    app_info_realms = zk_plus.create_app_infomation(app_name, app_version, app_host, app_port, '1.0',
                                                    state='Stoped')  # Running  Stoped
    zk_plus.set_realms(app_name, app_port, app_info_realms)
    print('APP[' + app_name + ']已从应用云平台离线!')

def zookeeper_delete_self(sweet_settings):
    _zk_info = sweet_settings['zk']['zkConnectionString']
    _n_p = sweet_settings['zk']['zkDigestAuthString']
    _zk_username = _n_p[:_n_p.find(':')]
    _zk_password = _n_p[_n_p.find(':') + 1:]
    zk_plus = ZookeeperPlus(_zk_info, _zk_username, _zk_password)
    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    zk_plus.delete_app_path(app_name,app_port)
    print('APP[' + app_name + ']已从应用云平台删除!')
    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT
    app_host = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_HOST

    sysstr = platform.system()
    if sysstr.lower() == 'windows':
        filename = os.environ["TMP"] + '\\' + app_name + app_host + str(app_port) + '.json'
    else:
        filename = os.environ["TMP"] + '/' + app_name + app_host + str(app_port) + '.json'
    if os.path.exists(filename):
        os.remove(filename)

def check_force_off_line_zookeeper():
    from sys import argv
    _argv_count = len(argv)
    if _argv_count > 1:
        for i in range(1, _argv_count):
            _argv = argv[i].lower()
            if _argv.startswith('--quitzookeeper'):
                print('--quitzookeeper')
                get_sweet_params()
                global sweet_settings
                zookeeper_delete_self(sweet_settings)
                quit(0)

def isrun():
    app_name = settings.SWEETPY_EVUN_CLOUD_REGISTER_APPNAME
    app_port = settings.SWEETPY_EVUN_CLOUD_REGISTER_APP_PORT

    sysstr = platform.system()
    if sysstr.lower() == 'windows':
        filename = os.environ["TMP"] + '\\' + app_name + str(app_port) + '.tmp'
    else:
        filename = os.environ["TMP"] + '/' + app_name + str(app_port) + '.tmp'
    if os.path.exists(filename):
        os.remove(filename)
        return True
    else:
        with open(filename, 'w') as f:
            f.write('')
        return False

# check_force_off_line_zookeeper()

if isrun():
    import signal
    def stop(sig, former):
        zookeeper_off_line()
        quit(0)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    sysstr = platform.system()
    if sysstr.lower() != 'windows':
        signal.signal(signal.SIGHUP, stop)

    get_sweet_params()

    if sweet_settings:
        #设置django数据库
        set_django_connection(sweet_settings)
        #向应用云注册
        zookeeper_on_line(sweet_settings)
