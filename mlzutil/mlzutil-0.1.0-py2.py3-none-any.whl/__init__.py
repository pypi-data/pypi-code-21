#  -*- coding: utf-8 -*-
# *****************************************************************************
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

import os
import os.path
import logging
import select
import fcntl
from subprocess import Popen, PIPE, CalledProcessError

try:
    import mlzlog
except ImportError:
    mlzlog = None


def system_call(cmd, sh=True, log=None):
    if log is None:
        if mlzlog is not None and mlzlog.log is not None:
            log = mlzlog.log
        else:
            log = logging

    log.debug('System call [sh:%s]: %s' \
              % (sh, cmd))

    out = []
    proc = None
    poller = None
    out_buf = ['']
    err_buf = ['']

    def pollOutput():
        """
        Read, log and store output (if any) from processes pipes.
        """

         # collect fds with new output
        fds = [entry[0] for entry in poller.poll()]

        if proc.stdout.fileno() in fds:
            while True:
                try:
                    tmp = proc.stdout.read(100)

                    if not tmp:
                        break
                except IOError:
                    break
                out_buf[0] += tmp.decode('utf-8')

                while '\n' in out_buf[0]:
                    line, _, out_buf[0] = out_buf[0].partition('\n')
                    log.debug(line)
                    out.append(line + '\n')

                if not tmp:
                    break
        if proc.stderr.fileno() in fds:
            while True:
                try:
                    tmp = proc.stderr.read(100)
                    if not tmp:
                        break
                except IOError:
                    break
                err_buf[0] += tmp.decode('utf-8')

                while '\n' in err_buf[0]:
                    line, _, err_buf[0] = err_buf[0].partition('\n')
                    log.warning(line)

                if not tmp:
                    break


    while True:
        if proc is None:
            # create and start process
            proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=sh)

            # create poll select
            poller = select.poll()

            flags = fcntl.fcntl(proc.stdout, fcntl.F_GETFL)
            fcntl.fcntl(proc.stdout, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            flags = fcntl.fcntl(proc.stderr, fcntl.F_GETFL)
            fcntl.fcntl(proc.stderr, fcntl.F_SETFL, flags| os.O_NONBLOCK)

            # register pipes to polling
            poller.register(proc.stdout, select.POLLIN)
            poller.register(proc.stderr, select.POLLIN)

        pollOutput()

        if proc.poll() is not None: # proc finished
            break

    # poll once after the process ended to collect all the missing output
    pollOutput()

    # check return code
    if proc.returncode != 0:
        raise RuntimeError(
            CalledProcessError(proc.returncode, cmd, ''.join(out))
            )

    return str(''.join(out))


def ensure_directory(dirpath):
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)


def mount(dev, mountpoint, flags='', log=None):
    ensure_directory(mountpoint)
    system_call('mount %s %s %s' % (flags, dev, mountpoint),
               log=log)


def umount(mountpoint, flags='', log=None):
    system_call('umount %s %s' % (flags, mountpoint),
               log=log)
