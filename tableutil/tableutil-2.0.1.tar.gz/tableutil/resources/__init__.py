import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

table_style_css = u'{base}{filename}'.format(base=base_dir, filename=u'table_style.css')
