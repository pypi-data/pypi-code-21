# ****************       BEGIN-STANDARD-COPYRIGHT      ***************
#
# Copyright (c) 2017, Spirent Communications.
#
# All rights reserved. Proprietary and confidential information of Spirent Communications.
#
#  ***************        END-STANDARD-COPYRIGHT       ***************

"""Builtin sessions provider."""

from .session_profile import SessionProfile

class BuiltinSession(object):
    """Provide an access to builtin sessions"""

    def __init__(self, protocol_socket, agent_type):
        self._protosock = protocol_socket
        self._agent_type = agent_type

    @property
    def rft(self):
        """Return session profile obj with URI=application://com.fanfare.itest.appstore.applications.rft

           The session window for iTest RFT sessions has been designed in partnership with IBM to enable you to launch Rational
           Functional Tester scripts from iTest. This integration is certified by IBM as Ready for IBM Rational Software.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fanfare.itest.appstore.applications.rft')

    @property
    def cmd(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.cmd

           You can run Microsoft Windows Command Prompt sessions (that is, run cmd terminal sessions). For each open session,
           the Command Prompt Session window displays your commands and the local PC's responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.cmd')

    @property
    def chat(self):
        """Return session profile obj with URI=application://com.fnfr.bobcat.tools.chat

           You can add steps that receive and send XMPP chat messages during execution. A test case can send and
           receive as many messages as are needed. Message text can contain both fixed text and response data
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.bobcat.tools.chat')

    @property
    def serial(self):
        """Return session profile obj with URI=application://com.fnfr.itest.application.serial

          For Serial Port sessions, the computer running iTest communicates directly over a serial port connection with the device
          under test. For each open session, the Serial Port session window displays your commands and the device's responses. You
          can think of the session window as a terminal client - a terminal that iTest is monitoring and capturing.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.application.serial')

    @property
    def tool(self):
        """Return session profile obj with URI=application://com.fnfr.itest.application.sf.tool """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.application.sf.tool')

    @property
    def file(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.file

           The File session type enables an automated test case to work with text files during execution (open a
           file, go to a specified position in the file, read a line, write a line, and so on).
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.file')

    @property
    def landslide(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.landslide
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.landslide')

    @property
    def ranorex(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.ranorex

           Ranorex Test session provides ways of automating the Windows, Web, and Mobile UI applications. The seamless
           testing of these iTest functionalities is achieved by iTest integration with Ranorex application (www.ranorex.com).
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.ranorex')

    @property
    def selenium(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.selenium

           For Selenium sessions, iTest opens an instance of the Firefox browser. You interact with the pages in the normal
           way while iTest captures your actions and responses from the session.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.selenium')

    @property
    def netconf(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.spirent.netconf.tool

           The NetConf session window displays your commands and the device's responses. You can think of the session window
           as aterminal - a terminal to a NetConf service as a subsystem that iTest is monitoring and capturing.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.spirent.netconf.tool')

    @property
    def posapp(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.spirent.posapp.tool """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.spirent.posapp.tool')

    @property
    def udp(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.udp.tool

        For UDP sessions, the computer running iTest communicates directly over UDP (User Datagram Protocol) with the specified device.
        For each open session, the UDP session window displays your commands and the local echo. Open another session to view the device's
        response. You can think of the window as a terminal client - a terminal that iTest is monitoring and capturing.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.udp.tool')

    @property
    def vmware_core(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.vmware.vi.core.tool """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.vmware.vi.core.tool')

    @property
    def vmware_vscphere(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.vmware.vsphere.core.too """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.vmware.vsphere.core.tool')

    @property
    def vnc(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.vnc

           iTest VNC sessions are intended to help you to control a remote OS to perform configuration/setup/tear-down tasks. iTest
           VNC sessions are not intended to enable you to thoroughly test an application on a remote platform.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.vnc')

    @property
    def webservices(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.webservices

           The Web Services session window provides a work surface for composing and submitting Web Service requests.
           Any request that you submit in the iTest session is forwarded to the Web Services server.
           The Web Service performs the action and returns its normal response.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.webservices')

    @property
    def rest(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.webservices.restful

        The REST session window provides a work surface for composing and submitting HTTP requests. Any request that
        you submit in the iTest session is forwarded to the RESTful service. The service performs the action and returns
        its normal response. iTest captures all of the actions that you perform in a session and all of the responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.webservices.restful')

    @property
    def xmlrpc(self):
        """Return session profile obj with URI=application://com.fnfr.itest.applications.webservices.xmlrpc

          The XML-RPC session window provides a work surface for composing and submitting XML-RPC method calls over HTTP and HTTPS.
          Any request that you submit in the iTest session is forwarded to the XML-RPC service. The service performs the action and
          returns a response. You can view the response in the Response section of the XML-RPC session window. iTest captures all of
          the actions that you perform in a session and all of the responses. You can use the captured items to create test case
          steps that interact with the XML-RPC server.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.applications.webservices.xmlrpc')

    @property
    def database(self):
        """Return session profile obj with URI=application://com.fnfr.itest.tools.database

          The Database Client session window is an interactive browser where you perform database operations and monitor responses.
          iTest captures all commands and responses and you an save captured items as test case steps that start the session and
          set and request database records. Automated test cases open the same session window to perform database operations.
          iTest supports sessions with MySQL, SqlServer, Oracle, Szlite, Derby, or a custom database type that you specify.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.tools.database')

    @property
    def flex(self):
        """Return session profile obj with URI=application://com.fnfr.itest.tools.flex

           iTest supports testing Flash applications that were developed using Adobe Flex.
           iTest can capture your interactions with Flex applications that are hosted on web pages.
           iTest captures each step of an interactive (manual) test in the Flex application.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.tools.flex')

    @property
    def windowsgui(self):
        """Return session profile obj with URI=application://com.fnfr.itest.tools.windowsgui """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.itest.tools.windowsgui')

  #  @property
  #  def testtool(self):
  #     """Return session profile obj with URI=application://com.fnfr.itest.applications.webservices.xmlrpc """
  #      return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.open.automation.tool.testtool')

    @property
    def agilent(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.agilent """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.agilent')

    @property
    def http(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.http

           Using an HTTP session, a test case can talk directly with a device using the HTTP protocol operations GET and POST.
           HTTP GET commands are useful in cases where you are not testing a Web application, but rather are testing something
           like a device through which the HTTP is passing.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.http')

    @property
    def ixia_ixload(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.ixia.ixload

        To run an IxLoad session in iTest, you first define a test or tests in IxLoad and save the configuration file (RFX file)
        as you normally would. You then start the IxLoad session in iTest and run the IxLoad test. When the session starts, it checks
        out the libraries and connects and runs the initialization script and then loads the configuration, validates it, and transforms
        it (see the description for the iTest load command). The test produces responses and CSV files, which you can then post-process.
        The IxLoad session window is an interactive terminal where you enter commands to perform IxLoad actions on the device. IxLoad returns
        text responses. The responses to IxLoad responses are structured and iTest uses built-in mappers to supply read-made queries.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.ixia.ixload')

    @property
    def ixia_ixnetwork(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.ixia.ixnetwork

        In IxNetwork sessions, you can start and stop traffic, start and stop capture, and review statistics.
        The levels of the Object Data Matrix are represented as subdirectories (see Table 1-11, API Command Data
        ModelStructure in the IxNetwork Tcl API Guide). The iTest IxNetwork session window enables you to navigate
        the object hierarchy by using commands that you typically use to navigate a file system.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.ixia.ixnetwork')

    @property
    def ixiaTraffic(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.ixiaTraffic

        The Ixia Traffic session window is an interactive terminal where you enter commands to perform Ixia Traffic actions
        on the device. The session on the Ixia device returns text responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.ixiaTraffic')

 #   @property
 #    def swing(self):
 #       """Return session profile obj with URI=application://com.fnfr.svt.applications.java.swing
 #
 #      The Swing session type allows you to test Java applications with user interfaces that were developed using Swing.
 #      """
 #       return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.java.swing')

    @property
    def mail(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.mail

           You can add steps that construct and send email messages during execution. A test case can construct and send as
           many email messages as are needed. The message body can contain both fixed text and test response and result data.
           """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.mail')

    @property
    def process(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.process

           Execute and manage processes on the computer that is running iTest.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.process')

    @property
    def python(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.python

          iTest Python session is a terminal session, similar to Tcl Shell. The session uses native Python interpreter
          to getting responses. Supported versions of interpreters are: 2.4-2.7 and 3.0-3.6. iTest support an internal
          Python interpreter and also allows you to point to an external interpreter via Preferences settings.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.python')

    @property
    def smartbits(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.smartbits

           The SmartBits session window is an interactive terminal where you enter commands to perform
           SmartBits actions on the device. SmartBits returns text responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.smartbits')

    @property
    def snmp(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.snmp

           A hierarchical browser for getting and setting SNMP MIB data using the Simple Network Management Protocol
           (SNMP V1, V2c, or V3) defined in RFC 1157
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.snmp')

    @property
    def avalanche(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.spirent.avalanche

           There are several options for running an Avalanche test in iTest:
			* Running a test using the Tcl scripts generated by Avalanche
			* Running an Avalanche test on a TestCenter device
			* Running a test using Demo mode
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.spirent.avalanche')

    @property
    def testcenter_gui(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.spirent.testcenter.gui """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.spirent.testcenter.gui')

    @property
    def spirenttestcenter(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.spirenttestcenter

           iTest integrates with Spirent TestCenter (STC) and provides REST API to ensure that the automation functionality is readily available
           to a wide variety of clients using both script and GUI. This integration also eliminates the requirement of an STC installation on the
           client system. This allows you to use existing tools available to create STC automation clients that can run on any platform.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.spirenttestcenter')

    @property
    def ssh(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.ssh

           A virtual terminal that communicates with a device using the SSH protocol (SSH-1 or SSH-2) defined in RFC 4250
           Note: Because Linux and Unix devices typically include Telnet and SSH servers, you can start a Telnet or SSH session
           to "localhost" to access a shell.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.ssh')

    @property
    def syslog(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.syslog

           Each Syslog session monitors the syslog messages that arrive at the built-in iTest syslog server (visible in the Syslog view).
           While the syslog server receives all messages, any syslog session can filter the messages based on the following property settings
           in the session profile.
           As a result of configuring session profile settings, only the messages that meet the filter settings appear in the session window.
           This enables your test cases to analyze the particular responses (messages) of interest and to ignore irrelevant messages.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.syslog')

    @property
    def tclsh(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.tclsh

           You can type Tcl commands and expressions into the iTest Tcl Shell session window.
           iTest captures your commands and the interpreter's responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.tclsh')

    @property
    def telnet(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.telnet

           A virtual terminal that communicates with a device using the Telnet protocol defined in RFC 854
           Note: Because Linux and Unix devices typically include Telnet and SSH servers, you can start a Telnet
           or SSH session to "localhost" to access a shell.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.telnet')

    @property
    def web(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.web """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.web')

    @property
    def powershell(self):
        """Return session profile obj with URI=application://com.spirent.itest.applications.powershell

           PowerShell sessions execute commands at the Windows PowerShell prompt. The PowerShell session
           window displays your commands and the local PC's responses.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.powershell')

    @property
    def wireshark(self):
        """Return session profile obj with URI=application://com.fnfr.svt.applications.wireshark

           Wireshark sessions provide a command line interface for interactively capturing packets from a network interface.
           For commands that return status and packet data, iTest saves the responses as structured data and generates
           associated queries to simplify pass/fail analysis.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.fnfr.svt.applications.wireshark')

    @property
    def landsliderest(self):
        """Return session profile obj with URI=application://com.spirent.itest.applications.landsliderest

        You can use iTest to automate Spirent Landslide tests.
        In iTest, when you start a Landslide session, iTest launches the Landslide TAS user interface running on the Landslide device.
          1. Now you can interact with the TAS in the normal way. For example, you might load a test configuration, start the test session,
        collect the responses, wait to collect several data sets, stop the test session, request the test session results, and then close the test session.
          2. When you are finished working on the TAS, you return to iTest and close the Landslide session window.
          3. You can now save the captured steps and responses as an iTest test case. As needed, you can modify and update the test case (for example, modify
        the ImportTestSuite step by causing it to load a different Landslide test suite file or replace the filename with a variable whose value is set at runtime).
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.landsliderest')

    @property
    def popmail(self):
        """Return session profile obj with URI=application://com.spirent.itest.applications.popmail

           You may se the Mail (POP3) sessions to retrieve emails from subscribers, view content, extract the required text and
           attachments, save the attached images as individual files, and then insert them into other sessions, for example, Selenium.
        """
        return SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.popmail')

#    @property
#   def scriptingSession(self):
#        """Return session profile obj with URI=application://com.spirent.itest.applications.sf.scriptingSession
#
#        The Script Library Support session type enables your iTest test cases to invoke functions and procedures
#        that are defined in external script libraries (your existing "home-grown" procedure libraries).
#       """
#        return SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.sf.scriptingSession')

    @property
    def stcrest(self):
        """Return session profile obj with URI=application://com.spirent.itest.applications.stcrest """
        return  SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.stcrest')

    @property
    def eggplant(self):
        """Return session profile obj with URI=application://com.spirent.itest.applications.testplant

           EggPlant Test session provides ways of automating execution of image-based GUI testing. The seamless testing of these iTest functionalities
           is achieved by iTest integration with EggPlant application (http://www.testplant.com/eggplant/testing-tools/eggplant-developer/).
        """
        return  SessionProfile(self._protosock, self._agent_type, 'application://com.spirent.itest.applications.testplant')

