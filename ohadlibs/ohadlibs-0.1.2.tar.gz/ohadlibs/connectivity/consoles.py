import telnetlib

from paramiko.ssh_exception import SSHException

from third_parties.python_ssh import Connection


# --------------- Classes ---------------


class RemoteConsole:

    def __init__(self, address, username, password, port):
        self.address = address
        self.username = username
        self.password = password
        self.port = port

    def test_connection(self):
        pass


class SSHConsole(RemoteConsole):

    def __init__(self,  address, username, password):
        RemoteConsole.__init__(self, address, username, password, '22')

    def test_connection(self):
        try:
            conn = Connection(self.address, 'admin', password='admin', port=22)
            print conn
        except SSHException:
            print "Unable to connect."


class TelnetConsole(RemoteConsole):

    def __init__(self,  address, username, password):
        RemoteConsole.__init__(self, address, username, password, '23')

    def test_connection(self):
        tn = telnetlib.Telnet(self.address)
        tn.open(self.address, self.port, timeout=30)
