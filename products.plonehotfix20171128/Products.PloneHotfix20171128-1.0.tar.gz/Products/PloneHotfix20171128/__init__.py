import logging

logger = logging.getLogger('Products.PloneHotfix20171128')

# First import any current CMFPlone patches.
try:
    from Products.CMFPlone import patches  # noqa
except:
    pass

# General hotfixes for all.
hotfixes = [
    'in_portal',
    'redirect',
    'user_home_page',
]

try:
    str.format
    unicode.format
except AttributeError:
    # Python 2.4 has no format method so it needs no fix.
    # It is also vastly outdated and no longer supportable by us.
    le = logger.error
    le('*****************************************************')
    le('** You are using unsupported and outdated versions **')
    le('** of Python and Plone. YOU NEED TO UPDATE SOON.   **')
    le('*****************************************************')
else:
    hotfixes.append('strformat')

# Apply the fixes
for hotfix in hotfixes:
    try:
        __import__('Products.PloneHotfix20171128.%s' % hotfix)
        logger.info('Applied %s patch' % hotfix)
    except:
        logger.warn('Could not apply %s' % hotfix)
if not hotfixes:
    logger.info('No hotfixes were needed.')
else:
    logger.info('Hotfix installed')
