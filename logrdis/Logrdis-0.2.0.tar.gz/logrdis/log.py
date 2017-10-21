import logging
import re

LOGGER = logging.getLogger(__name__)

def find_match(log_line, cfg):
    """Receives a log line and finds a match using the cfg object.

    :param log_line: str. a log line to match
    :param cfg: dict. a parsed YAML configuration directive
    :returns: tuple. (tablename for match, re.Match. a match object or None)
    :raises: KeyError
    """
    match = None
    tablename = None
    if 'ingest' not in cfg:
        raise KeyError('ingest key not found in configuration')
    if 'process' not in cfg:
        raise KeyError('process key not found in configuration')

    for tablekey, ingest_regex in cfg.get('ingest', list()).items():
        match = re.search(ingest_regex, log_line)
        if match:
            if tablekey not in cfg.get('process').keys():
                raise KeyError('{} not found in configuration process dict'.format(tablekey))
            tablename = cfg.get('process', {}).get(tablekey, {}).get('tablename', None)
            LOGGER.debug('Match for {}'.format(ingest_regex))
            break

    return (tablename, match)