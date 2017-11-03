import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

host = u'{base}{filename}'.format(base=base_dir, filename=u'host.json')
intercept = u'{base}{filename}'.format(base=base_dir, filename=u'intercept.json')
proxy = u'{base}{filename}'.format(base=base_dir, filename=u'proxy.json')
redirect = u'{base}{filename}'.format(base=base_dir, filename=u'redirect.json')

