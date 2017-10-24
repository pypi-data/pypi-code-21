"""
.. uml::
    @startuml
    skinparam backgroundColor #EEEBDC

    title Status Slave Heartbeat

    participant HOST
    participant SLAVE

    autonumber 1
    note over HOST, SLAVE: runs every second
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT <size:14>0x01</size>
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x01,0x00,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_NO_EVENT 0x10
    ... 50ms ...

    newpage Communication Single Key Approved
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x08,<PIN:8831>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_APPROVED 0x05
    ... 50ms ...

    newpage Communication Single Key Denied
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x08,<PIN:8831>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_DENIED 0x04
    ... 50ms ...

    newpage Communication Multiple Key Approved
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x01,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_EVENT 0x01
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x20,0x09,<U2F:23432>x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_EVENT_W_PROTOCOL 0x20
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x02,0x16,<1ST CHALLENGE>,0x21</size>""
    HOST -> SLAVE : REQUEST_SECOND_KEY 0x04
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x30,0x40,<2ND KEY>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_SECOND_KEY 0x30
    ... 50ms ...

    note over HOST #FFAAAA: ""<size:10>0x01,0x05,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_APPROVED 0x05
    ... 50ms ...

    newpage Slave Status
    skinparam backgroundColor #EEEBDC
    autonumber 1
    note over HOST #FFAAAA: ""<size:10>0x01,0x04,0x00,0x21</size>""
    HOST -> SLAVE : REQUEST_STATUS 0x03
    ... 50ms ...
    note over SLAVE #aqua: ""<size:10>0x01,0x40,0x10,<STATUS CODES>,x021</size>""
    SLAVE -[#blue]> HOST : RESPONSE_STATUS 0x40
    ... 50ms ...
    @enduml
"""
from abc import ABCMeta, abstractproperty, abstractmethod


class SlaveMessageBase(metaclass=ABCMeta):
    """Slave message base
.. uml::
    @startuml
    class LockMessage {
        -_address : INT
        -_frame_number : INT
        -_frame_type : INT
        -_data_size : INT
        -_data : INT
        -_crc : INT
        __methods__
        -_calculate_crc(*args)
        __setters/getters__
        +address()
        +frame_number()
        +data_size()
        +data()
        +crc()
    }
    @enduml
    """
    TERMINATOR = b'\n'
    MAX_DATA = 255

    @abstractmethod
    def message(self): pass

    @abstractmethod
    def address(self): pass

    @abstractmethod
    def frame_type(self): pass

    @abstractmethod
    def data_size(self): pass

    @abstractmethod
    def data(self): pass


class SlaveResponse(SlaveMessageBase):
    """Slave response from reader

    Communication coming from the reader in single byte array and parses into respective fields.

    """
    RESPONSE_NO_EVENT = 0x10
    RESPONSE_EVENT_W_PROTOCOL = 0x20
    RESPONSE_SECOND_KEY = 0x30
    RESPONSE_STATUS = 0x40

    def __init__(self, raw_msg):
        """Message comming from reader

        :param bytearray raw_msg:

        """
        if isinstance(raw_msg, (bytes, bytearray)):
            self._address = int.from_bytes(raw_msg[:1], byteorder='big')
            self._frame_type = int.from_bytes(raw_msg[1:2], byteorder='big')
            self._data_size = int.from_bytes(raw_msg[2:3], byteorder='big')

            if self._data_size is not 0:
                self._data = raw_msg[3:]
            else:
                self._data = None

    @property
    def message(self):
        """Message of response

        :returns: bytearray representing the message

        """
        msg = bytearray()
        msg.append(self._address)
        msg.append(self._frame_type)
        msg.append(self._data_size)

        if self._data_size is not None:
            data = self._data.to_bytes(self._data_size, byteorder='big')
            msg.extend(data)

        return msg

    @property
    def address(self):
        """Address of reader

        :returns: Address encoded on message

        """
        return self._address

    @property
    def frame_type(self):
        """Frame type of response

        :returns: Type of communication of message

        """
        return self._frame_type

    @property
    def data_size(self):
        """Size of data on response

        :returns: How much data was attached to the message

        """
        return self._data_size

    @property
    def data(self):
        """Data of response

        :returns: Returns the data encoded onto the message

        """
        return self._data


class SlaveRequest(SlaveMessageBase):
    """Slave request

    Represents the communication sent to the slave reader.

    Arguments passed to the class are encoded into a byte array
    suitable for transmission to the reader.

    >>> msg = SlaveRequest(0x01, 0x01, None)

    """
    REQUEST_EVENT = 0x01
    REQUEST_SECOND_KEY = 0x02
    REQUEST_STATUS = 0x03
    REQUEST_DENIED = 0x04
    REQUEST_APPROVED = 0x05

    def __init__(self, address, request_type, data=None):
        self._message = bytearray()
        self._message.append(address)
        self._message.append(request_type)
        self._data_size = 0
        self._data = None

        if data is not None:
            """
            If data is greater than 255 bytes, then drop the data.
            """
            if len(data) < self.MAX_DATA:
                self._data_size = len(data)
                self._message.append(self._data_size)
                self._data = data
                self._message.extend(self._data)
            else:
                self._message.append(0)
        else:
            self._message.append(0)

        # self._message.extend(self.TERMINATOR)

    @property
    def message(self):
        """Message of request

        :returns: bytearray representing the message

        """
        return self._message

    @property
    def address(self):
        """Address of request

        :returns: Address encoded on message

        """
        return int.from_bytes(self._message[:1], byteorder='big')

    @property
    def frame_type(self):
        """Frame type of request

        :returns: int - Type of communication of message

        """
        return int.from_bytes(self._message[1:2], byteorder='big')

    @property
    def data_size(self):
        """Data Size

        Number of bytes attached to message data section

        :returns: int - data size
        """
        return self._data_size

    @property
    def data(self):
        """Data on request

        :returns: bytearray - Returns the data encoded onto the message
        """
        return self._data


class ControllerMessage(SlaveMessageBase):

    CONTROLLER_REBOOT = b'R'
    CONTROLLER_TEMP = b'T'
    CONTROLLER_FLASH = b'F'
    CONTROLLER_LONG_FLASH = b'L'
    CONTROLLER_STATUS = 0x03

    def __init__(self, command):
        self._message = bytearray()
        self._message.append(0x00)
        self._message.append(self.CONTROLLER_STATUS)
        self._message.append(0x01)
        self._message.extend(bytes(command))

    @property
    def message(self):
        """Message of request

        :returns: bytearray representing the message

        """
        return self._message

    @property
    def address(self):
        """Address of request

        :returns: Address encoded on message

        """
        return int.from_bytes(self._message[:1], byteorder='big')

    @property
    def frame_type(self):
        """Frame type of request

        :returns: int - Type of communication of message

        """
        return int.from_bytes(self._message[1:2], byteorder='big')

    @property
    def data_size(self):
        """Data Size

        Number of bytes attached to message data section

        :returns: int - data size
        """
        return 0

    @property
    def data(self):
        """Data on request

        :returns: bytearray - Returns the data encoded onto the message
        """
        return None