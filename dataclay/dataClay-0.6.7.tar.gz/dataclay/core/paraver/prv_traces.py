from collections import namedtuple
from enum import Enum  # Backport of enum "enum34"

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class TraceType(Enum):
    METHOD = 0
    SEND_REQUEST = 1
    SEND_RESPONSE = 3
    RECEIVE = 2


class TraceMethod(namedtuple("TraceMethod",
                             ["thread_id", "time", "enter_flag", "full_name"])):
    """Named tuple container for method traces, with some utility functions."""
    @classmethod
    def build_from_entry(cls, entry_data, nano_drift=0):
        """Factory method used when reading .prv files."""
        return cls(int(entry_data[1]), int(entry_data[2]) + nano_drift,
                   True if entry_data[3] == "1" else False, entry_data[4])

    def is_enter(self):
        return self.enter_flag


class TraceSend(namedtuple("TraceSend",
                           ["thread_id", "time", "sending_port", "request_id",
                            "desthost_ip", "dest_port", "message_size", "method_id"])):
    """Named tuple container for network send traces, with some utility functions."""
    @classmethod
    def build_from_entry(cls, entry_data, nano_drift=0):
        """Factory method used when reading .prv files."""
        return cls(int(entry_data[1]), int(entry_data[2]) + nano_drift,
                   int(entry_data[3]), int(entry_data[4]), entry_data[5],
                   int(entry_data[6]), int(entry_data[7]), int(entry_data[8]))


class TraceReceive(namedtuple("TraceReceive",
                              ["thread_id", "time", "origin_host_ip", "origin_host_port",
                               "request_id", "method_id"])):
    """Named tuple container for network receive traces, with some utility functions."""
    @classmethod
    def build_from_entry(cls, entry_data, nano_drift=0):
        """Factory method used when reading .prv files."""
        return cls(int(entry_data[1]), int(entry_data[2]) + nano_drift, entry_data[3],
                   int(entry_data[4]), int(entry_data[5]), int(entry_data[6]))
