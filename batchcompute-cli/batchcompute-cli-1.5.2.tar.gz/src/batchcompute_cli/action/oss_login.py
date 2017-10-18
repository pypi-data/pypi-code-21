
from batchcompute.utils.functions import ConfigError
from terminal import Logger, prompt, password, green

from ..util import config, oss_client

log = Logger()


def login(region, accessKeyId=None, accessKeySecret=None):

    opt = config.getConfigs(config.COMMON)

    opt['oss_region'] = region

    if accessKeyId and accessKeySecret:

        opt['oss_id'] = accessKeyId
        opt['oss_key'] = accessKeySecret

    else:
        opt['oss_id'] = prompt('input accessKeyId')
        opt['oss_key'] = password('and accessKeySecret')

    try:
        oss_client.check_client(opt)

        config.setConfigs(config.COMMON, opt)

        print(green('login success' ))

    except Exception as e:
        raise Exception(e)

def logout():
    config.removeConfig(config.COMMON, ['oss_region','oss_id','oss_key','osspath'])
