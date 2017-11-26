import logging
from NodeDefender import loggHandler

logger = logging.getLogger(__name__)
logger.setLevel('INFO')
logger.addHandler(loggHandler)

from NodeDefender.icpe import zwave, system, sensor, event
