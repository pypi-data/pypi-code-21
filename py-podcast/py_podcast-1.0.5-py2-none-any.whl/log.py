import sys
import logging
from podcasts.constants import *

# Logger to use everywhere
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(LOGGER)
