from helpers.config_manager import get_cfg, set_cfg
import os, shutil, subprocess, stat
from helpers.worklist import worklist as wl

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update():
    cfg = get_cfg()
    extensions = os.path.join(cfg['paths']['reactjorc'], 'extensions')

    # Remove all extensions and reinstall them.
    if os.path.exists(extensions):
        shutil.rmtree(extensions, onerror=remove_readonly)
    os.mkdir(extensions)

    for ext in cfg['extensions']:
        path = os.path.join(extensions, ext['rc_home'])

        if 'branch' in ext:
            subprocess.call(['git', 'clone', '-b', ext['branch'], ext['uri'], path])
        else:
            subprocess.call(['git', 'clone', '-b', 'master', ext['uri'], path])

        dependencies = path + '/requirements.txt'
        if os.path.exists(dependencies):
            deps = open(dependencies, 'r').read()
            if len(deps) > 0:
                subprocess.call(['pip', 'install', '-r', dependencies])

    wl('Updated extensions')
