
import serial

class SerialUtils:

    def __init__(self, port_name, baudrate=9600, encoding=None):
        self.port_name = port_name
        self.encoding = encoding

        self.ser = serial.Serial()
        self.ser.port = port_name
        self.ser.baudrate = baudrate
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.parity = serial.PARITY_NONE
        self.ser.stopbits = serial.STOPBITS_ONE

        self.ser.timeout = None      #block read
        self.ser.xonxoff = False     #disable software flow control
        self.ser.rtscts = False      #disable hardware (RTS/CTS) flow control
        self.ser.dsrdtr = False      #disable hardware (DSR/DTR) flow control
        self.ser.writeTimeout = 3
        self.ser.timeout = 0.2

    def open_port(self):
        self.ser.open()

    def close_port(self):
        self.ser.close()

    def flush_port(self):
        self.ser.flush()
        self.ser.flushInput()
        self.ser.flushOutput()

    def is_data_available(self):
        return self.ser.inWaiting() > 0

    def decode_string(self, string):
        # convert from bytes to string (using given string encoding scheme)
        return bytes(string).decode(self.encoding)

    def read_string(self, length):
        string = self.ser.read(length)
        if self.encoding is not None:
            string = self.decode_string(string)
        return string

    def read_line(self):
        line = self.ser.readline()
        if self.encoding is not None:
            line = self.decode_string(line)
        return line

    def read_lines(self):
        lines = []
        while self.is_data_available():
            line = self.read_line()
            lines.append(line)
        return lines

    def encode_string(self, string):
        # convert from string to bytes (using given string encoding scheme)
        return str(string).encode(self.encoding)

    def write_string(self, string):
        if self.encoding is not None:
            string = self.encode_string(string)
        length = self.ser.write(string)
        self.ser.flush()

    def write_lines(self, lines):
        for line in lines:
            write_string(line)

