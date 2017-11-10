from helpers.config_manager import get_cfg
LATEST_VERSION = '2.4.0'

def print_versions():
    print('Reactjo - ' + LATEST_VERSION)
    try:
        cfg = get_cfg()
        for ext in cfg['extensions']:
            path = os.path.join(
                cfg['paths']['reactjorc'], 'extensions', ext['rc_home'], 'entry.py'
            )
            subprocess.run([cfg['py_cmd'], path, '--version'])
    except:
        pass
