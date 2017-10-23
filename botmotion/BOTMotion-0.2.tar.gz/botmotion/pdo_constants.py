# BOT Motion Module
#
# PDO Constants
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
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
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

# Operation Modes
OPMODE_NONE   = 0
OPMODE_PP     = 1
OPMODE_VL     = 2
OPMODE_PV     = 3
OPMODE_TQ     = 4
OPMODE_HM     = 6
OPMODE_IP     = 7
OPMODE_CSP    = 8
OPMODE_CSV    = 9
OPMODE_CST    = 10
OPMODE_CSTCA  = 11

# Controlword commands
CMD_SHUTDOWN    = 0x06
CMD_SWITCH_ON   = 0x07
CMD_FAULT_RESET = 0x80
CMD_ENABLE_OP   = 0x0f
CMD_DISABLE_OP  = 0x0e
CMD_QUICK_STOP  = 0x02

# Statusword Bits
READY_TO_SWITCH_ON_STATE            = 0x1
SWITCHED_ON_STATE                   = 0x2
OPERATION_ENABLED_STATE             = 0x4
FAULT_STATE                         = 0x8
FAULT_REACTION_ACTIVE_STATE         = 0xf
VOLTAGE_ENABLED_STATE               = 0x10
QUICK_STOP_STATE                    = 0x20
SWITCH_ON_DISABLED_STATE            = 0x40
WARNING_STATE                       = 0x80
MANUFACTURER_SPECIFIC_STATE         = 0x100
REMOTE_STATE                        = 0x200
TARGET_REACHED_OR_RESERVED_STATE    = 0x400
INTERNAL_LIMIT_ACTIVE_STATE         = 0x800
OPERATION_MODE_SPECIFIC_STATE       = 0x1000
MANUFACTURER_SPECIFIC_STATES        = 0xC000

# Statusword bit for CSP
SW_CSP_FOLLOWING_ERROR              = 0x2000
SW_CSP_TARGET_POSITION_IGNORED      = 0x1000
SW_FAULT_OVER_CURRENT               = 0x4000
SW_FAULT_UNDER_VOLTAGE              = 0x8000
SW_FAULT_OVER_VOLTAGE               = 0xC000
SW_FAULT_OVER_TEMPERATURE           = 0x0100