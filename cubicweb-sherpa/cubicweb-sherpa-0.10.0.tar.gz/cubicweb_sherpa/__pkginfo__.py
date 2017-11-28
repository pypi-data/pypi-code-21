# pylint: disable=W0622
"""cubicweb-sherpa application packaging information"""

distname = 'cubicweb-sherpa'

numversion = (0, 10, 0)
version = '.'.join(str(num) for num in numversion)

license = 'GPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'SEDA v2 profile generator'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb[pyramid]': '>= 3.25.0, < 3.26.0',
    'six': '>= 1.4.0',
    'cubicweb-seda': '>= 0.12.0, < 0.13.0',
    'cubicweb-registration': None,
    'cubicweb-rememberme': None,
    'cubicweb-relationwidget': None,
    'jinja2': '>= 2.9',
}

__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
