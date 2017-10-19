# pylint: disable=W0622
"""cubicweb-seda application packaging information"""

modname = 'seda'
distname = 'cubicweb-seda'

numversion = (0, 11, 5)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Data Exchange Standard for Archival'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'cubicweb': '>= 3.25.3, < 3.26',
    'six': '>= 1.4.0',
    'cubicweb-eac': None,
    'cubicweb-skos': '>= 0.12.1',
    'cubicweb-compound': '>= 0.6',
    'cubicweb-relationwidget': '>= 0.4',
    'cubicweb-squareui': None,
    'pyxst': '>= 0.2',
    'rdflib': '>= 4.1',
}
__recommends__ = {}

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
]
