# -*- coding: utf-8 -*-

import codecs
from warnings import warn
from .resources import table_style_css
from fdutil.resources import open_document_snippet

# Useful CSS
with open(table_style_css, 'rb') as fp:
    TABLE_CSS = u'{css}'.format(css=fp.read())

# Useful JS
with open(open_document_snippet, 'rb') as fp:
    OPEN_DOCUMENT_JS = u'{js}'.format(js=fp.read())


# TODO: The below is deprecated!
HEAD = (u'<!doctype html>\n'
        u'<html lang="en-GB">\n'
        u'<head>\n'
        u'<meta charset="UTF-8">\n'
        u'<style>{{css}}<style/>\n'
        + u'<script>'
        + OPEN_DOCUMENT_JS
        + u'<script/>\n'
        + u'</head>\n')


def open(fname,
         css=TABLE_CSS):
    warn(u'tableutil.tablehtml.open() is deprecated please migrate to using fdutil.html',
         category=DeprecationWarning)

    f = codecs.open(fname,
                    u'w',
                    encoding=u'utf8')
    f.write(HEAD.replace(u'{{css}}', css))
    f.write(u'<body>\n')
    return f


def close(f):
    warn(u'tableutil.tablehtml.close() is deprecated please migrate to using fdutil.html',
         category=DeprecationWarning)

    f.write(u'</body>\n'
            u'</html>')
    f.close()
