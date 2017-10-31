#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/acts
* file   : tools.py
* time   : 2017/10/30
'''
#--------------------#
from datetime import datetime
#----------#
import config as cfg
from ..utils import base
from ..utils import helper as hp
#--------------------#

#--------------------#
def addfile_get_content(f, header_type='py'):
    cur_dir = base.module_dir()
    data = {
        'coder': cfg.get_config('coder'),
        'email': cfg.get_config('email'),
        'module': base.file_name(cur_dir),
        'path': base.dir_name(f) or '.',
        'file': base.file_name(f),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    header = cfg.get_header(header_type)
    return hp.apply_templete(data, header)
#--------------------#
