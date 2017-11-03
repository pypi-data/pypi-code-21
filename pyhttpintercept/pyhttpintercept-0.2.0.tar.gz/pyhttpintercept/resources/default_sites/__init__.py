import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

default_index = u'{base}{filename}'.format(base=base_dir, filename=u'index.html')
example_site = u'{base}{filename}'.format(base=base_dir, filename=u'example')
