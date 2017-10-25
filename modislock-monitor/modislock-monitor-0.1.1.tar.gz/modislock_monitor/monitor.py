# coding: utf-8

import os
import sys
import time
from datetime import datetime
from threading import Thread
from types import SimpleNamespace

# Queue
from .event_queue import EventQueue

# Serial Objects
from serial import SerialException, serial_for_url
from .transport import WatchedReader, PacketHandler

# Database
from .database import Database, Readings, ReaderStatus, Sensors
from sqlalchemy.exc import IntegrityError, OperationalError

# Extensions
from .extensions import log, mon_config

# Async
from .tasks import system_reset, factory_reset, reboot

# Readers
from .slave_reader import SlaveReader, SlaveRequest, SlaveResponse, ControllerMessage

# Pins
from .platform_detection import isRaspberryPi

# GPIO access
if isRaspberryPi:
    import RPi.GPIO as GPIO
else:
    import GPIOEmu as GPIO


# Inserts module path into system search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Monitor(object):
    """Monitor(Database)

    The monitor uses UART communication from the incoming reader requests to determine validation and onboard relay
    settings. GPIO pins associated with each reader are pulled high when a slave ID of 1 to 4 are responding to the
    heartbeat request sent out periodically.

    The Monitor object acts as the central validation source worker for the Modis Lock. The object is responsible for
    communication with the controller on the lock that in turn communicates to the remote readers. Interface with the
    Monitor and controller is done through UART.

    GPIO pins are used for both status information as well as sensor readings. These GPIO states are tracked with the
    use of a database connection. Without this connection the Monitor will fail to initialize.

    Usually a Monitor object can be created with defaults with the .. file::`__init__.py` file of the package like this:

    >>> from modislock_monitor import Monitor
    >>> monitor = Monitor()

    """
    # Configuration
    config = mon_config

    # Monitor elements
    monitor = SimpleNamespace(transport=None, sessions=dict(), events=EventQueue())

    def __init__(self):
        #: Check version of python
        if sys.version_info[:3] < self.config.REQUIRED_PYTHON_VER:
            log.error("Monitor requires at least Python {}.{}.{}".format(*self.config.REQUIRED_PYTHON_VER))
            sys.exit(1)

        #: Initialize the GPIO module and PINs
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(self.config.DEBUG)

        #: Status LED
        GPIO.setup(self.config.STATUS_PIN, GPIO.OUT, initial=GPIO.LOW)

        #: Initialize the readers, doors, and reset buttons
        self._init_readers()
        self._init_door_sensors()
        self._init_reset()

        #: Transportation mechanism
        class ReaderMessage(PacketHandler):
            """Packet Handler for communications between host and readers.

            The handler is quite simplified from the previous version and simply enqueues a task onto the event queue.

            """
            def __init__(self):
                super(ReaderMessage, self).__init__()

            def handle_packet(self, packet):
                """Places the packet with the handler function onto the event queue

                :param bytes packet:

                """
                Monitor.monitor.events.enqueue(Monitor.handle_incoming, args=[packet], priority=10)

            def handle_out_of_packet_data(self, data):
                """Handles any bytes received from outside a frame

                :param bytes data:
                """
                log.debug('Garbage received from uart outside of frame: {}'.format(data))

        # Serial port setup
        try:
            port = self.config.SERIAL_PORT['RPI_PORT'] if isRaspberryPi else self.config.SERIAL_PORT['PC_PORT']
            serial_port = serial_for_url(port, baudrate=115200, timeout=1)
        except SerialException as e:
            log.error('Error initializing serial port: {}'.format(e))
            raise IOError

        self.monitor.transport = WatchedReader(serial_port, ReaderMessage)
        self.running = False

    def _status_led_update(self):
        while self.running:
            time.sleep(0.5)
            GPIO.output(self.config.STATUS_PIN, not GPIO.input(self.config.STATUS_PIN))

    def _init_door_sensors(self):
        """Initialize the door sensors

        """
        def _update_door_status(gpio_id):
            """Thread worker that watches the door inputs

            Updates the database accordingly.

            :param int gpio_id: GPIO of door that has triggered the event

            """
            index = list(self.config.DOOR_PIN.keys())
            values = list(self.config.DOOR_PIN.values())
            index = index[values.index(gpio_id)]
            val = GPIO.input(self.config.DOOR_PIN[index])
            log.debug('Door Update:\nPin {}/{}\nStatus {}\n'
                      .format(gpio_id, index, 'HIGH' if val == GPIO.HIGH else 'LOW'))

            try:
                index = int(index[-1:])
            except ValueError:
                pass
            else:
                Monitor.monitor.events.enqueue(Monitor.handle_doors, args=[index, val], priority=100)

        for pin in self.config.DOOR_PIN.keys():
            # Setup Pin
            GPIO.setup(self.config.DOOR_PIN[pin], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            # Get Value
            value = GPIO.input(self.config.DOOR_PIN[pin])
            # Add event
            GPIO.add_event_detect(self.config.DOOR_PIN[pin],
                                  GPIO.BOTH,
                                  callback=_update_door_status)
            try:
                door_id = int(pin[-1:])
            except ValueError:
                pass
            else:
                with Database() as db:
                    query = db.session.query(Sensors)\
                        .filter(Readings.sensors_id_sensors == door_id) \
                        .first()

                    if query is not None:
                        query.value = "ACTIVE" if value == GPIO.HIGH else 'INACTIVE'

                        try:
                            db.session.commit()
                        except (IntegrityError, OperationalError):
                            db.session.rollback()
                            log.error('Status Monitor Database Error')
                    else:
                        door = Readings(value='ACTIVE' if value == GPIO.HIGH else 'INACTIVE',
                                        sensors_id_sensors=door_id)
                        db.session.add(door)

                        try:
                            db.session.commit()
                        except (IntegrityError, OperationalError):
                            db.session.rollback()
                            log.error('Status Monitor Database Error')

    def _init_readers(self):
        """Initialize the readers

        """
        def _update_reader_status(gpio_id):
            """Thread worker that updates the database based on GPIO inputs received through the configured pins.

            :param int gpio_id: GPIO of reader that updates status

            """
            index = list(self.config.READER_PIN.keys())
            values = list(self.config.READER_PIN.values())
            index = index[values.index(gpio_id)]
            val = GPIO.input(self.config.READER_PIN[index])

            log.debug('Reader Update:\nPin {}/{}\nStatus {}\n'
                      .format(gpio_id, index, 'HIGH' if val == GPIO.HIGH else 'LOW'))
            try:
                index = int(index[-1:])
            except ValueError:
                pass
            else:
                Monitor.monitor.events.enqueue(Monitor.handle_reader, args=[index, val], priority=50)

        for pin in self.config.READER_PIN.keys():
            # Setup PIN
            GPIO.setup(self.config.READER_PIN[pin], GPIO.IN)
            # Get initial value
            value = GPIO.input(self.config.READER_PIN[pin])
            # Add event to PIN
            GPIO.add_event_detect(self.config.READER_PIN[pin],
                                  GPIO.BOTH,
                                  callback=_update_reader_status)
            try:
                reader_id = int(pin[-1:])
            except ValueError:
                pass
            else:
                with Database() as db:
                    query = db.session.query(ReaderStatus) \
                        .filter(ReaderStatus.reader_id_reader == reader_id) \
                        .one_or_none()

                    if query is not None:
                        query.status = 'DISCONNECTED' if value == GPIO.LOW else 'CONNECTED'

                        try:
                            db.session.commit()
                        except (IntegrityError, OperationalError) as e:
                            db.session.rollback()
                            log.error(e.args[0])
                    else:
                        reader = ReaderStatus(status='DISCONNECTED' if value == GPIO.LOW else 'CONNECTED',
                                              reader_id_reader=reader_id)
                        db.session.add(reader)

                        try:
                            db.session.commit()
                        except (IntegrityError, OperationalError):
                            db.session.rollback()
                            log.error('Status Monitor Database Error')

    def _init_reset(self):
        """Initialize the reset button

        """
        self.reset_time = datetime.now()

        def _update_reset_status(gpio):
            """Thread worker that watches the reset button.

            Has 2 tasks, a short press of less than 30 seconds resets the
            system. A longer than 30 second press resets the system to factory defaults

            :param int gpio: GPIO number

            """
            config = mon_config

            if GPIO.input(config.RESET_PIN) == GPIO.LOW:
                self.reset_time = datetime.now()
            else:
                seconds_past = (datetime.now() - self.reset_time).total_seconds()
                log.debug('Reset btn held down for {} seconds'.format(seconds_past))

                if 2.0 < seconds_past <= 10.0:
                    log.info('Reset Host')
                    reboot.delay()
                elif 10.0 < seconds_past <= 30.0:
                    log.info('Reset settings in database')
                    system_reset.delay()
                elif seconds_past > 30.0:
                    log.info('Reset everything to factory')
                    factory_reset.delay()
                else:
                    self.reset_time = None

        GPIO.setup(self.config.RESET_PIN,
                   GPIO.IN)

        GPIO.add_event_detect(self.config.RESET_PIN,
                              GPIO.BOTH,
                              callback=_update_reset_status,
                              bouncetime=100)

    @classmethod
    def handle_incoming(cls, packet):
        """Handles incoming packets from controller over UART

        :param bytes packet: Incoming packet request from transport

        """
        if len(packet) < 3:
            log.debug('Malformed frame, under 3 bytes.')
            return

        try:
            slave_id = int.from_bytes(packet[:1], byteorder='big')
            frame_type = int.from_bytes(packet[1:2], byteorder='big')
            req_size = int.from_bytes(packet[2:3], byteorder='big')
        except ValueError:
            log.debug('Malformed frame. Unable to convert bytes to integer representations.')
            return

        reader = None

        if (0 < slave_id <= cls.config.MAX_SLAVES) and \
                (SlaveResponse.RESPONSE_NO_EVENT <= frame_type <= SlaveResponse.RESPONSE_STATUS):

            log.debug('Incoming request from:\nSlave->{}\nFrame type->{}\nMessage: {}'
                      .format(slave_id, hex(frame_type), ''.join('%02x' % b for b in packet)))

            if frame_type == SlaveResponse.RESPONSE_NO_EVENT:
                # TODO: Heartbeat, at present, heartbeat is not passed from controller to host
                pass
            elif frame_type == SlaveResponse.RESPONSE_EVENT_W_PROTOCOL:
                if req_size > 3 and slave_id not in cls.monitor.sessions:
                    reader = SlaveReader(slave_id, request_cb=Monitor.handle_outgoing)
                    cls.monitor.sessions[slave_id] = reader
            elif frame_type == SlaveResponse.RESPONSE_SECOND_KEY:
                if req_size > 0 and slave_id in cls.monitor.sessions:
                    reader = cls.monitor.sessions[slave_id]

            if reader is not None:
                reader.process_message(packet)
        elif slave_id == 0:
            if frame_type == SlaveResponse.RESPONSE_STATUS:
                # TODO: Controller status here
                pass
        else:
            log.error('Address {} is an incorrect address request for slave device'.format(slave_id))

    @classmethod
    def handle_outgoing(cls, packet):
        """Handles all processed packages returning from the slave reader objects

        :param SlaveRequest packet: Frame outgoing through controller to reader

        """
        if isinstance(packet, SlaveRequest):
            log.debug('Outgoing message to:\nSlave->{}\nFrame type->{}\nMessage: {}'
                      .format(packet.address,
                              packet.frame_type,
                              ''.join('%02x' % b for b in packet.message)))

            if packet.frame_type == SlaveRequest.REQUEST_DENIED or packet.frame_type == SlaveRequest.REQUEST_APPROVED:
                try:
                    del cls.monitor.sessions[packet.address]
                except KeyError:
                    log.error('Key not found in sessions')

            cls.monitor.transport.send_packet(packet.message)

    @classmethod
    def handle_doors(cls, sensor_id, value):
        """Handles door sensors changes from GPIO interrupts

        :param int sensor_id: GPIO Number of door sensor
        :param int value: LOW(0) | HIGH(1)

        """
        with Database() as db:
            query = db.session.query(Readings) \
                .filter(Readings.sensors_id_sensors == sensor_id) \
                .one_or_none()

            if query is not None:
                query.value = 'ACTIVE' if value == GPIO.HIGH else 'INACTIVE'

                try:
                    db.session.commit()
                except (IntegrityError, OperationalError):
                    db.session.rollback()
                    log.error('Error updating door status in database')

    @classmethod
    def handle_reader(cls, reader_id, value):
        """Handles the reader changes from GPIO interrupts

        :param int reader_id: Reader GPIO pin number
        :param int value: LOW(0) | HIGH(1)

        """
        with Database() as db:
            query = db.session.query(ReaderStatus) \
                .filter(ReaderStatus.reader_id_reader == reader_id) \
                .one_or_none()

            if query is not None:
                query.status = 'CONNECTED' if value == GPIO.HIGH else 'DISCONNECTED'

                try:
                    db.session.commit()
                except (IntegrityError, OperationalError):
                    db.session.rollback()
                    log.error('Error updating reader status is database')

    def run(self):
        """Runs the monitor thread

        Waits for interrupts and processes the event queue. During startup will send a command to the controller
        to restart.

        """
        self.monitor.transport.start()

        while not self.monitor.transport.is_alive():
            time.sleep(0.5)

        self.running = True
        # Reset on-board controller
        self.monitor.transport.send_packet(ControllerMessage(ControllerMessage.CONTROLLER_REBOOT).message)
        status_thread = Thread(target=self._status_led_update())
        status_thread.start()

        while self.running:
            while self.monitor.events.has_more():
                # Dequeue functions to run
                func, args, kwargs = self.monitor.events.dequeue()

                if func is not None:
                    func(*args, **kwargs)

        self.monitor.transport.stop()
        status_thread.join()
        GPIO.cleanup()

    def stop(self):
        """Stops the current running monitor

        """
        log.info('Monitor shutdown requested')
        self.running = False



