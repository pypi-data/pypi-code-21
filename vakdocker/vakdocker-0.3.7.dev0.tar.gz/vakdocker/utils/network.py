#import socket
#import logging
from random import randint

def get_open_port(minp=8000, maxp=9000):
    port = randint(minp, maxp)

    #TODO: unable to check using this approach
    # Most like because loopback is blocked on cloud servers by default
    #sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #result = sock.connect_ex(('127.0.0.1', port))
    #print result
    #if result != 0:
        #logging.error('Trying Port %d - Could not connect externally' % (port))
        #raise Exception('Service expects ports between (%d, %d) to be open' \
                        #% (minp, maxp))

    return port

if __name__ == '__main__':
    get_open_port()
