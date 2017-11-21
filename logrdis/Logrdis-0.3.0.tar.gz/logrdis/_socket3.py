import logging
import asyncio
from asyncio import Protocol, DatagramProtocol
from .log import find_match

LOGGER = logging.getLogger(__name__)

class LogTCPProtocol(Protocol):
    """TCP Server derived from Protocol."""

    def __init__(self, cfg, sql):
        """Initialize Server with sql object.

        :param cfg: dict. parsed YAML config object (see config.py)
        :param sql: Adapter. initialized sql.Adapter object
        """
        super(LogTCPProtocol, self).__init__()
        self.data = ""
        self.cfg = cfg
        self.sql = sql
        self.transport = None

    def connection_made(self, transport):
        """Call on connection."""
        LOGGER.debug('Connection: {}'.format(transport.get_extra_info('peername')))
        self.transport = transport

    def connection_lost(self, exc):
        """Lost connection, log it."""
        LOGGER.debug('Connection lost: {}'.format(self.transport.get_extra_info('peername')))

    def data_received(self, data):
        """Data is ready.

        Uses sql object to parse and store logs
        """
        self.data += str(data)

        # Process raw log by newlines
        log_lists = self.data.split('\n')
        for log in log_lists:
            self.data.replace(log, '')
            tablename, match = find_match(log, self.cfg)

            if match is None or tablename is None:
                LOGGER.error('Could not find a match for {}'.format(log))
            else:
                self.sql.store(tablename, match)
                LOGGER.info('Stored match in {}'.format(tablename))
                self.data = ""

class LogUDPProtocol(DatagramProtocol):
    """UDP Server implementation."""

    def __init__(self, cfg, sql):
        """Initialize Server with sql object.

        :param cfg: dict. parsed YAML config object (see config.py)
        :param sql: Adapter. initialized sql.Adapter object
        """
        super(LogUDPProtocol, self).__init__()
        self.data = ""
        self.cfg = cfg
        self.sql = sql
        self.transport = None

    def connection_made(self, transport):
        """Call on connection."""
        LOGGER.debug('Connection: {}'.format(transport.get_extra_info('peername')))
        self.transport = transport

    def connection_lost(self, exc):
        """Lost connection, log it."""
        LOGGER.debug('Connection lost: {}'.format(self.transport.get_extra_info('peername')))

    def datagram_received(self, data, addr):
        """Data is ready.

        Uses sql object to parse and store logs
        """
        LOGGER.debug('Connection from {}'.format(addr))
        self.data += str(data)

        # Process raw log by newlines
        log_lists = self.data.split('\n')
        for log in log_lists:
            self.data.replace(log, '')
            tablename, match = find_match(log, self.cfg)

            if match is None or tablename is None:
                LOGGER.error('Could not find a match for {}'.format(log))
            else:
                self.sql.store(tablename, match)
                LOGGER.info('Stored match in {}'.format(tablename))
                self.data = ""

class AsynchSocketServer:
    """Create a loop and socket, based on type."""

    def __init__(self):
        """Initialize the socket based on socket_type.

        Manages the async socket and asyncio loop
        """
        self.loop = asyncio.new_event_loop()
        self.server = None
        self.protocol = None

    def run_forever(self, cfg, sql):
        """Start the server.

        :param cfg: YAML configuration directive, fully parsed (config.py)
        :param sql: Adapter. initialized
        :raises: KeyError
        """
        socket_type = cfg.get('socket')
        listen_host = cfg.get('listen_host', '')
        listen_port = cfg.get('listen_port', '4444')
        if socket_type not in ['tcp', 'udp']:
            raise KeyError('Invalid socket type found in configuration')

        if socket_type == 'tcp':
            self.protocol = LogTCPProtocol
        else:
            self.protocol = LogUDPProtocol

        coro = self.loop.create_server(lambda: self.protocol(cfg, sql), host=listen_host, port=listen_port)
        self.server = self.loop.run_until_complete(coro)

        LOGGER.debug('Starting server on {}'.format(self.server.sockets[0].getsockname()))
        try:
            self.loop.run_forever()
        except (SystemExit, KeyboardInterrupt):
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

    def stop(self):
        """Called by unit tests to cleanly stop the loop."""
        self.server.close()
        self.loop.call_soon_threadsafe(self.loop.stop)