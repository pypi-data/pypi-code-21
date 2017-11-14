#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/acts
* file   : config.py
* time   : 2017/10/27
'''
#--------------------#
from ..utils import base
from ..utils import helper as hp
from ..utils import templete as tp
#--------------------#

#--------------------#
version = '1.0.1'
path_home = base.dir_home()
config_path = base.path_join(path_home, '.api-cli')
config_file = base.path_join(config_path, 'config')
#--------------------#

#--------------------#
def get_cfg(b_read_file=True):
    default = {
        'coder': '',
        'email': '',
        #
        'git.api-frame.git': 'https://gitee.com/dzlua/api-frame.git',
        'git.api-frame.path': base.path_join(config_path, 'git/api-frame/'),
    }
    if b_read_file:
        return hp.get_config(config_file, default)
    else:
        return hp.get_config(None, default)
#----------#
def set_cfg(cfg):
    hp.set_config(config_file, cfg)
#--------------------#

#--------------------#
def set_config(key, value):
    cfg = get_cfg()
    cfg['user'][key] = value
    set_cfg(cfg)
#----------#
def get_config(key, session='user'):
    cfg = get_cfg()
    return cfg[session][key]
#----------#
def get_configs(keys, session='user'):
    cfg = get_cfg()
    datas = cfg[session]
    rets = {}
    for k in keys:
        try:
            rets[k] = datas[k]
        except:
            pass
    return rets
#----------#
def get_config_all(session='user'):
    cfg = get_cfg()
    return cfg[session]
#----------#
def del_config(key):
    cfg = get_cfg()
    cfg.remove_option('user', key)
    set_cfg(cfg)
#----------#
def del_configs(keys):
    cfg = get_cfg()
    for k in keys:
        cfg.remove_option('user', k)
    set_cfg(cfg)
#--------------------#

#--------------------#
def get_header_file():
    return base.path_join(
        config_path,
        get_config('header', 'templete') )
#----------#
def get_header(header_type='py'):
    cfg = hp.get_config(get_header_file())
    return cfg['sys'][header_type]
#----------#
def get_header_types():
    cfg = hp.get_config(get_header_file())
    return cfg['sys']
#--------------------#

#--------------------#
def set_config_to_default():
    base.del_dir(config_path)
    #
    cfg = get_cfg(False)
    cfg['user'] = {}
    cfg['templete'] = {
        'header': 'header.cfg'
    }
    set_cfg(cfg)
    #
    file = get_header_file()
    cfg = hp.get_config(file, tp.header)
    cfg['sys'] = {}
    hp.set_config(file, cfg)
#----------#
def init():
    if not base.is_exist(config_file):
        set_config_to_default()
    #----------#
#--------------------#

#--------------------#
init()
#--------------------#
