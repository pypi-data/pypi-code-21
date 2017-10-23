# BOT Motion Module
#
# Config
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

#from motor_config import config_maxon_411678 as object_dict
#from motor_config import config_amk_dt4 as object_dict

IF_NAME = 'enx3c18a0099d3c'#'enp0s25'
TCP_PORT = 40001
UDP_PORT = 40002
PORT_PDO = UDP_PORT
PORT_SDO = TCP_PORT

SDO_CONFIG_FILE = 'sdo_config_maxon_411678.csv'

IP_MOTOR1 = '192.168.101.221'
IP_MOTOR2 = '192.168.101.222'
IP_MOTOR3 = '192.168.101.223'
IP_MOTOR4 = '192.168.101.224'

sdo_ip_id = {
    IP_MOTOR1: 0,
    IP_MOTOR2: 1,
    IP_MOTOR3: 2,
    IP_MOTOR4: 3,
}
