import os

base_dir = u'{dir}{sep}'.format(dir=os.path.dirname(os.path.realpath(__file__)),
                                sep=os.sep)

# JS
open_document_snippet = u'{base}{filename}'.format(base=base_dir, filename=u'open_document_snippet.js')
enable_tooltip_snippet = u'{base}{filename}'.format(base=base_dir, filename=u'enable_tooltip_snippet.js')
clickable_popover = u'{base}{filename}'.format(base=base_dir, filename=u'clickable_popover.js')
