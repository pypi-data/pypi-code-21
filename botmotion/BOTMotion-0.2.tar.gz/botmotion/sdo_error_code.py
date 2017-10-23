# BOT Motion Module
#
# SDO Error Code Constants
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


# abort codes
SDO_ABORT_TOGGLE_BIT            = 0x05030000 # Toggle bit not changed
SDO_ABORT_PROTO_TIMEOUT         = 0x05040000 # SDO protocol timeout
SDO_ABORT_CLIENTSERVER          = 0x05040001 # Client/Server command specifier not valid or unknown
SDO_ABORT_MEMORY                = 0x05040005 # Out of memory
SDO_ABORT_UNSUPPORTED           = 0x06010000 # Unsupported access to an object
SDO_ABORT_READ_WO               = 0x06010001 # Attempt to read to a write only object
SDO_ABORT_WRITE_RO              = 0x06010002 # Attempt to write to a read only object
SDO_ABORT_OBJNOTEXIST           = 0x06020000 # The object does not exist in the object directory
SDO_ABORT_NOPDOMAPPING          = 0x06040041 # The object can not be mapped into the PDO
SDO_ABORT_EXCEED_PDO            = 0x06040042 # The number and length of the objects to be mapped would exceed the PDO length
SDO_ABORT_PARAM_INCOMPATIBLE    = 0x06040043 # General parameter incompatibility reason
SDO_ABORT_INTERNAL_INCOMP       = 0x06040047 # General internal incompatibility in the device
SDO_ABORT_HW_ERROR              = 0x06060000 # Access failed due to a hardware error
SDO_ABORT_TYPE_MISMATCH         = 0x06070010 # Data type does not match, length of service parameter does not match
SDO_ABORT_TYPE_MISMATCH_HI      = 0x06070012 # Data type does not match, length of service parameter too high
SDO_ABORT_TYPE_MISMATCH_LO      = 0x06070013 # Data type does not match, length of service parameter too low
SDO_ABORT_NO_SUBINDEX           = 0x06090011 # Subindex does not exist
SDO_ABORT_RANGE_EXCEED          = 0x06090030 # Value range of parameter exceeded (only for write access)
SDO_ABORT_VALUE_WRHIGH          = 0x06090031 # Value of parameter written too high
SDO_ABORT_VALUE_WRLOW           = 0x06090032 # Value of parameter written too low
SDO_ABORT_MINMAX                = 0x06090036 # Maximum value is less than minimum value
SDO_ABORT_ERROR                 = 0x08000000 # General error
SDO_ABORT_NOTRANS               = 0x08000020 # Data cannot be transferred or stored to the application
SDO_ABORT_NOTRANS_LOCAL         = 0x08000021 # Data cannot be transferred or stored to the application because of local control
SDO_ABORT_NOTRANS_STATE         = 0x08000022 # Data cannot be transferred or stored to the application because of the present device state
SDO_ABORT_NO_OBJECT_DICT        = 0x08000023 # Object dictionary dynamic generation fails or no object dictionary is present

sdo_error_dict = {
    SDO_ABORT_TOGGLE_BIT:           'Toggle bit not changed',
    SDO_ABORT_PROTO_TIMEOUT:        'SDO protocol timeout',
    SDO_ABORT_CLIENTSERVER:         'Client/Server command specifier not valid or unknown',
    SDO_ABORT_MEMORY:               'Out of memory',
    SDO_ABORT_UNSUPPORTED:          'Unsupported access to an object',
    SDO_ABORT_READ_WO:              'Attempt to read to a write only object',
    SDO_ABORT_WRITE_RO:             'Attempt to write to a read only object',
    SDO_ABORT_OBJNOTEXIST:          'The object does not exist in the object directory',
    SDO_ABORT_NOPDOMAPPING:         'The object can not be mapped into the PDO',
    SDO_ABORT_EXCEED_PDO:           'The number and length of the objects to be mapped would exceed the PDO length',
    SDO_ABORT_PARAM_INCOMPATIBLE:   'General parameter incompatibility reason',
    SDO_ABORT_INTERNAL_INCOMP:      'General internal incompatibility in the device',
    SDO_ABORT_HW_ERROR:             'Access failed due to a hardware error',
    SDO_ABORT_TYPE_MISMATCH:        'Data type does not match, length of service parameter does not match',
    SDO_ABORT_TYPE_MISMATCH_HI:     'Data type does not match, length of service parameter too high',
    SDO_ABORT_TYPE_MISMATCH_LO:     'Data type does not match, length of service parameter too low',
    SDO_ABORT_NO_SUBINDEX:          'Subindex does not exist',
    SDO_ABORT_RANGE_EXCEED:         'Value range of parameter exceeded (only for write access)',
    SDO_ABORT_VALUE_WRHIGH:         'Value of parameter written too high',
    SDO_ABORT_VALUE_WRLOW:          'Value of parameter written too low',
    SDO_ABORT_MINMAX:               'Maximum value is less than minimum value',
    SDO_ABORT_ERROR:                'General error',
    SDO_ABORT_NOTRANS:              'Data cannot be transferred or stored to the application',
    SDO_ABORT_NOTRANS_LOCAL:        'Data cannot be transferred or stored to the application because of local control',
    SDO_ABORT_NOTRANS_STATE:        'Data cannot be transferred or stored to the application because of the present device state',
    SDO_ABORT_NO_OBJECT_DICT:       'Object dictionary dynamic generation fails or no object dictionary is present',
}