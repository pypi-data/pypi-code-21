# Journaling
import logging
from systemd.journal import JournalHandler

# Config
from .config import load_config

mon_config = load_config()

# Logging
log = logging.getLogger(mon_config.MONITOR_SYSTEMD)
log.addHandler(logging.StreamHandler())
log.addHandler(JournalHandler(SYSLOG_IDENTIFIER=mon_config.MONITOR_SYSTEMD))
log.setLevel(logging.DEBUG if mon_config.DEBUG else logging.INFO)


