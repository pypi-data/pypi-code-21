# -*- coding: utf-8 *-*
import logging
import json
import os
import pwd
import sys

if sys.version_info[0] >= 3:
    from . import config
    from .dynamodb import DynamoHandler
else:
    import config
    from dynamodb import DynamoHandler

logger = logging.getLogger(config.Appl)
logger.setLevel(logging.DEBUG)

handler = DynamoHandler.to(config.Table,
                           config.Region,
                           config.AccessKeyId,
                           config.SecretAccessKey)
logger.addHandler(handler)

def getmeta(meta):
    if meta:
        parts = meta.split(';')
        if len(parts) == 3:
            return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name}), 'Study': parts[0], 'Uid': parts[1], 'Requested': parts[2]}
        else:
            return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name, 'Data': meta})}
    else:
        return {'meta': json.dumps({'Appl': config.Appl, 'User': pwd.getpwuid(os.getuid()).pw_name})}

def info(str, meta=None):
    logger.info(str, extra=getmeta(meta))

def debug(str, meta=None):
    logger.debug(str, extra=getmeta(meta))

def warning(str, meta=None):
    logger.warning(str, extra=getmeta(meta))

def error(str, meta=None):
    logger.error(str, extra=getmeta(meta))