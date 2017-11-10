"""
IoT Device implementation

Utility library that allows easy creation and usage of a virtual device with following functionality:

- Loading arbitrary message descriptions
- Being able to provide argument data vectors, or randomize data in given range
- Argument encoding
- Common settings such as update intervals, etc...
- Handling all required protocol layer packages (crc checks...)
- Handling of queries and updates
- Possible to extend functionality ala basic service

"""
import json
import datetime

from datetime import timezone


class IoTDevice():
    """
    Device representation

    """
    def __init__(self, phy_handler, parameters=None, filename=None ):
        """

        :param parameters:
        :param filename:
        :param frame_handler:
        """
        if not parameters and not filename:
            raise Exception("Device parameters not defined")

        self.msg = MessageLayer(parameters=parameters, filename=filename)
        self.frame = FrameLayer(phy_handler=phy_handler, msg_handler=self.msg)
        self.msg.bind_frame_layer(self.frame)
        phy_handler.bind_frame_layer(self.frame)

    def put_args(self, msgno, args):
        """

        :param msgno:
        :param args:
        :return:
        """
        self.msg.put_args(msgno,args)

class MessageLayer():
    """
    Message and Device layer representation, contains

    - description and argument data
    - Message encoding/decoding
    - Query processing
    """
    __ARG_FLAG = 0x00
    __DESC_FLAG = 0x80
    __MAX_MSG = 127  # max message ID
    __ID = 0x7F  # protocol ID

    __FIELD_DESCRIPTION = 'description'
    __FIELD_ARGS = 'args'
    __FIELD_LENGTH = 'length'
    __FIELD_MSGNUM = 'msgnum'
    __FIELD_FLAG = 'flag'
    __FIELD_DATA = 'data'

    def __init__(self, parameters=None, filename=None, frame_handler=None):
        """

        :param parameters:
        :param filename:
        :param frame_handler:
        """
        if parameters:
            self.init_device_parameters( parameters)
        elif filename:
            self.init_device_parameters_from_file(filename)

        self.bind_frame_layer( frame_handler)

    def bind_frame_layer(self, frame_handler):
        """

        :param frame_handler:
        :return:
        """
        self.frame_handler = frame_handler

    def put_args(self, msgno, args):
        """

        :param msgno:
        :param args:
        :return:
        """
        msg = {self.__FIELD_FLAG: int(self.__ARG_FLAG)}
        msg[self.__FIELD_MSGNUM] = int(msgno)
        msg[self.__FIELD_DATA] = args

        self.put_message(msg)

    def put_message(self, message):
        """
        Process message
        :param message:
        :return:
        """
        flag = message[self.__FIELD_FLAG]
        msgno = message[self.__FIELD_MSGNUM]
        response = None

        if flag == self.__ARG_FLAG:
            args = message[self.__FIELD_DATA] if self.__FIELD_DATA in message.keys() else None
            response = self._process_arg_query(msgno, data=args)
        elif flag == self.__DESC_FLAG:
            response = self._process_description_query(msgno)

        if response :
            self.send_message(response)

    def get_message(self, msg_id):
        """

        :param msg_id:
        :return:
        """
        #msg = self.messages

    def init_device_parameters(self, parameters):
        """
        Initialize device

        :param descriptions:
        :return:
        """
        desc = parameters['messages']
        self.messages = {}
        self.max_msg = 0
        for k,v in desc.items() :
            entry = {}
            entry[self.__FIELD_DESCRIPTION] = bytearray(v[self.__FIELD_DESCRIPTION], 'utf-8')
            entry[self.__FIELD_MSGNUM] = int(k)

            if 'args' in v.keys():
                args = v[self.__FIELD_ARGS]
                entry[self.__FIELD_ARGS] = bytearray.fromhex(args)
            elif self.__FIELD_LENGTH in v.keys():
                len = v[self.__FIELD_LENGTH]
                length = int(str(len))
                entry[self.__FIELD_ARGS] = bytearray(length)
            # print(str(val) + " : " + str(val.text) + " : " + str((val.text is None)))

            self.messages[k] = entry

            if int(k) > self.max_msg:
                self.max_msg = int(k)

            # print ("msg: " + str(entry['msgnum']))
            # print("dsc: " + str(entry['description']))
            # print("arg: " + str(entry['args']))

    def init_device_parameters_from_file(self, filename):
        """
        Load description data from json file

        :param filename:
        :return: json description data
        """
        f = open(str(filename), 'r')
        data = f.read()

        desc = json.loads(str(data))
        self.init_device_parameters(desc)
        #print(json.dumps(desc, indent=4))


    def _process_arg_query(self, num, data=None):
        """or update

        :param num:
        :param data:
        :return:
        """

        # Query for last message
        if num == self.__MAX_MSG:
            num = self.max_msg
        if str(num) in self.messages.keys():
            msg = self.messages[str(num)]
            if data:
                msg[self.__FIELD_ARGS] = data

            response = {self.__FIELD_FLAG : int(self.__ARG_FLAG)}
            response[self.__FIELD_MSGNUM] = num
            args = msg[self.__FIELD_ARGS]
            a_data = bytearray(len(args))
            a_data[:] = args
            response[self.__FIELD_DATA] = a_data
            return response

    def _process_description_query(self, num):
        """
        Handle description request

        :param num:
        :return:
        """
        if num == self.__MAX_MSG:
            num = self.max_msg

        if str(num) in self.messages.keys():
            msg = self.messages[str(num)]

            response = {self.__FIELD_FLAG: int(self.__DESC_FLAG)}
            response[self.__FIELD_MSGNUM] = num
            desc = msg[self.__FIELD_DESCRIPTION]
            d_data = bytearray(len(desc))
            d_data[:] = desc
            response[self.__FIELD_DATA] = d_data
            return response

    def receive_message_data(self, data, inx, length):
        """
        Process message from binary form

        :param data:
        :param inx:
        :param length:
        :return:
        """
        message = self._decode_message(data, inx, length)
        if message :
            self.put_message(message)
            # print("recv msg: " + str(length))

    def send_message(self, message):
        """
        Encode and send message

        :param message:
        :return:
        """
        data = self._encode_message(message)
        self.frame_handler.send_frame(data, 0, len(data))

    def _decode_message(self, data, inx, length):
        """
        Decode message into dict

        :param data:
        :param inx:
        :param length:
        :return: parsed message, None if unable to parse
        """
        message = {}

        msg_protocol = 0xFF & data[inx]

        if length < 2 or (msg_protocol != MessageLayer.__ID):
            return None

        message[self.__FIELD_FLAG] = data[inx + 1] & 0x80
        message[self.__FIELD_MSGNUM] = 0x7F & data[inx + 1]

        payload_data = None
        if length > 2:
            payload_data = bytearray(length - 2)
            payload_data[0:len(payload_data)] = data[inx + 2:inx + length]

        message[self.__FIELD_DATA] = payload_data

        return message

    def _encode_message(self, message):
        """
        Encode message into binary form

        :param message:
        :return:
        """
        arg_len = 0
        data = None
        if self.__FIELD_DATA in message.keys():
            data = message[MessageLayer.__FIELD_DATA]
            if data:
                arg_len = len(data)

        msg_data = bytearray(arg_len + 2)
        msg_data[0] = MessageLayer.__ID
        msg_data[1] = 0xFF & (message[self.__FIELD_MSGNUM] | message[self.__FIELD_FLAG])

        if arg_len > 0:
            msg_data[2:arg_len + 2] = data[0:arg_len]
        # print("msg_len: " + str(arg_len))
        return msg_data
        # print("encode: " + json.dumps(message))


class FrameLayer():
    """
    Frame layer representation
    """
    _SNCF_CRC8_POLYNOMIAL = 0x4D

    def __init__(self, phy_handler=None, msg_handler=None, frame_timeout=1000):
        """
        Initialize buffers

        :param buffer_size:
        :param frame_timeout:
        """

        self.frame_timeout = frame_timeout
        self._crc_table = self.__calculate_crc_table( FrameLayer._SNCF_CRC8_POLYNOMIAL)
        self.recv_buffer = bytearray(512)
        self.expected_length = 0
        self.recvsize = 0
        self.last_frame_ts = datetime.datetime.now(timezone.utc)

        self.rx_error_count = 0
        self.tx_error_count = 0
        self.rx_frame_count = 0
        self.tx_frame_count = 0

        self.bind_physical_layer(phy_handler)
        self.bind_message_layer(msg_handler)

    def bind_message_layer(self, msg_handler):
        """
        Bind upper message layer

        :param msg_handler:
        :return:
        """
        self.msg_handler = msg_handler

    def bind_physical_layer(self, phy_handler):
        """
        Bind lower physical layer

        :param phy_handler:
        :return:
        """
        self.phy_handler = phy_handler

    def send_frame(self, data, inx, length ):
        """
        Encode frame and send it to physical layer

        :param data: byte array data
        :param inx: starting index
        :param length: length
        :return:
        """

        frame = bytearray(length +2)

        id =  (0xFF & (0x80 | (length -1)))
        frame[0] = id
        frame[1:1 + length] = data[inx:inx+length]
        crc = self.__calculate_crc(frame, 0, len(frame)-1)
        frame[-1] = crc
        # print("id: " + hex(frame[0]))
        # print("crc: " + hex(crc))

        self.phy_handler.send_data(frame, 0, len(frame))

    def receive_frame_data(self, data, inx, length ):
        """
        Process new frame data

        :param data:
        :param inx:
        :param length:
        :return:
        """
        now = datetime.datetime.now(timezone.utc)

        # Frame timeout check
        if self.recvsize > 0 and self.last_frame_ts + datetime.timedelta(miliseconds = self.frame_timeout) > now:
            self.__reset_parameters()


        for i in range(inx, inx + length):

            d = data[i]

            #New frame
            if self.recvsize == 0 and (d & 0xFF) >= 0x80  and (d & 0xFF) <= 0xBF:

                self.last_frame_ts = now
                self.expected_length = (0x7F & d) +  2
                self.recv_buffer[0] = (d & 0xFF)
                self.recvsize += 1
            #Frame data
            elif self.recvsize > 0 :
                self.recv_buffer[self.recvsize] = (d & 0xFF)

                #Received sufficient data
                if self.recvsize >= self.expected_length :
                    self.recvsize +=1
                    res = self.decode_and_process_frame()

                    self.recvsize = 0
                    self.expected_length = 0

                else :
                    self.recvsize +=1

    def decode_and_process_frame(self):
        """
        Decode frame received from server

        :return: True on sucessful decode, false otherwise
        """

        id = 0xFF & self.recv_buffer[0]

        msg_layer_id = 0xFF & self.recv_buffer[1]
        if id >= 0x80 :
            len = (0x3F & id)  +  1

            if (len + 1 > self.recvsize):
                return False

            if len > 0 :

                crc = self.__calculate_crc(self.recv_buffer, 0, len + 1)
                if crc != self.recv_buffer[len + 1] :

                    self.rx_error_count +=1
                    return False

                self.rx_frame_count +=1

                #Send data to messsage layer
                self.msg_handler.receive_message_data( self.recv_buffer, 1, len)


    def __reset_parameters(self):
        """
        Reset receive parameters

        :return:
        """
        self.expected_length = 0
        self.recvsize = 0

    def __calculate_crc(self, data, start, end):
        """
        CRC check calculation

        :param data:
        :param inx:
        :param length:
        :return:
        """
        c = 0

        for i in range(start, end):
            c = self._crc_table[int(c & 0xFF) ^ int(data[i] & 0xFF)]

        return c

    def __calculate_crc_table(self, polynomial):
        """
        Initialize CRC claculation table

        :param polynomial:
        :return: None
        """
        #cs_table = bytearray(256)
        """cs_table = []
        for i in range(0, 256) :

            curr = int(i)
            for j in range(0,8) :

                if (curr & 0x80) is not 0 :
                    curr = (curr << 1) ^ int(polynomial)
                else :
                    curr = curr << 1

            #cs_table[i] = curr.to_bytes(1, byteorder='big')
            print("i: " + str(i) + " curr: " + str(curr))
            cs_table[i] = curr #bytes(int(curr))

        return cs_table
        """

        cs_table = (0x00, 0x4D, 0x9A, 0xD7, 0x79, 0x34, 0xE3, 0xAE, 0xF2, 0xBF, 0x68, 0x25, 0x8B,
                    0xC6, 0x11, 0x5C, 0xA9, 0xE4, 0x33, 0x7E, 0xD0, 0x9D, 0x4A, 0x07, 0x5B, 0x16,
                    0xC1, 0x8C, 0x22, 0x6F, 0xB8, 0xF5, 0x1F, 0x52, 0x85, 0xC8, 0x66, 0x2B, 0xFC,
                    0xB1, 0xED, 0xA0, 0x77, 0x3A, 0x94, 0xD9, 0x0E, 0x43, 0xB6, 0xFB, 0x2C, 0x61,
                    0xCF, 0x82, 0x55, 0x18, 0x44, 0x09, 0xDE, 0x93, 0x3D, 0x70, 0xA7, 0xEA, 0x3E,
                    0x73, 0xA4, 0xE9, 0x47, 0x0A, 0xDD, 0x90, 0xCC, 0x81, 0x56, 0x1B, 0xB5, 0xF8,
                    0x2F, 0x62, 0x97, 0xDA, 0x0D, 0x40, 0xEE, 0xA3, 0x74, 0x39, 0x65, 0x28, 0xFF,
                    0xB2, 0x1C, 0x51, 0x86, 0xCB, 0x21, 0x6C, 0xBB, 0xF6, 0x58, 0x15, 0xC2, 0x8F,
                    0xD3, 0x9E, 0x49, 0x04, 0xAA, 0xE7, 0x30, 0x7D, 0x88, 0xC5, 0x12, 0x5F, 0xF1,
                    0xBC, 0x6B, 0x26, 0x7A, 0x37, 0xE0, 0xAD, 0x03, 0x4E, 0x99, 0xD4, 0x7C, 0x31,
                    0xE6, 0xAB, 0x05, 0x48, 0x9F, 0xD2, 0x8E, 0xC3, 0x14, 0x59, 0xF7, 0xBA, 0x6D,
                    0x20, 0xD5, 0x98, 0x4F, 0x02, 0xAC, 0xE1, 0x36, 0x7B, 0x27, 0x6A, 0xBD, 0xF0,
                    0x5E, 0x13, 0xC4, 0x89, 0x63, 0x2E, 0xF9, 0xB4, 0x1A, 0x57, 0x80, 0xCD, 0x91,
                    0xDC, 0x0B, 0x46, 0xE8, 0xA5, 0x72, 0x3F, 0xCA, 0x87, 0x50, 0x1D, 0xB3, 0xFE,
                    0x29, 0x64, 0x38, 0x75, 0xA2, 0xEF, 0x41, 0x0C, 0xDB, 0x96, 0x42, 0x0F, 0xD8,
                    0x95, 0x3B, 0x76, 0xA1, 0xEC, 0xB0, 0xFD, 0x2A, 0x67, 0xC9, 0x84, 0x53, 0x1E,
                    0xEB, 0xA6, 0x71, 0x3C, 0x92, 0xDF, 0x08, 0x45, 0x19, 0x54, 0x83, 0xCE, 0x60,
                    0x2D, 0xFA, 0xB7, 0x5D, 0x10, 0xC7, 0x8A, 0x24, 0x69, 0xBE, 0xF3, 0xAF, 0xE2,
                    0x35, 0x78, 0xD6, 0x9B, 0x4C, 0x01, 0xF4, 0xB9, 0x6E, 0x23, 0x8D, 0xC0, 0x17,
                    0x5A, 0x06, 0x4B, 0x9C, 0xD1, 0x7F, 0x32, 0xE5, 0xA8)

        return cs_table


class PhysicalLayer():
    """
    Physical layer representation
    """

    def __init__(self, frame_handler=None):
        """
        Initialize buffers
        :param buffer_size:
        """
        self.bind_frame_layer( frame_handler)

    def bind_frame_layer(self, frame_handler):
        """

        :param frame_handler:
        :return:
        """

        self.frame_handler = frame_handler

    def process_received_data(self, data, inx, length):
        """
        Process data received from server

        :param data:
        :param inx:
        :param length:
        :return:
        """
        self.frame_handler.receive_frame_data(data, inx, length)

    def send_data(self, data, inx, length):
        """
        Send data over channel, override implementation
        :param data:
        :param inx:
        :param length:
        :return:
        """
        print("phy data to send: " + str(data))


file = 'c:\Workspace\python\pycharm\Tests\parameters.json'
#dev = MessageLayer(filename=file)


phy = PhysicalLayer()
dev =IoTDevice(phy, filename=file)


#"9F 7F 01 3D A1 FF FF 1E 00 71 9D FF FF D9 E6 FF FF 27 6D 61 0F 00 00 00 00 01 00 00 00 00 00 00 00 9E"
#9F 7F 01 3D A1 FF FF 1E 00 75 9D FF FF 94 E6 FF FF 0F 77 5E 0F 00 00 00 00 01 00 00 00 00 00 00 00 F8
#data = "7F 07 C4 09 00 00"
#data =bytearray.fromhex(data)
#frame.send_frame(data,0, len(data))

#full_data = "9F 7F 01 3D A1 FF FF 1E 00 75 9D FF FF 94 E6 FF FF 0F 77 5E 0F 00 00 00 00 01 00 00 00 00 00 00 00 F8"
"""
full_data = '85 7F 07 C4 09 00 00 B6'
full_data= bytearray.fromhex(full_data)
phy.process_received_data(full_data, 0, len(full_data))

full_data = '81 7F 0F 1F'
full_data= bytearray.fromhex(full_data)
phy.process_received_data(full_data, 0, len(full_data))

print('Finished test')
"""