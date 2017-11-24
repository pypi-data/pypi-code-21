#!/usr/bin/env python
import os
import sys
import time
from batchcompute_sge.lib import sge_common

def restart_sge_worker(logger, retry_count = 10):
    for i in range(retry_count + 1):
        try:
            sge_common.kill_process(
                    sge_common.SGE_USER, 
                    sge_common.SGE_MASTER, 
                    retry_count = 10, 
                    logger = logger)
            sge_common.kill_process(
                    sge_common.SGE_USER, 
                    sge_common.SGE_EXECD, 
                    retry_count = 10, 
                    logger = logger)
            sge_common.start_sge_execd()
            return
        except Exception, e:
            logger.exception(str(e))
            if i == retry_count:
                raise e
            time.sleep(1)

def main():
    logger = sge_common.get_logger('sge_bootstrap.log')
    try:
        master_ip_address = os.environ['SGE_MASTER_IP_ADDRESS']
        master_host_name = os.environ['SGE_MASTER_HOST_NAME']

        logger.warning('sge bootstrap starts. master_ip_address: %s, master_host_name: %s' % (master_ip_address, master_host_name))

        pid = sge_common.get_process_pid('root', 'sge_execd_watchdogd')
        if pid != 0:
            logger.warning('sge_execd_watchdogd has been already started. pid: %d' % pid)
        else:
            sge_common.set_etc_hosts(master_ip_address, master_host_name)
            sge_common.set_act_qmaster(sge_common.SGE_ROOT, sge_common.SGE_CELL_NAME, master_host_name)
            restart_sge_worker(logger)
            sge_common.run_cmd('/usr/local/bin/sge_execd_watchdogd')

        logger.warning('sge bootstrap stops.')
        sys.exit(0)
    except Exception, e:
        logger.exception(str(e))
        logger.warning('sge bootstrap stops.')
        sys.exit(1)

if __name__ == '__main__':
    main()

