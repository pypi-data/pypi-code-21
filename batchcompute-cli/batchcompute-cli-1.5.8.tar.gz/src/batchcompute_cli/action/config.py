from ..util import config,client,oss_client,util
from terminal import green,bold,yellow
from .. import const
from ..const import CMD
import re
FALSE_ARR = ['', 'null', 'None', 'false', 'False','0']

def all(region=None, osspath=None, locale=None, image=None, type=None, cluster=None, qsubuser=None, vpc_cidr_block=None, version=None, ssl=None, god=None):
    if not region and not osspath and not locale and not image and not type and not cluster and not qsubuser and not vpc_cidr_block and not version and not ssl and not god:
        show_config()
    else:
        if region:
            update_region(region)
        if osspath:
            update_osspath(osspath)
        if locale:
            update_locale(locale)
        if image:
            update_image(image)
        if type:
            update_type(type)
        if cluster:
            update_cluster(cluster)
        if version:
            update_version(version)
        if ssl:
            update_ssl(ssl)
        if qsubuser:
            update_qsubuser(qsubuser)
        if vpc_cidr_block:
            update_vpc_cidr_block(vpc_cidr_block)
        if god:
            update_god(god)
        print(green('done'))

def update_region(region):
    m = config.getConfigs(config.COMMON)
    m['region'] = region

    try:
        client.check_client(m)
        config.setConfigs(config.COMMON, m)

        util.set_default_type_n_image()

    except Exception as e:
        e = '%s' % e
        if 'nodename nor servname provided' in e:
            raise Exception('Invalid region %s\n %s' % (region,e))
        else:
            raise Exception(e)

def update_vpc_cidr_block(vpc_cidr_block):
    m = config.getConfigs(config.COMMON)

    vpc_cidr_block = vpc_cidr_block.strip()
    if vpc_cidr_block in FALSE_ARR:
        config.removeConfig(config.COMMON, 'vpc_cidr_block')
    else:
        if re.match(r'^[0-9\.\/]+$', vpc_cidr_block):
            m['vpc_cidr_block'] = vpc_cidr_block
            config.setConfigs(config.COMMON, m)
        else:
            raise Exception('Invalid vpc_cidr_block format')


def update_qsubuser(qsubuser):
    m = config.getConfigs(config.COMMON)

    qsubuser = qsubuser.strip()
    if qsubuser in FALSE_ARR:
        config.removeConfig(config.COMMON, 'qsubuser')
    else:
        if re.match(r'^[0-9A-Za-z]+$', qsubuser):

            m['qsubuser'] = qsubuser
            config.setConfigs(config.COMMON, m)
        else:
            raise Exception('Invalid qsubuser, it should consist of letters and numbers ')


def update_osspath(osspath):
    if osspath in FALSE_ARR:
        # remove
        config.removeConfig(config.COMMON, 'osspath')
    else:
        m = config.getConfigs(config.COMMON)

        if not osspath.endswith('/'):
            osspath += '/'
        m['osspath'] = osspath

        try:
            oss_client.check_client(m)
            config.setConfigs(config.COMMON, m)

        except Exception as e:
            raise Exception('Invalid osspath %s\n  %s' % (osspath,e)) if m.get('osspath') else e


def update_locale(locale):
    if locale in FALSE_ARR:
        # remove
        config.removeConfig(config.COMMON, 'locale')
    else:
        m = config.getConfigs(config.COMMON)
        if locale not in const.LOCALE_SUPPORTED:
            raise Exception('Unsupported locale')

        m['locale'] = locale
        config.setConfigs(config.COMMON, m)

def update_image(image):
    image = image.strip()
    if image in FALSE_ARR:
        # remove
        config.removeConfig(config.COMMON, 'defaultimage')
    else:
        m = config.getConfigs(config.COMMON)
        m['defaultimage'] = image
        config.setConfigs(config.COMMON, m)

def update_type(type):
    type = type.strip()
    if type in FALSE_ARR:
        # remove
        config.removeConfig(config.COMMON, 'defaulttype')
    else:
        m = config.getConfigs(config.COMMON)

        itMap = client.get_ins_type_map()

        if not itMap.get(type):
            raise Exception("'%s' is invalid, type '%s t' for more" % (type, CMD))

        m['defaulttype'] = type
        config.setConfigs(config.COMMON, m)

def update_cluster(cluster):
    cluster = cluster.strip()
    if cluster in FALSE_ARR:
        # remove
        config.removeConfig(config.COMMON, 'defaultcluster')
    else:
        m = config.getConfigs(config.COMMON)

        clusters = client.list_clusters()
        clsIdMap = {}
        for n in clusters.get('Items'):
            clsIdMap[n.get('Id')] = 1

        if not clsIdMap.get(cluster):
            raise Exception("'%s' is invalid, type '%s c' for more" % (type, CMD))

        m['defaultcluster'] = cluster
        print(m)
        config.setConfigs(config.COMMON, m)


def update_version(version):
    m = config.getConfigs(config.COMMON)

    version = version.strip()
    if version in FALSE_ARR:
        config.removeConfig(config.COMMON, 'version')
    else:
        m['version'] = version

        try:
            client.check_client(m)
            config.setConfigs(config.COMMON, m)
        except Exception as e:
            raise Exception('Invalid version %s' % version)

def update_ssl(ssl):
    m = config.getConfigs(config.COMMON)
    ssl = ssl.strip()
    if ssl in FALSE_ARR:
        m['ssl'] = 'false'
        config.setConfigs(config.COMMON, m)
    else:
        config.removeConfig(config.COMMON, 'ssl')

def update_god(god):
    m = config.getConfigs(config.COMMON)
    god = god.strip()
    if god not in FALSE_ARR:
        m['god'] = '1'
        config.setConfigs(config.COMMON, m)
    else:
        config.removeConfig(config.COMMON, 'god')


def show_config():
    try:
        arr = ['region','accesskeyid','accesskeysecret','version','osspath','locale', 'defaultimage','defaulttype','defaultcluster','ssl','god',
               'oss_region','oss_id','oss_key','qsubuser','vpc_cidr_block']
        opt = config.getConfigs(config.COMMON, arr)
        if not opt:
            raise Exception('error')
        for k in arr:
            if opt.get(k):
                v = hide_key(opt[k]) if k=='accesskeysecret' else opt[k]
                print('%s: %s' %(bold(k), green(v)))
    except Exception as e:
        raise Exception('You need to login first')


def hide_key(s):
    if len(s) > 6:
        return "%s******%s" % (s[:3],s[-3:])
    elif len(s) > 1:
        return "%s*****" % s[:1]
    else:
        return "******"