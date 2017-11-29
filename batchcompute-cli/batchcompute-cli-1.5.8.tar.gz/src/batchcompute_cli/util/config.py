
try:
    import ConfigParser
except:
    import configparser as ConfigParser

import os


cf = ConfigParser.ConfigParser()

def get_cfg_path():
    usr_home = os.path.expanduser('~')
    cfg_dir = os.path.join(usr_home, '.batchcompute')
    if(not os.path.exists(cfg_dir)):
        os.makedirs(cfg_dir)
    cfg_path = os.path.join(cfg_dir, 'cliconfig')
    return cfg_path

COMMON = 'common'

ALL = ['region','accesskeyid','accesskeysecret','osspath','locale','ssl','god',
                              'defaultimage','defaulttype','defaultcluster','version',
                              'oss_region','oss_key','oss_id','qsubuser','vpc_cidr_block']

def getConfigs(section, keys=ALL):
    '''
    section: currently support 'common' only
    keys: array, example: ['region','accesskeyid']
    '''
    cfg_path = get_cfg_path()

    if(os.path.exists(cfg_path)):
        cf.read(cfg_path)
        mk={}

        for k in keys:
            try:
                mk[k] = cf.get(section, k)
            except:
                pass
        return mk
    else:
        return {}

def setConfigs(section, opt):
    cfg_path = get_cfg_path()
    with open(cfg_path,'w') as f:
        cf.remove_section(section)
        cf.add_section(section)
        for k in opt:
            cf.set(section, k, opt[k])
        cf.write(f)
        return True
    return False

def setConfig(section, key , value):
    cfg_path = get_cfg_path()
    with open(cfg_path,'w') as f:
        if section not in cf.sections():
            cf.add_section(section)
        cf.set(section, key, value)
        cf.write(f)
        return True
    return False

def removeConfig(section, key=ALL):
    cfg_path = get_cfg_path()
    if(os.path.exists(cfg_path)):
        try:
            with open(cfg_path,'w') as f:
                if isinstance(key, (tuple,list)):
                    for k in key:
                       cf.remove_option(section, k)
                else:
                    cf.remove_option(section, key)
                cf.write(f)
        except:
            pass
    else:
        return False

def get_oss_path():
    pre_oss_path = getConfigs(COMMON,['osspath']).get('osspath')
    if not pre_oss_path:
        raise Exception('Not found osspath, type: "bcs set -h" for more help')

    pre_oss_path = '%s/' % pre_oss_path.rstrip('/')
    return pre_oss_path

def isGod():
    return getConfigs(COMMON, ['god']).get('god')

def getRegion():
    region= getConfigs(COMMON, ['region']).get('region')
    if region:
        return region
    else:
        raise Exception('you need to login first')

def get_qsubuser():
    qsubuser = getConfigs(COMMON, ['qsubuser']).get('qsubuser')
    return qsubuser if qsubuser else 'root'

def get_oss_region():
    m= getConfigs(COMMON, ['region','oss_region'])

    region = m.get('oss_region') or m.get('region')
    if region:
        return region
    else:
        raise Exception('you need to login first')

def get_default_image():
    img = getConfigs(COMMON, ['defaultimage']).get('defaultimage')
    if not img:
        raise Exception('No found default image\n  using:"bcs set -i <img-id>" to set default image\n  type: "bcs set -h" for more help')
    return img

def get_default_instance_type():
    img = getConfigs(COMMON, ['defaulttype']).get('defaulttype')
    if not img:
        raise Exception('No found default instance type\n  using:"bcs set -t <instance-type>" to set default instance type\n  type: "bcs set -h" for more help')
    return img


def get_default_instance_cluster():
    img = getConfigs(COMMON, ['defaultcluster']).get('defaultcluster')
    if not img:
        raise Exception('No found default cluster\n  using:"bcs set -c <cluster-id>" to set default cluster\n  type: "bcs set -h" for more help')
    return img

