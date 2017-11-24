#!/usr/bin/env python
import os
import sys
import time
import signal
from batchcompute_sge.lib import sge_common

SGE_WATCHDOG_WORKING_DIR = '/var/log'


def watch(logger):
    while True:
        try:
            pid = sge_common.get_process_pid(sge_common.SGE_USER, sge_common.SGE_EXECD)
            if not pid:
                logger.warning('not found sge_execd. try to start')
                sge_common.start_sge_execd()
        except Exception, e:
            logger.exception(str(e))
        time.sleep(5)

def main():
    sge_common.daemonize()

    os.chdir(SGE_WATCHDOG_WORKING_DIR)
    logger = sge_common.get_logger('sge_execd_watchdog.log')
    logger.warning('sge execd watchdog starts. working dir: ' + SGE_WATCHDOG_WORKING_DIR)

    watch(logger)

    logger.warning('sge execd watchdog stops')
    sys.exit(0)

if __name__ == '__main__':
    main()

