import json
import logging as logging_module
import os
import platform

import sys

import subprocess

from whatap import build
from whatap.util.date_util import DateUtil

__version__ = build.version

LOGGING_MSG_FORMAT = '[%(asctime)s] : - %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d  %H:%M:%S'

logging = logging_module.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

ROOT_DIR = __file__


class ContextFilter(logging_module.Filter):
    def __init__(self):
        super(ContextFilter, self).__init__()
        self.last_id = None
    
    def filter(self, record):
        try:
            if record.id:
                if self.last_id == record.id:
                    return False
                
                self.last_id = record.id
                return True
        
        except Exception as e:
            record.id = ''
            return True


from whatap.conf.configure import Configure as conf

CONFIG_FILE_NAME = 'whatap.conf'
PLUGIN_FILE_NAME = 'plugin.json'
LOG_FILE_NAME = 'whatap-hook.log'


class Logger(object):
    def __init__(self):
        self.logger = logging
        self.logger.addFilter(ContextFilter())
        self.handler = None
        
        self.create_log()
    
    def create_log(self):
        os.environ['WHATAP_LOGS'] = os.path.join(os.environ['WHATAP_HOME'],
                                                 'logs')
        if not os.path.exists(os.environ['WHATAP_LOGS']):
            try:
                os.mkdir(os.environ['WHATAP_LOGS'])
            
            except Exception as e:
                print('WHATAP: LOG FILE WRITE ERROR.')
                print(
                    'WHATAP: Try to execute command. \n  {}'.format(
                        'sudo mkdir -m 777 -p $WHATAP_HOME/logs`'))
        
        self.print_log()
    
    def print_log(self):
        try:
            if self.handler:
                self.logger.removeHandler(self.handler)
            
            temp_logging_msg_format = '[%(asctime)s] : %(id)s - %(message)s'
            logging_format = logging_module.Formatter(
                fmt=temp_logging_msg_format, datefmt=LOGGING_DATE_FORMAT)
            
            fh = logging_module.FileHandler(
                os.path.join(os.environ['WHATAP_LOGS'], LOG_FILE_NAME))
            fh.setFormatter(logging_format)
            self.logger.addHandler(fh)
            self.handler = fh
            
            self.logger.setLevel(logging_module.DEBUG)
        except Exception as e:
            print('WHATAP: LOGGING ERROR: {}'.format(e))
        else:
            self.print_whatap()
    
    def print_whatap(self):
        str = '\n' + \
              ' _      ____       ______' + build.app + '-AGENT  \n' + \
              '| | /| / / /  ___ /_  __/__ ____' + '\n' + \
              '| |/ |/ / _ \\/ _ `// / / _ `/ _ \\' + '\n' + \
              '|__/|__/_//_/\\_,_//_/  \\_,_/ .__/' + '\n' + \
              '                          /_/' + '\n' + \
              'Just Tap, Always Monitoring' + '\n' + \
              'WhaTap ' + build.app + ' Agent version ' + build.version + ', ' + build.release_date + '\n\n'
        
        str += '{0}: {1}\n'.format('WHATAP_HOME', os.environ['WHATAP_HOME'])
        str += '{0}: {1}\n'.format('Config',
                                   os.path.join(os.environ['WHATAP_HOME'],
                                                os.environ['WHATAP_CONFIG']))
        str += '{0}: {1}\n\n'.format('Logs', os.environ['WHATAP_LOGS'])
        
        print(str)
        logging.debug(str)


def read_file(home, file_name):
    data = ''
    try:
        f = open(os.path.join(os.environ.get(home), file_name), 'r+')
        data = f.readline()
        f.close()
    finally:
        return data


def write_file(home, file_name, value):
    try:
        f = open(os.path.join(os.environ.get(home), file_name), 'w+')
        f.write(value)
        f.close()
    except Exception as e:
        print('WHATAP: WHATAP HOME ERROR.')
        print(
            'WHATAP: Try to execute command. \n  {}'.format(
                '`sudo chmod -R 777 $WHATAP_HOME`'))
        return False
    else:
        return True


def check_whatap_home(target='WHATAP_HOME'):
    whatap_home = os.environ.get(target)
    if not whatap_home:
        print('WHATAP: ${} is empty'.format(target))
    
    return whatap_home


def init_config(home):
    whatap_home = os.environ.get(home)
    if not whatap_home:
        whatap_home = read_file(home, home.lower())
        if not whatap_home:
            whatap_home = os.getcwd()
            print('WHATAP: WHATAP_HOME is empty')
            print(
                'WHATAP: WHATAP_HOME set default CURRENT_WORKING_DIRECTORY value')
            print('CURRENT_WORKING_DIRECTORY is {}\n'.format(whatap_home))
    
    if not write_file(home, home.lower(), whatap_home):
        return False
    
    os.environ[home] = whatap_home
    config_file = os.path.join(os.environ[home],
                               CONFIG_FILE_NAME)
    
    if not os.path.exists(config_file):
        with open(
                os.path.join(os.path.dirname(__file__),
                             CONFIG_FILE_NAME),
                'r+') as f:
            content = f.read()
            try:
                with open(config_file, 'w+') as new_f:
                    new_f.write(content)
            except Exception as e:
                print('WHATAP: PERMISSION ERROR: {}'.format(e))
                print(
                    'WHATAP: Try to execute command. \n  {}'.format(
                        '`sudo chmod -R 777 $WHATAP_HOME`'))
                return False
    
    return True


def update_config(home, opt_key, opt_value):
    config_file = os.path.join(os.environ[home],
                               CONFIG_FILE_NAME)
    
    try:
        with open(config_file, 'r+') as f:
            is_update = False
            content = ''
            for line in f:
                if line:
                    key = line.split('=')[0].strip()
                    if key == opt_key:
                        is_update = True
                        line = '{0}={1}\n'.format(key, opt_value)
                    
                    content += line
            if not is_update:
                content += '{0}={1}\n'.format(opt_key, opt_value)
            open(config_file, 'w+').write(content)
    
    except Exception as e:
        print('WHATAP: OPTION ERROR: {}'.format(e))


def config(home):
    os.environ['WHATAP_CONFIG'] = CONFIG_FILE_NAME
    
    from whatap.conf.configure import Configure as conf
    if conf.init():
        from whatap.trace import PacketEnum, UdpSession
        PacketEnum.PORT = int(conf.net_udp_port)
        
        plugin_file = os.path.join(os.environ[home], PLUGIN_FILE_NAME)
        if conf.plugin and not os.path.exists(plugin_file):
            content = open(
                os.path.join(os.path.dirname(__file__),
                             PLUGIN_FILE_NAME),
                'r+').read()
            try:
                os.mknod(plugin_file)
                new = open(plugin_file, 'w+')
                new.write(content)
                new.close()
            except Exception as e:
                logging.debug(e, extra={'id': 'PLUGIN FILE ERROR'})
                logging.debug(
                    'WHATAP: Try to execute command. \n  {}'.format(
                        '`sudo chmod -R 777 $WHATAP_HOME`'))
        
        hooks(home)


from whatap.trace.trace_import import ImportFinder
from whatap.trace.trace_module_definication import DEFINICATION, IMPORT_HOOKS, \
    PLUGIN


def hooks(home):
    try:
        for key, value_list in DEFINICATION.items():
            for value in value_list:
                if len(value) == 3 and not value[2]:
                    continue
                
                IMPORT_HOOKS[value[0]] = {'def': value[1],
                                          'module': '{0}.{1}.{2}.{3}'.format(
                                              'whatap',
                                              'trace',
                                              'mod',
                                              key)}
    except Exception as e:
        logging.debug(e, extra={'id': 'MODULE ERROR'})
    finally:
        try:
            plugin_file = os.path.join(os.environ.get(home, ''),
                                       'plugin.json')
            if conf.plugin and os.path.exists(plugin_file):
                from whatap.trace.mod.plugin import instrument_plugin
                
                with open(plugin_file, 'r+') as data_file:
                    PLUGIN.update(json.load(data_file))
                    delete_key = None
                    for key, value in PLUGIN.items():
                        if key.startswith("["):
                            delete_key = key
                        else:
                            DEFINICATION["plugin"].append(
                                (key, 'instrument_plugin'))
                    
                    del PLUGIN[delete_key]
                
                key = 'plugin'
                for value in DEFINICATION[key]:
                    IMPORT_HOOKS[value[0]] = {'def': value[1],
                                              'module': '{0}.{1}.{2}.{3}'.format(
                                                  'whatap',
                                                  'trace',
                                                  'mod',
                                                  key)}
        
        except Exception as e:
            logging.debug(e, extra={'id': 'PLUGIN ERROR'})
        finally:
            sys.meta_path.insert(0, ImportFinder())
            logging.debug('WHATAP AGENT START!', extra={'id': 'WA000'})


def agent():
    home = 'WHATAP_HOME'
    whatap_home = os.environ.get(home)
    if not whatap_home:
        whatap_home = read_file(home, home.lower())
        if not whatap_home:
            whatap_home = os.getcwd()
            
            print('WHATAP: WHATAP_HOME is empty')
            print(
                'WHATAP: WHATAP_HOME set default CURRENT_WORKING_DIRECTORY value')
            print('CURRENT_WORKING_DIRECTORY is {}\n'.format(whatap_home))
    
    if write_file(home, home.lower(), whatap_home):
        os.environ['WHATAP_HOME'] = whatap_home
        
        go()
        config(home)


ARCH = {
    'x86_64': 'amd64',
    'x86': '386',
    'x86_32': '386',
    'ARM': 'arm',
    'AArch64': 'arm64',
}

AGENT_NAME = 'whatap_python'


def go(batch=False):
    os.environ['WHATAP_VERSION'] = build.version
    
    os.environ['whatap.start'] = str(DateUtil.now())
    
    os.environ['python.uptime'] = str(DateUtil.datetime())
    os.environ['python.version'] = sys.version
    
    os.environ['os.release'] = platform.release()
    
    os.environ['sys.version_info'] = str(sys.version_info)
    os.environ['sys.executable'] = sys.executable
    os.environ['sys.path'] = str(sys.path)
    
    if not batch:
        home = 'WHATAP_HOME'
        file_name = AGENT_NAME + '.pid'
    else:
        home = 'WHATAP_HOME_BATCH'
        file_name = AGENT_NAME + '.pid.batch'
    
    if go_kill(home, file_name):
        try:
            agent_cwd = os.environ.get(home)
            if os.path.exists(os.path.join(agent_cwd, AGENT_NAME)):
                os.remove(os.path.join(agent_cwd, AGENT_NAME))

            source_cwd = os.path.join(os.path.join(os.path.dirname(__file__), 'agent'), platform.system().lower(),
                                      ARCH[platform.machine()])
            
                
            os.symlink(os.path.join(source_cwd, AGENT_NAME),
                       os.path.join(agent_cwd, AGENT_NAME))
            
            os.environ['whatap.enabled'] = 'True'
            process = subprocess.Popen('./{0}'.format(AGENT_NAME),
                                       cwd=agent_cwd)
            
            # Write PID file
            write_file(home, file_name, str(process.pid))
        
        except Exception as e:
            print('WHATAP: AGENT ERROR: {}'.format(e))
        else:
            print('WHATAP: AGENT UP! (process name: {})\n'.format(AGENT_NAME))


import signal


def go_kill(home, file_name):
    try:
        pids = subprocess.check_output('pgrep {0}'.format(AGENT_NAME),
                                       shell=True).split()
    except Exception as e:
        return True
    else:
        pid = read_file(home, file_name)
        try:
            if len(pid.split()):
                os.kill(int(pid), signal.SIGKILL)
            else:
                if not read_file('WHATAP_HOME', AGENT_NAME + '.pid') \
                        and not read_file('WHATAP_HOME_BATCH',
                                          AGENT_NAME + '.pid.batch'):
                    for pid in pids:
                        os.kill(int(pid), signal.SIGKILL)
                    
                    write_file(home, AGENT_NAME + '.pid', '')
                    write_file(home, AGENT_NAME + '.pid.batch', '')
        
        
        except Exception as e:
            logging.debug(e, extra={'id': ' AGENT UPGRADE ERROR'})
            logging.debug(
                'Try to execute command. \n  {}'.format(
                    '`ps -ef | grep {}`'.format(AGENT_NAME)))
            logging.debug(
                'Next, `sudo kill -9 {}` or `sudo killall {}`'.format(
                    pid, AGENT_NAME))
            return False
        else:
            print('WHATAP: AGENT DOWN..')
            return True


from whatap.trace.mod.application_wsgi import interceptor, start_interceptor, \
    end_interceptor, trace_handler


def register_app(fn):
    @trace_handler(fn, True)
    def trace(*args, **kwargs):
        callback = None
        try:
            environ = args[0]
            callback = interceptor((fn, environ), *args, **kwargs)
        except Exception as e:
            logging.debug('WHATAP(@register_app): ' + str(e),
                          extra={'id': 'WA777'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    if not os.environ.get('whatap.enabled'):
        agent()
    
    return trace


def method_profiling(fn):
    def trace(*args, **kwargs):
        callback = None
        try:
            ctx = start_interceptor(service_name=fn.__name__)
            callback = fn(*args, **kwargs)
            end_interceptor(ctx.thread_id)
        except Exception as e:
            logging.debug('WHATAP(@method_profiling): ' + str(e),
                          extra={'id': 'WA776'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    if not os.environ.get('whatap.enabled'):
        agent()
    
    return trace


def batch_agent():
    home = 'WHATAP_HOME_BATCH'
    batch_home = os.environ.get(home)
    if not batch_home:
        if not read_file(home, home.lower()):
            print('WHATAP: WHATAP_HOME_BATCH is empty')
            return
    
    if write_file(home, home.lower(), batch_home):
        os.environ['WHATAP_HOME_BATCH'] = batch_home
        os.environ['WHATAP_HOME'] = batch_home
        go(batch=True)


def batch_profiling(fn):
    import inspect
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    
    def trace(*args, **kwargs):
        if not os.environ.get('whatap.batch.enabled'):
            home = 'WHATAP_HOME_BATCH'
            batch_home = read_file(home, home.lower())
            if not batch_home:
                print(
                    'WHATAP(@batch_profiling): try, whatap-start-batch')
                return fn(*args, **kwargs)
            else:
                os.environ['whatap.batch.enabled'] = 'True'
                os.environ['WHATAP_HOME_BATCH'] = batch_home
                os.environ['WHATAP_HOME'] = batch_home
                config(home)
        
        callback = None
        try:
            ctx = start_interceptor(
                service_name=module.__file__.split('/').pop())
            
            callback = fn(*args, **kwargs)
            end_interceptor(ctx.thread_id)
        except Exception as e:
            logging.debug('WHATAP(@batch_profiling): ' + str(e),
                          extra={'id': 'WA777'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    return trace
