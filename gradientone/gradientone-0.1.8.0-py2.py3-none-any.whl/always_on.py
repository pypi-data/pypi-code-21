"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import os
from updater import UpdateController
from controllers import kill_proc_tree
from gateway_helpers import clear_pid_list


def run():
    pid = str(os.getpid())
    pidfile = "/tmp/mydaemon.pid"

    f = open(pidfile, 'w')
    f.write(pid)
    f.close()

    # clean up any old client processes, except this one
    kill_proc_tree(exc_pid=pid)
    # clear the pid list to start over
    clear_pid_list()

    ctrl = UpdateController()
    try:
        ctrl.start_checking()
    finally:
        ctrl.terminate()
        os.unlink(pidfile)


if __name__ == "__main__":
    run()


# cron job that logs status and restarts if failed
# * * * * * ps up `cat /tmp/mydaemon.pid ` >/dev/null && echo "Working at: $(date)" >> /tmp/debug.log || echo "Restart at: $(date)" >> /tmp/debug.log || echo "Failed Restart at: $(date)" >> /tmp/debug.log  # noqa
# * * * * * ps up `cat /tmp/mydaemon.pid ` >/dev/null || /usr/local/bin/python [REPLACE WITH PATH TO THIS FILE] 2> /tmp/err.log  # noqa
# 0 0 */3 * * > /tmp/debug.lo
