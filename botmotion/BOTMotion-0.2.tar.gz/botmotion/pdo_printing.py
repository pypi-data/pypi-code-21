# BOT Motion Module
#
# BOT Motion Module
#
# Author:      Henrik Stroetgen <hstroetgen@synapticon.com> / <support@synapticon.com>
# Date:        2016-11-19
# Location:    Filderstadt, Germany
#
#
#
#       Copyright (c) 2016, Synapticon GmbH
#       All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice, this
#          list of conditions and the following disclaimer.
#       2. Redistributions in binary form must reproduce the above copyright notice,
#          this list of conditions and the following disclaimer in the documentation
#          and/or other materials provided with the distribution.
#       3. Execution of this software or parts of it exclusively takes place on hardware
#          produced by Synapticon GmbH.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#       ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FORx
#       ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#       The views and conclusions contained in the software and documentation are those
#       of the authors and should not be interpreted as representing official policies,
#       either expressed or implied, of the Synapticon GmbH.
#

import curses

class Printing():
    def __init__(self):
        self.__stdscr = None

    def __del__(self):
        self.close()

    def close(self):
        if self.__stdscr:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def init(self):
        self.__stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

    def get_stdscr(self):
        return self.__stdscr

    def decode_status_word(self, status_word):
        if not status_word.ready_to_switch_on and \
                not status_word.switched_on and \
                not status_word.operation_enabled and \
                not status_word.fault and \
                not status_word.switch_on_disabled:
            return 'Not ready to switch on'
        elif not status_word.ready_to_switch_on and \
                not status_word.operation_enabled and \
                not status_word.switched_on and \
                not status_word.fault and \
                    status_word.switch_on_disabled:
            return 'Switch on disabled'
        elif not status_word.switched_on and \
                not status_word.operation_enabled and \
                not status_word.fault and \
                not status_word.switch_on_disabled and \
                    status_word.quick_stop and \
                    status_word.ready_to_switch_on:
            return 'Ready to switch on'
        elif not status_word.operation_enabled and \
              not status_word.switch_on_disabled and \
              not status_word.fault and \
                  status_word.quick_stop and \
                  status_word.ready_to_switch_on and \
                  status_word.switched_on:
            return 'Switched on'
        elif not status_word.fault and \
                not status_word.switch_on_disabled and \
                status_word.ready_to_switch_on and \
                status_word.switched_on and \
                status_word.operation_enabled and \
                status_word.quick_stop:
            return 'Operation enabled'
        elif not status_word.fault and \
             not status_word.switch_on_disabled and \
             not status_word.quick_stop and \
             status_word.ready_to_switch_on and \
             status_word.switched_on and \
             status_word.operation_enabled:
            return 'Quick stop'
        elif not status_word.switch_on_disabled and \
             status_word.ready_to_switch_on and \
             status_word.switched_on and \
             status_word.operation_enabled and \
             status_word.fault:
            return 'Fault reaction active'
        elif not status_word.switch_on_disabled and \
             not status_word.ready_to_switch_on and \
             not status_word.switched_on and \
             not status_word.operation_enabled and \
             status_word.fault:
            return 'Fault'
        elif status_word.fault and \
             status_word.fault_over_current and \
            status_word.fault_under_voltage:
            return 'Fault: Over voltage'
        elif status_word.fault and \
             status_word.fault_over_temperature:
            return 'Fault: Over temperature'
        elif status_word.fault and \
             status_word.fault_over_current:
            return 'Fault: Over current'
        elif status_word.fault and \
            status_word.fault_under_voltage:
            return 'Fault: Under voltage'

        else:
            return 'U shouldn\'t see me'

    def print_pdo(self, pdo_in, pdo_out, index):
        self.__stdscr.addstr(0+index*4, 0, 'Position:   %12d | Velocity:    %8d | Torque:      %8d | Time: %8d'
                      % (pdo_in.position_actual, pdo_in.velocity_actual, pdo_in.torque_actual, pdo_in.timestamp))
        self.__stdscr.addstr(1+index*4, 0, 'Target Pos: %12d | Target Velo: %8d | Target Torq: %8d'
                      % (pdo_out.position_target, pdo_out.velocity_target, pdo_out.torque_target))
        self.__stdscr.addstr(2+index*4, 0, 'Status: %s' % self.decode_status_word(pdo_in.status_word) )
        self.__stdscr.refresh()


