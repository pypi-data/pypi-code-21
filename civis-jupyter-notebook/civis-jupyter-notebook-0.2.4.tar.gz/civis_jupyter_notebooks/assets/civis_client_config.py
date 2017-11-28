import os
import civis
from civis_jupyter_notebooks.platform_persistence import logger as LOGGER

if 'CIVIS_API_KEY' in os.environ:
    LOGGER.info('creating civis api client')
    client = civis.APIClient(resources='all')
    LOGGER.info('civis api client created')

# clean out the namespace for users
del os
del LOGGER
