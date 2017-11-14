from ..externals.ecs import EcsClient
from ..util import config


def __get_cfg():
    c = config.getConfigs(config.COMMON,['region','accesskeyid','accesskeysecret',
                                            'oss_region', 'oss_id', 'oss_key'])
    return {
        'region': c.get('oss_region') or c.get('region'),
        'accesskeyid':  c.get('oss_id') or c.get('accesskeyid') ,
        'accesskeysecret': c.get('oss_key') or c.get('accesskeysecret')
    }

def get_endpoint():
    return 'http://ecs.aliyuncs.com'


def describeInstances(opt):
    cfg = opt or __get_cfg()

    aid = cfg.get('oss_id') or cfg.get('accesskeyid')
    akey = cfg.get('oss_key') or cfg.get('accesskeysecret')

    region = cfg.get('oss_region') or cfg.get('region')

    clt = EcsClient(aid, akey)
    result = clt.DescribeInstanceTypes(region)

    return result.get('InstanceTypes').get('InstanceType')


