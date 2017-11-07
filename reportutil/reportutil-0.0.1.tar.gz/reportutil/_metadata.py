
# Variables for setup (these must be string only!)
__module_name__ = u'reportutil'
__description__ = u'Module to assist in the creation of reports.'

__version__ = u'0.0.1'

__author__ = u'Oli Davis'
__authorshort__ = u'OWBD'
__authoremail__ = u'oli.davis@me.com'

__license__ = u'MIT'

__githost__ = 'bitbucket.org'
__gituser__ = u'davisowb'
__gitrepo__ = u'reportutil.git'


# Additional variables
__copyright__ = u'Copyright (C) 2016 {author}'.format(author=__author__)

__url__ = u'https://{host}/{user}/{repo}'.format(host=__githost__,
                                                 user=__gituser__,
                                                 repo=__gitrepo__)
__downloadurl__ = u'{url}/get/{version}.tar'.format(url=__url__,
                                                    host=__githost__,
                                                    user=__gituser__,
                                                    repo=__gitrepo__,
                                                    version=__version__)
