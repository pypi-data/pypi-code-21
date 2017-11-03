import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

ui_persist = u'{base}{filename}'.format(base=base_dir, filename=u'ui_persist.json')
ui_layout = u'{base}{filename}'.format(base=base_dir, filename=u'ui_layout.json')
