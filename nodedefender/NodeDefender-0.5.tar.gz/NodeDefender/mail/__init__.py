from flask_mail import Mail
import logging
import NodeDefender

mail = Mail(NodeDefender.app)

logger = logging.getLogger(__name__)
logger.setLevel("INFO")
logger.addHandler(NodeDefender.loggHandler)

enabled = NodeDefender.config.mail.enabled()

import NodeDefender.mail.decorators
import NodeDefender.mail.user
import NodeDefender.mail.group
import NodeDefender.mail.node
import NodeDefender.mail.icpe

if enabled:
    logger.info("Mail initialized")
else:
    logger.info("Mail not enabled")
