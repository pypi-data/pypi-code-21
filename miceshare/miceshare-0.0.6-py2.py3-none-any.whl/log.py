# coding:utf8
import logging
import logging.handlers

log = logging.getLogger('miceshare')
log.setLevel(logging.DEBUG)
log.propagate = False

fmt = logging.Formatter('%(asctime)s [%(levelname)s] %(filename)s %(lineno)s: %(message)s')
# ch = logging.StreamHandler()
# ch.setFormatter(fmt)
# log.handlers.append(ch)


LOG_FILE = 'logs/info.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes = 1024*1024*10, backupCount=10)

handler.setFormatter(fmt)
log.addHandler(handler)
log.setLevel(logging.DEBUG)
