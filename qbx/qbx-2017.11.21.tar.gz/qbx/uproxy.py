# Super simple script that listens to a local UDP port and relays all packets to an arbitrary remote host.
# Packets that the host sends back will also be relayed to the local UDP client.
# Works with Python 2 and 3

import sys
import socket
from docopt import docopt as docoptinit

uproxy_doc = """
Usage:
    uproxy.py [options]

Options:
    --port=<port>                local port
    --dest=<dest>                dest format as host:port
"""


def fail(reason):
    sys.stderr.write(reason + '\n')
    sys.exit(1)


# uproxy --port port --dest host:port
def uproxy(argv):
    docopt = docoptinit(uproxy_doc, argv)
    print(docopt)
    port = int(docopt['--port'])
    dest = docopt['--dest']
    dest_host, dest_port = dest.split(':')
    dest_port = int(dest_port)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))
    except:
        fail('Failed to bind on port ' + str(port))

    known_server = (dest_host, dest_port)
    sys.stderr.write('All set.\n')
    while True:
        data, addr = s.recvfrom(32768)
        print('recv', data)
        s.sendto(data, known_server)


if __name__ == '__main__':
    uproxy(['--port', '12637', '--dest', 'localhost:3333'])
