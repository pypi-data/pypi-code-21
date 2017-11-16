#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2014  Michael D. M. Dryden -
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import, print_function, unicode_literals

from ..dstat import state

import logging

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GObject
except ImportError:
    print("ERR: GTK not available")
    sys.exit(1)

logger = logging.getLogger(__name__)


class BaseLoop(GObject.GObject):
    __gsignals__ = {
        b'experiment_done': (GObject.SIGNAL_RUN_FIRST, None, tuple()),
        b'progress_update': (GObject.SIGNAL_RUN_FIRST, None, (float,))
    }

    def __init__(self, experiment):
        GObject.GObject.__init__(self)
        self.line = None
        self.lastdataline = 0
        self.current_exp = experiment
        self.experiment_proc = None

    def run(self):
        self.experiment_proc = (
            GObject.idle_add(self.experiment_running_data),
            GObject.idle_add(self.experiment_running_proc),
            GObject.timeout_add(100, self.update_progress)
        )

    def experiment_running_data(self):
        """Receive data from experiment process and add to
        current_exp.data['data].
        Run in GTK main loop.

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """
        try:
            incoming = state.ser.get_data()
            while incoming is not None:
                try:
                    self.line, data = incoming
                    if self.line > self.lastdataline:
                        newline = True
                        try:
                            logger.info("running scan_process()")
                            self.current_exp.scan_process(self.lastdataline)
                        except AttributeError:
                            pass
                        self.lastdataline = self.line
                    else:
                        newline = False
                    self.current_exp.store_data(incoming, newline)
                except TypeError:
                    pass
                incoming = state.ser.get_data()
            return True

        except EOFError as err:
            logger.error(err)
            self.experiment_done()
            return False
        except IOError as err:
            logger.error(err)
            self.experiment_done()
            return False

    def experiment_running_proc(self):
        """Receive proc signals from experiment process.
        Run in GTK main loop.

        Returns:
        True -- when experiment is continuing to keep function in GTK's queue.
        False -- when experiment process signals EOFError or IOError to remove
            function from GTK's queue.
        """
        try:
            proc_buffer = state.ser.get_proc()
            if proc_buffer is not None:
                if proc_buffer in ["DONE", "SERIAL_ERROR", "ABORT"]:
                    self.experiment_done()
                    if proc_buffer == "SERIAL_ERROR":
                        self.on_serial_disconnect_clicked()

                else:
                    logger.warning("Unrecognized experiment return code: %s",
                                   proc_buffer)
                return False
            return True

        except EOFError as err:
            logger.warning("EOFError: %s", err)
            self.experiment_done()
            return False
        except IOError as err:
            logger.warning("IOError: %s", err)
            self.experiment_done()
            return False

    def experiment_done(self):
        logger.info("Experiment done")
        self.current_exp.experiment_done()
        for proc in self.experiment_proc:
            GObject.source_remove(proc)
        self.emit("experiment_done")

    def update_progress(self):
        progress = self.current_exp.get_progress()
        self.emit("progress_update", progress)
        return True
