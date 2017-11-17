#!/bin/env python
###################################################################
# connection_example.py : A test script example which includes:
#     common_seup section - device connection, configuration
#     Tescase section with testcase setup and teardown (cleanup)
#     common_cleanup section - device cleanup
# The purpose of this sample test script is to show how to connect the 
# devices/UUT in the common setup section. How to run few simple testcases
# And finally, recover the test units in
# the common cleanup section. Script also provides an example on how to invoke
# TCL interpreter to call existing TCL functionalities.
###################################################################

from ats import tcl
from ats import aetest
from ats.log.utils import banner
from ats.async import pcall

import re
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def check_mgmtInterface_status(device):
    """ function checks device mgmt interface status """
    output  = device.execute('show interface br')
    found_match = 0
    for line in output.split('\r\n'):
        matchObj = re.search('^mgmt[0-9]+ .* (up|down) .*', line)
        if matchObj:
            found_match = 1
            if matchObj.group(1) == "up":
                log.info ("Mgmt interface is up and running")
                return 1
            else:
                log.warning ("Mgmt interface is down")
                return 0
    if not found_match:
        log.warning ("Can not find MGMT interface")
        return 0

def get_mgmtInterface_Rx_packets(device):
    """ function returns the num of packets device mgmt interface received  """
    output  = device.execute('show interface mgmt 0')
    found_match = 0
    for line in output.split('\r\n'):
        matchObj = re.search('([0-9]+) input packets .* packets', line)
        if matchObj:
            found_match = 1
            Rx = matchObj.group(1)
            log.info ("Got Mgmt interface Rx packets: %s" % (Rx))
            return int(Rx)
    if not found_match:
        log.warning ("Can not find MGMT interface Rx packets")
        return -1

def get_terminal_width(device):
    """ function returns device terminal width """
    output  = device.execute('show terminal')
    found_match = 0
    for line in output.split('\r\n'):
        matchObj = re.search('Length: [0-9]+ lines, Width: ([0-9]+) columns', 
                             line)
        if matchObj:
            found_match = 1
            width = matchObj.group(1)
            log.info ("Got terminal width: %s" % (width))
            return width
    if not found_match:
        log.warning ("Can not get terminal config info")
        return -1

###################################################################
###                  COMMON SETUP SECTION                       ###
###################################################################

# Configure and setup all devices and test equipment in this section.
# This should represent the BASE CONFIGURATION that is applicable
# for the bunch of test cases that would follow.

class common_setup(aetest.CommonSetup):
    """ Common Setup for Sample Test """

    @aetest.subsection
    def connect(self, testscript, testbed, uut_name, stdby_name):
        """ common setup subsection: connecting devices """
        
        # Grab the device object of the uut device with that name
        uut = testbed.devices[uut_name]

        # Save it in testscript parmaeters to be able to use it from other
        # test sections
        testscript.parameters['uut'] = uut       

        # Connect to the device
        uut.connect()

        # Make sure that the connection went fine
        if not hasattr(uut, 'execute'):
            self.failed()

        if uut.execute != uut.connectionmgr.default.execute:
            self.failed()

    @aetest.subsection
    def show_exec(self, uut):
        """ common setup subsection: exec show command """
       
        log.info ("show clock")
        # Sending show clock to the device as an execute cmd
        output = uut.execute('show version')
        # Make sure the output is not none
        if output is not None:
            log.info ("The outputs is: %s" % (output))
        else:
            self.failed()
        
    @aetest.subsection
    def healthcheck(self, uut):
        """ common setup subsection: health checking """

        check_result = check_mgmtInterface_status(uut)

        if check_result:
            log.info("Device Health Check Passed")
        else:
            log.info("Device Health Check Failed")
            self.failed()

#######################################################################
###                          TESTCASE BLOCK                         ###
#######################################################################
#
# Place your code that implements the test steps for the test case. 
# Each test may or may not contains sections: 
#           setup   - test preparation
#           test    - test action
#           cleanup - test wrap-up

class PcallTestcase(aetest.Testcase):

    @staticmethod
    def pcalled_function(uut):
        return uut.execute('show running-config')

    @aetest.test
    def test_pcall(self, uut):
        # do a pcall
        res = pcall(self.pcalled_function, uut = [uut,])

        log.info('Pcall returned:')
        log.info(str(res))

class tc_one(aetest.Testcase):
    """This is description for my testcase one"""
    @aetest.setup
    def tc_one_setup(self):
        """ test setup """
        log.info("Pass testcase setup")

    @aetest.test
    def myParser(self, uut):
        """ Router show example"""
        tcl.eval('package require router_show')
        result = tcl.eval('router_show -device %s '
                          '-cmd "show ipv6 route summary"' % \
                           (uut.handle,))

        python_result = tcl.cast_keyed_list(result)

        log.info(python_result['bgp'])

    @aetest.test
    def config_line_vty(self, uut, testscript):
        """test action: Config line vty"""

        # config device line vty
        # list containing configuration to send to the device
        configs = '''line vty
                  exec-timeout 0'''

        log.info("Configuring the device: line vty")

        try:
            uut.configure(configs)
        except :
            import sys
            log.error('Invalid CLI given: %s' % (configs,))
            log.error('Error with cli')
            log.error(sys.exc_info())

        # Tcl functionality invoked here as an example
        tcl_res = tcl.eval('set x 5')
        log.info ("TCL eval result: %s" % tcl_res)
        
        # config terminal width
        log.info ("Configuring the device: terminal width")
        width = get_terminal_width(uut)
        if width == -1:
            log.warning("Can not get terminal width, common setup failed")
            self.failed()
        else:
            testscript.parameters['original_term_width'] = width
            if not width == '511':
                log.info ("execute cli: terminal width 511")
                uut.execute('terminal width 511')

    @aetest.cleanup
    def do_some_cleaning(self):
        """ testcase clean up """
        log.info("Testcase cleanup")


########################################################################
####                       COMMON CLEANUP SECTION                    ###
########################################################################
#
## Remove the BASE CONFIGURATION that was applied earlier in the 
## common cleanup section, clean the left over

class common_cleanup(aetest.CommonCleanup):
    """ Common Cleanup for Sample Test """

    @aetest.subsection
    def restore_terminal_width(self, uut, original_term_width):
        """ Common Cleanup subsection """
        log.info(banner("script common cleanup starts here"))
        
        new_width = get_terminal_width(uut)
        if new_width == -1:
            log.warning("Can not get terminal width, common cleanup failed")
            
            # A failure in common_cleanup section will be reported by ATS
            # as part of test automation result.
            self.failed()
        else:
            log.info("New terminal width: %s" % (new_width))

        if not new_width == original_term_width:
            log.info ("recover original terminal width")
            log.info ("execute cli: terminal width %s" %
                      (original_term_width))
            uut.execute('terminal width %s' % original_term_width)
        
        log.info ("terminal width successfully recovered!")

if __name__ == '__main__': # pragma: no cover
    aetest.main()
