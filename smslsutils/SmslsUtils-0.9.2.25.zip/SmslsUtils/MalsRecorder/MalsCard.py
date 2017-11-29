
from .SerialUtils import SerialUtils
import csv
import sys

ENCODING = 'ascii'

class MalsCard:
    num_channels = 6
    output_format = ['Sample','Temp','G1','P1','G2','P2','G3','P3','G4','P4','G5','P5','G6','P6']

    def __init__(self, port):
        
        self.ser = SerialUtils(port, baudrate=9600, encoding=ENCODING)

    def open(self):
        print('Opening SmslsTron connection on port {}...'.format(self.ser.port_name))
        self.ser.open_port()
        self.ser.flush_port()
        read_str = self.ser.read_line()
        print(read_str)
        try:
            self.ser.write_string('a')
        except:
            print('Failed to write start command to SmslsTron. Maybe it''s already running?')    

    def close(self):
        self.ser.close_port()
        print('Closed SmslsTron connection.')

    def read_data(self):
        # read new data from the serial port
        read_str = ''
        try:
            if self.ser.is_data_available():
                read_str = self.ser.read_line()
                #print(read_str)
        except:
            print("Unexpected error reading serial data:", sys.exc_info()[0])

        # parse the string into numbers
        values = {}
        if (len(read_str) > 0):
            chunks = read_str.split()
            for i in range(len(chunks)):
                try:
                    v = chunks[i].split(':')[-1]
                    val = 0
                    if '.' in v:
                        val = float(v)
                    else:
                        val = int(v)
                    values[self.output_format[i]] = val
                except ValueError:
                    print("Unexpected value in parsing serial data:", sys.exc_info()[0])
                except:
                    print("Unexpected error in parsing serial data:", sys.exc_info()[0])

            self.ser.flush_port()

        return values



class MalsCard_DesignService:
    num_channels = MalsCard.num_channels
    output_format = MalsCard.output_format

    def __init__(self, filepath):
        self.filepath = filepath
        self.cur_line = 0

    def open(self):
        self.fid = open(self.filepath, 'r')
        self.reader = csv.DictReader(self.fid)

    def close(self):
        self.fid.close()

    def read_data(self):
        # read new data from the csv file
        data = csv.DictReader.__next__(self.reader)
        values = {}
        for key in self.output_format:
            val = data[key]
            if '.' in val:
                val = float(val)
            else:
                val = int(val)
            values[key] = val
        return values

