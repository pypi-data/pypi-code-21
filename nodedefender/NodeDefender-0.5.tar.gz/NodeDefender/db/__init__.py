import logging
import NodeDefender.db.sql
import NodeDefender.db.redis
from NodeDefender import loggHandler

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(loggHandler)

def load():
    mqtt.load()
    icpe.load()
    sensor.load()
    field.load()

import NodeDefender.db.data
import NodeDefender.db.group
import NodeDefender.db.user
import NodeDefender.db.message
import NodeDefender.db.node
import NodeDefender.db.icpe
import NodeDefender.db.sensor
import NodeDefender.db.commandclass
import NodeDefender.db.field
import NodeDefender.db.mqtt
logger.info("Database initialized")
