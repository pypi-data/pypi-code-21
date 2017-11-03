import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

handler = u'{base}{filename}'.format(base=base_dir, filename=u'handler.json')
scenario = u'{base}{filename}'.format(base=base_dir, filename=u'scenario.json')
