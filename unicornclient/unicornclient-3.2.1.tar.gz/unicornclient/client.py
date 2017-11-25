import socket
import time
import random
import logging
import ssl

from . import config
from . import parser
from . import handler
from . import sender
from . import manager

TIMEOUT = 30

class ShutdownException(Exception):
    pass

def main():
    logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)

    _parser = parser.Parser()
    _sender = sender.Sender()

    _manager = manager.Manager(_sender)
    _handler = handler.Handler(_manager)

    _manager.start_default()
    _sender.daemon = True
    _sender.start()

    while True:
        client = None
        try:
            address = (config.HOST, config.PORT)
            logging.info('connecting to ' + str(address))

            connection = socket.create_connection(address, TIMEOUT)
            connection.settimeout(TIMEOUT)

            ssl_context = ssl.create_default_context()
            if not config.SSL_VERIFY:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
            client = ssl_context.wrap_socket(connection, server_hostname=address[0])

            logging.info('authenticating')
            _sender.socket = client
            _manager.authenticate()

            while True:
                data = client.recv(128)
                if not data:
                    raise ShutdownException()
                _parser.feed(data)
                parsed = _parser.parse()
                for message in parsed:
                    _handler.handle(message)
                if not _sender.socket:
                    raise ShutdownException()

        except socket.error as err:
            logging.error('client socket error')
            logging.error(err)
        except ShutdownException as err:
            logging.critical('server shutdown')
        finally:
            if client:
                client.close()

        time.sleep(random.randint(0, 9))

if __name__ == '__main__':
    main()
