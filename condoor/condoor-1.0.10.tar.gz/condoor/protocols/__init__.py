"""Protocols module providing different protocol handlers."""


from collections import defaultdict

from condoor.protocols.base import Protocol
from condoor.protocols.ssh import SSH
from condoor.protocols.telnet import Telnet
from condoor.protocols.telnet import TelnetConsole
from condoor.protocols.console import Console

protocol2object = defaultdict(
    Protocol, {
        'ssh': SSH,
        'telnet': Telnet,
        'telnet_console': TelnetConsole,
        'ssh_console': SSH,
        'console': Console,
        'console_console': Console,
    }
)


def make_protocol(protocol_name, device):
    """Make a protocol object factory function."""
    return protocol2object[protocol_name](device)
