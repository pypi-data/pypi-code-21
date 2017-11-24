#!/usr/bin/env python
import os
import sys
import time
import json
import sge_refresh
from batchcompute_sge.lib import sge_common

SGE_WATCHDOG_WORKING_DIR = '/var/log'
BCCLUSTER_CONFIG_FILE = '/root/.bccluster.json'

def load_config():
    with open(BCCLUSTER_CONFIG_FILE, 'r') as f:
        config = json.load(f)
    if not config.get('access_key_id', '') \
        or not config.get('access_key_secret', '') \
        or not config.get('region', '') \
        or not config.get('master_security_group_id', ''):
        raise Exception('config file(%s) is not ready' % BCCLUSTER_CONFIG_FILE)
    return config

def watch(logger):
    while True:
        try:
            logger.info('watch begin')
            pid = sge_common.get_process_pid(sge_common.SGE_USER, sge_common.SGE_MASTER)
            if not pid:
                logger.warning('not found sge_qmaster. try to start')
                sge_common.start_sge_master()

            config = load_config()
            refresher = sge_refresh.Refresher(config, logger = logger)
            refresher.refresh()

        except Exception, e:
            logger.exception(str(e))
        time.sleep(5)

def main():
    sge_common.daemonize()

    os.chdir(SGE_WATCHDOG_WORKING_DIR)
    logger = sge_common.get_logger('sge_master_watchdog.log')
    logger.warning('sge master watchdog starts. working dir: ' + SGE_WATCHDOG_WORKING_DIR)

    watch(logger)

    logger.warning('sge master watchdog stops')
    sys.exit(0)

if __name__ == '__main__':
    main()

