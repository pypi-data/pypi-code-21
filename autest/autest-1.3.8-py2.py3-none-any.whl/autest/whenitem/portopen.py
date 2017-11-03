import socket
from autest.api import AddWhenFunction
import hosts.output as host

def PortOpen(port, address=None, timeout=None):

    ret = False
    if address is None:
        address = "localhost"

    if timeout is None:
        timeout = .5

    address = (address, port)

    try:
        s = socket.create_connection(address, timeout=timeout)
        s.close()
        ret = True
    except socket.error:
        s = None
        ret = False
    except socket.timeout:
        s = None
    host.WriteDebug(["portopen", "when"],
                    "checking port {0} = {1}".format(port, ret))

    return ret


AddWhenFunction(PortOpen)
