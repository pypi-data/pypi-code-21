"""
.. uml::
@startuml

skinparam titleFontSize 20
skinparam titleFontColor blue
title State of Slave

skinparam state {
    StartColor MediumBlue
    EndColor Red

    BackgroundColor Peru
    BorderColor Gray
    ArrowColor red

    FontName Impact
    FontSize 16
    FontStyle plain
    FontColor black
    FontAlign center

    AttributeFontSize 12
    AttributeFontName sans
    AttributeFontStyle plain
    AttributeFontColor black
    AttributeFontAlign center

    ArrowFontSize 8
    ArrowFontName sans
    ArrowFontStyle italic
    ArrowFontColor black
    ArrowFontAlign left
}

[*] -down-> Idle : Newly\ncreated\nreader
Idle -left-> [*] : Timed out

state Idle {
    Idle : This state is renewed when a no event\nresponse is received from host.
    Idle -down-> Idle : No Event\nResponse
    Idle -down-> Processing : <-Event\nwith\nprotocol\nattached\nreceived\n
}

state Processing {
    Processing : Lookup protocol to determine how many keys and handler.
    Processing --> Waiting_For_Key : <-Waiting\nfor\nrequested\nkey
    Processing --> Idle : <-Approved/Denied

    state Validating {
        Validating : Validation will be handled by the validator which is a\ndynamic object, based on system options
    }
}

state Waiting_For_Key {
    Waiting_For_Key : Is a delay countdown state.\nIf the delay times out the\ntransaction is canceled.
    Waiting_For_Key --> Processing : <-Requested key\nsent for\nvalidation
}
@enduml

"""

import re
from struct import pack
from transitions import Machine

# Database
from modislock_monitor.database import (Database, Settings, SettingsValues, ReaderSettings)
from .protocol import Validator
from .protocol.base import BaseValidator
from .slave_message import SlaveResponse, SlaveRequest

# SQL Tools
from sqlalchemy import and_

# Timer
from threading import Timer


class SlaveReader(object):
    """SlaveReader represents a connected reader

    """
    states = ['idle', 'processing', 'waiting_for_key']

    def __init__(self, address, timeout=10, request_cb=None):
        """Main entry point for validation.

        Keeps track of address of origin of the frame.
        Has a state machine for the purpose of second validation cycle.

        :param int address: Address of Slave
        :param int timeout: Timeout for each request, after which time the session will end and return a denied
        :param func request_cb: Callback used when after validation/denied/request second key will send the message to

        """
        # Address of slave
        self._address = address

        # State machine
        self._machine = Machine(model=self, states=SlaveReader.states, initial='idle')

        # Transitions for the machine added
        self._machine.add_transition(trigger='no_event',
                                     source='idle',
                                     dest='idle',
                                     after='_reset')
        self._machine.add_transition(trigger='event_w_protocol',
                                     source='idle',
                                     dest='processing')
        self._machine.add_transition(trigger='second_key_needed',
                                     source='processing',
                                     dest='waiting_for_key')
        self._machine.add_transition(trigger='approved',
                                     source='waiting_for_key',
                                     dest='idle')
        self._machine.add_transition(trigger='approved',
                                     source='processing',
                                     dest='idle')
        self._machine.add_transition(trigger='denied',
                                     source='processing',
                                     dest='idle',
                                     after='_reset')
        self._machine.add_transition(trigger='denied',
                                     source='waiting_for_key',
                                     dest='idle',
                                     after='_reset')

        # Callback for write requests
        self.__request = request_cb or self._default_request_cb

        # Validation Callable
        self.__validator = None

        # Timer object
        self._timer = Timer(timeout, self._session_timeout)
        self._timer.start()

    def _session_timeout(self):
        """Session Callback

        If the session times out, it will be reported back to the monitor for session destruction

        """
        self._reset()

    def _default_request_cb(self, write_message):
        """Default request call back.

        .. note:: Used if none is provided.

        :param str write_message: Message to be sent to callback

        """
        pass

    def _reset(self):
        """Reset the validator.

        This represents a resolved validation request and will send a denied response
        back through the request_cb.

        """
        # self.__validator = None
        self._timer.cancel()
        send_msg = SlaveRequest(self._address, SlaveRequest.REQUEST_DENIED)
        self.__request(send_msg)

    def process_message(self, message_str):
        """Process incoming message

        Called during all stages of validation. Incoming packets are processed for
        validation or denied results. Results are passed to the request_cb.

        :param bytes message_str: Message to be processed originating from the reader

        """
        message = SlaveResponse(message_str)

        if self.address != message.address:
            self.no_event()
            return

        if self._machine.is_state('idle', self):
            if message.frame_type == SlaveResponse.RESPONSE_NO_EVENT:
                self.no_event()
                return
            elif message.frame_type == SlaveResponse.RESPONSE_EVENT_W_PROTOCOL:
                # Transition state to -> State Processing
                self.event_w_protocol()
            elif message.frame_type == SlaveResponse.RESPONSE_STATUS:
                # TODO: Status needs to be defined
                pass

        if self._machine.is_state('processing', self):
            """
            Process state is the main working area of the class. Validation and or request for second key here.
            """
            try:
                self.__validator = Validator(message.address, message.data)
            except (KeyError, TypeError):
                self.denied()
                return

            if self.__validator.valid:
                result = self.__validator.validate(message.data[3:])

                if result[0] == BaseValidator.VALIDATION_FIRST:
                    # Form message to reader, address, frame and challenge are on the argument
                    send_msg = SlaveRequest(message.address, SlaveRequest.REQUEST_SECOND_KEY, result[1])
                    # Change state machine to waiting_for_key
                    self.second_key_needed()
                    # Send the message
                    self.__request(send_msg)
                elif result[0] == BaseValidator.VALIDATION_OK:
                    self._timer.cancel()
                    self.approved()
                    send_msg = SlaveRequest(message.address, SlaveRequest.REQUEST_APPROVED, self.get_relay_settings())
                    self.__request(send_msg)

                elif (result[0] == BaseValidator.VALIDATION_DENIED) or \
                        (result[0] == BaseValidator.VALIDATION_NOT_FOUND) or \
                        (result[0] == BaseValidator.VALIDATION_ERROR):
                    self.denied()
            else:
                self.denied()
                return

        elif self._machine.is_state('waiting_for_key', self):
            if message.frame_type == SlaveResponse.RESPONSE_SECOND_KEY:
                # State Waiting_For_Key - received second key on frame
                result = self.__validator.validate(message.data)

                if result[0] == BaseValidator.VALIDATION_OK:
                    self.approved()
                    self._timer.cancel()
                    send_msg = SlaveRequest(message.address, SlaveRequest.REQUEST_APPROVED, self.get_relay_settings())
                    self.__request(send_msg)

                elif (result[0] == BaseValidator.VALIDATION_DENIED) or \
                        (result[0] == BaseValidator.VALIDATION_NOT_FOUND) or \
                        (result[0] == BaseValidator.VALIDATION_ERROR):
                    self.denied()
            else:
                self.denied()

    @property
    def address(self):
        """Address of current session slave address

        :returns: address of slave

        """
        return self._address

    def get_relay_settings(self):
        """Retrieves Reader Associated Relay Settings

        Requests the relay settings from the database. If the database fails, then relays fail to be triggered.

        .. note:: SELECT id_reader, location_name, id_settings, settings_name\n
                  FROM reader_settings\n
                  JOIN settings ON reader_settings.settings_id_settings = settings.id_settings\n
                  WHERE id_reader = 1;

        :returns: bytes - encoded relay settings

        """
        with Database() as db:
            # Database connection
            relay = db.session.query(ReaderSettings)\
                .join(Settings, ReaderSettings.settings_id_settings == Settings.id_settings)\
                .filter(ReaderSettings.id_reader == self._address)\
                .with_entities(ReaderSettings.id_reader, Settings.settings_name)\
                .first()

            relay_num = re.findall('\d+', relay[1])[0]

            # Relay options
            relay_options = db.session.query(Settings)\
                .join(SettingsValues, Settings.id_settings == SettingsValues.settings_id_settings)\
                .with_entities(Settings.settings_name, Settings.units, SettingsValues.value)\
                .filter(and_(Settings.settings_group_name == 'MONITOR',
                             Settings.settings_name.like('%' + relay_num + '%')))\
                .all()

            relay_settings = {'r1': 0, 'r1d': 0, 'r2': 0, 'r2d': 0, 'o1': 0, 'o2': 0}

            if relay_options is not None:
                for settings in relay_options:
                    if "RELAY_1" in settings[0]:
                        if "ENABLED" in settings[0]:
                            relay_settings['r1'] = 1 if settings[2] == 'ENABLED' else 0
                        elif 'DELAY' in settings[0]:
                            relay_settings['r1d'] = int(settings[2])
                    elif "RELAY_2" in settings[0]:
                        if "ENABLED" in settings[0]:
                            relay_settings['r2'] = 1 if settings[2] == 'ENABLED' else 0
                        elif 'DELAY' in settings[0]:
                            relay_settings['r2d'] = int(settings[2])
                    elif 'OUTPUT_1' in settings[0]:
                        relay_settings['o1'] = 1 if settings[2] == 'ENABLED' else 0
                    elif 'OUTPUT_2' in settings[0]:
                        relay_settings['o1'] = 1 if settings[2] == 'ENABLED' else 0

            """
            Formatting of the data is byte, int, byte, int , byte, byte
            """
            ret_relays = pack('>BIBIBB',
                              relay_settings['r1'],
                              relay_settings['r1d'],
                              relay_settings['r2'],
                              relay_settings['r2d'],
                              relay_settings['o1'],
                              relay_settings['o2'])

            return ret_relays
