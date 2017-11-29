"""cw-celerytask-helpers packaging information"""

modname = 'cw_celerytask_helpers'
distname = 'cw-celerytask-helpers'

numversion = (0, 5, 3)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'
description = 'Worker side helpers for cubicweb-celerytask'
web = 'http://www.cubicweb.org/project/%s' % distname

__depends__ = {
    'celery': None,
    'redis': None,
}

classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
]
