#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/acts
* file   : create.py
* time   : 2017/10/30
'''
#--------------------#
from datetime import datetime
#----------#
import config as cfg
from ..utils import helper as hp
from ..utils import base
#--------------------#

#--------------------#
def templete_type(ext):
    tps = cfg.get_header_types()
    for tp in tps:
        if '.' + tp == ext:
            return tp
    return None
#----------#
def get_header(f, header_type, moudle=None):
    cur_dir = base.module_dir()
    data = {
        'coder': cfg.get_config('coder'),
        'email': cfg.get_config('email'),
        'module': moudle or base.file_name(cur_dir),
        'path': base.dir_name(f) or '.',
        'file': base.file_name(f),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    header = cfg.get_header(header_type)
    return hp.apply_templete(data, header)
#--------------------#

#--------------------#
def create(name):
    md_path = base.module_dir()
    path = base.path_join(md_path, name)
    git = cfg.get_config('git.api-frame.git')
    git_path = cfg.get_config('git.api-frame.path')

    if base.is_exist(path):
        print(u'Error: exist %s.' % path)
        return

    # rm
    base.del_dir(git_path)
    #
    print('clone ...')
    if not hp.git_clone(git, git_path):
        print('Error: on clone api-frame.')
        return
    #
    errs = []
    files = base.dir_files(git_path, dirs=['.git'])
    print('files: %s, writing...' % len(files))
    for f in files:
        bok = False
        ff = base.path_join(git_path, f)
        df = base.path_join(path, f)
        tp = templete_type(base.file_ext(f)[1])
        if not tp:
            bok = base.file_cp(ff, df)
        else:
            header = get_header(f, tp, name)
            header = hp.str_replace_by_line(header, '', 8, -1, linc=True)
            cont = base.read_file(ff)
            cont = hp.str_replace_by_line(cont, header, 0, 7)
            bok = base.create_file(df, cont)
        print('%s %s -> %s' % (bok,tp,f))
    #
    print('files: %s, errors: %s' % (len(files), len(errs)) )
    if len(errs) == 0:
        print('Done!')
#--------------------#
