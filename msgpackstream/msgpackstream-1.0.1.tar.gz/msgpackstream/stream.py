'''
Created on Nov 13, 2017

@author: Salim
'''
from _pyio import __metaclass__
from abc import ABCMeta, abstractmethod
from enum import Enum
from msgpackstream.format import FormatUtil, SegmentType, FormatType, ValueType, \
    EventType, ExtType
from _io import BytesIO
import binascii
import struct
from msgpackstream.errors import InvalidStateException
import datetime



class ParserState():
    '''
        Contains state of the parser. Parser state is represented by formattype to be prased, 
        template to be parsed based on and the length needed in the parsing process.
         
    '''
    def __init__(self, formattype, template, length=None, isdone=False, extcode=None):
        self.formattype = formattype
        self.template = template
        self._length = length
        self.remaining = length 
        self.isdone = isdone
        self.extcode = extcode
        
        
    def set_length(self, length):
        self._length = length
        self.remaining = length
    
    def get_length(self):
        return self._length 
        
    length = property(get_length, set_length)
    
    def __str__(self):
        return "ParserState formattype: " + str(self.formattype) + ", tempalte: " + str(self.template) + ", length: " + str(self.length) + ", remaining: " + str(self.remaining) + ", isdone: " + str(self.isdone) + ", extcode: " + str(self.extcode) + "}";



class  ScannerState(Enum):
    '''
        Scanner state contains the intention of the scanner and what it expects next based on what it has read so far
    '''
    IDLE = 1  # parser just started or has processed all given data successfully (no buffer exists)
    WAITING_FOR_HEADER = 2  # expecting a header byte to be read next
    WAITING_FOR_EXT_TYPE = 3  # expecting an extension type segment  
    WAITING_FOR_LENGTH = 4  # expecting length of the value to be read next
    WAITING_FOR_VALUE = 5  # expecting value to be read first
    SEGMENT_ENDED = 6  # segment finished parsing
        
    

class   ExtTypeParser():
    __metaclass__ = ABCMeta
    
        
    @abstractmethod
    def deserialize(self, exttype, buff, start , end):
        '''
            Should be implemented for every user defined extension type
        :param data:
        '''
    @abstractmethod
    def handled_extcode(self):
        pass
        
        
        

class TimestampParser(ExtTypeParser):
    
    def deserialize(self, exttype, buff, start, end):
        if exttype.formattype is FormatType.FIXEXT_4:
            return datetime.datetime.fromtimestamp(self.parse_uint(buff, start, end))
        elif exttype.formattype is FormatType.FIXEXT_8:
            val = self.parse_uint(buff, start, end)
            nsec = val >> 34
            sec = val & 0x00000003ffffffffL
            return datetime.datetime.fromtimestamp(sec + nsec / 1e9)
        elif exttype.formattype is FormatType.EXT_8:
            nsec = self.parse_uint(buff, start, start + 4)
            sec = self.parse_int(buff, start + 4, end)
            return datetime.datetime.fromtimestamp(sec + nsec / 1e9)
        else:
            raise Exception("Unsupported FormatType " + str(exttype.formattype) + " for Timestamp (extcode = -1)!!")        

    
    def handled_extcode(self):
        return -1
    
    def parse_uint(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return int(binascii.hexlify(buff.read((end - start))), 16)
    
    def parse_int(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        num = self.parse_uint(buff, start, end)
        l = (end - start)
        return self.twos_comp(num, l * 8)
    
    def twos_comp(self, val, bits):
        '''
            two complement to get negative
        :param val:
        :param bits:
        '''
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val  
        


class StreamUnpacker():
    '''
        StreamUnpacker provides a SAX-like unpacker that reads the input in stream and in batches. It will generate events accordingly. 
    '''
    
    def __init__(self):        
        self._stack = []
        self._scstate = ScannerState.IDLE
        self._state = None
        self.util = FormatUtil();
        self.prefix = []
        self.events = []
        self.memory = BytesIO()
        self.lastidx = 0;
        self._deserializers = {}
        self.register(TimestampParser())
        
    
    
    def process(self, buff):
        '''
            Process the input buffer. The buffer can contains all or a segment of the bytes from the complete message. 
            The function will buffer what will require extra bytes to be processed. 
        :param buff:
        '''
        
        # prepare pointers and inputs
        idx = self.memory.tell()
        self.memory.write(buff)
        self.memory.seek(idx)
            
        # read first byte 
        byte = self.memory.read(1)
        
        # process input while exists
        while byte:
            byte = ord(byte)
            
            # expected start of a new segment
            if self._scstate in [ScannerState.IDLE, ScannerState.WAITING_FOR_HEADER]:
                self.handle_read_header(byte)
                self.lastidx = idx + 1
            # the scanner expects to read one or multiple bytes that contain an 
            # integer contain the length of the value to be expected
            elif self._scstate is ScannerState.WAITING_FOR_LENGTH:
                self._state.remaining -= 1;  # decrease number of remaining bytes to get length
                if(self._state.remaining == 0):  # if no more bytes remaining
                    self.handle_read_length(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx + 1
            # if the scanner is expecting to parse one or multiple bytes as the value of the segment
            elif self._scstate is ScannerState.WAITING_FOR_VALUE:
                self._state.remaining -= 1;                               
                if(self._state.remaining == 0):
                    self.handle_read_value(self.memory, self.lastidx, idx + 1)
                    self.lastidx = idx + 1
            # if the scanner is expecting to parse an extension
            elif self._scstate is ScannerState.WAITING_FOR_EXT_TYPE:
                self.handle_read_ext_type(self.memory, idx)
                self.lastidx = idx + 1
            
            # if a data segment is ended
            if self._scstate is ScannerState.SEGMENT_ENDED:
                self.handle_segment_ended()                
            # proceed with scanning   
            idx = idx + 1
            byte = self.memory.read(1)
            
        # not finished processing all since it needed extra info     
        if self.lastidx is idx:
            self.memory = BytesIO()
            self.lastidx = 0
                
        
    
    def handle_read_length(self, buff, start, end):        
        '''
            handle read of number bytes needed to parse the value 
        :param buff:
        :param start:
        :param end:
        '''
        self._state.length = self.parse_uint(buff, start, end) * self._state.template.value.multiplier
    
        if self.current_state().template.value.valuetype is ValueType.NESTED:
            self.events.append((self.prefix[:], self._state.template.value.startevent, self._state.formattype, None))
            if self._state.template.value.multiplier is 1:
                self.prefix.append('item')
            if self._state.length is 0:  # it is an empty nested segment
                self._scstate = ScannerState.SEGMENT_ENDED
            else: 
                self.push_state()
                self._scstate = ScannerState.WAITING_FOR_HEADER
        else:
            if self._state.template.value.segmenttype is SegmentType.EXT_FORMAT:
                self._scstate = ScannerState.WAITING_FOR_EXT_TYPE
            else:
                self._scstate = ScannerState.WAITING_FOR_VALUE
                if self._state.length is 0:  # it is an empty nested segment
                    prefix = self.prefix[:]
                    if len(self._stack) > 0 and self._stack[-1].template.value.multiplier is 1:
                        prefix.append('item')
                    self.events.append((prefix, EventType.VALUE, self._state.formattype, self.empty_value(self._state.formattype)))
                    self._scstate = ScannerState.SEGMENT_ENDED
                
        
    
    def handle_read_value(self, buff, start, end):
        '''
            handle read of the value based on the expected length
        :param buff:
        :param start:
        :param end:
        '''
        segmenttype = self._state.template.value.segmenttype
        prefix = self.prefix[:]
        if len(self._stack) > 0 and self._stack[-1].template.value.multiplier is 1:
            prefix.append('item')
        
        value = None
        eventtype = None
        ftype = self._state.formattype
        # parsing value 
        if segmenttype in [SegmentType.HEADER_VALUE_PAIR, SegmentType.VARIABLE_LENGTH_VALUE, SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR]:
            self._scstate = ScannerState.SEGMENT_ENDED
            value = self.parse_value(self._state.formattype, buff, start, end)
            eventtype = EventType.VALUE            
        # next we should expect length
        elif segmenttype in [SegmentType.FIXED_EXT_FORMAT, SegmentType.EXT_FORMAT]:
            value = self.parse_ext_value(self._state.formattype, self._state.extcode, buff, start, end)
            eventtype = EventType.EXT
            ftype = ExtType(self._state.formattype, self._state.extcode)
        else:
            raise InvalidStateException(self._scstate, "header")
                  
        if len(self._stack) > 0 and self._stack[-1].template.value.multiplier is 2 and self._stack[-1].remaining % 2 is 0:
                self.events.append((prefix, EventType.MAP_PROPERTY_NAME, ftype, value))
        else:
            self.events.append((prefix, eventtype, ftype, value))
    
    def handle_read_header(self, byte):
        '''
            handle read of header and assign fetching the appropriate template that is needed to parse expected segment based on header
        :param byte:
        '''
        
        frmt = self.util.find(byte)
        template = self.util.find_template(frmt.value.code)
        segmenttype = template.value.segmenttype        
        # single byte segment
        if segmenttype is SegmentType.SINGLE_BYTE:
            self._scstate = ScannerState.SEGMENT_ENDED
            self._state = ParserState(frmt, template, isdone=True);
            self.events.append((self.prefix[:], EventType.VALUE, frmt, self.util.get_value(byte, frmt)))
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_VALUE_PAIR:
            self._scstate = ScannerState.WAITING_FOR_VALUE
            self._state = ParserState(frmt, template, length=template.value.length * template.value.multiplier , isdone=False);            
        # next we should expect value
        elif segmenttype is SegmentType.HEADER_WITH_LENGTH_VALUE_PAIR:
            length = self.util.get_value(byte, frmt) * template.value.multiplier
            self._state = ParserState(frmt, template, length=length , isdone=False);
            if self._state.template.value.valuetype is ValueType.NESTED:                
                self.events.append((self.prefix[:], self._state.template.value.startevent, frmt, None))
                if template.value.multiplier is 1:
                    self.prefix.append('item')
                if length is 0:
                    self._scstate = ScannerState.SEGMENT_ENDED
                else:
                    self.push_state()
                    self._scstate = ScannerState.WAITING_FOR_HEADER
            else:          
                if length is 0:
                    self.events.append((self.prefix, EventType.VALUE, self._state.formattype, self.empty_value(self._state.formattype)))
                    self._scstate = ScannerState.SEGMENT_ENDED
                else:
                    self._scstate = ScannerState.WAITING_FOR_VALUE
            
        # next we should expect length
        elif segmenttype is SegmentType.VARIABLE_LENGTH_VALUE:
            self._scstate = ScannerState.WAITING_FOR_LENGTH
            self._state = ParserState(frmt, template, length=template.value.length , isdone=False);
        # next we should expect length
        elif segmenttype is SegmentType.EXT_FORMAT:
            self._scstate = ScannerState.WAITING_FOR_LENGTH
            self._state = ParserState(frmt, template, length=template.value.length , isdone=False);
        # next we should expect type       
        elif segmenttype is SegmentType.FIXED_EXT_FORMAT:
            self._state = ParserState(frmt, template, length=template.value.length , isdone=False);
            self._scstate = ScannerState.WAITING_FOR_EXT_TYPE
        else:
            raise InvalidStateException(self._scstate, "header")
        
    def handle_read_ext_type(self, buff, idx):
        extcode = self.parse_int(buff, idx, idx + 1)
        self._state.extcode = extcode
        self._scstate = ScannerState.WAITING_FOR_VALUE
        if self._state.length is 0:  # it is an empty nested segment
            prefix = self.prefix[:]
            if len(self._stack) > 0 and self._stack[-1].template.value.multiplier is 1:
                prefix.append('item')
            self.events.append((prefix, EventType.EXT, ExtType(self._state.formattype, self._state.extcode), b''))
            self._scstate = ScannerState.SEGMENT_ENDED
        
        
        
    def parse_ext_value(self, formattype, extcode, buff, start, end):
        buff.seek(start)
        parser = self._deserializers.get(extcode, None)
        if parser:
            return parser.deserialize(ExtType(formattype, extcode), buff, start , end)
        else:
            return buff.read((end - start))
        
    def handle_segment_ended(self):
        '''
            process end of the segment based on template
        '''
        if self._state.template.value.endevent is not None:
            self.events.append((self.prefix[:], self._state.template.value.endevent, self._state.formattype, None))
             
        if(len(self._stack) is  0):
            self._scstate = ScannerState.IDLE            
            return         
        self.pop_state()
        self._state.remaining = self._state.remaining - 1
        if self._state.template.value.multiplier is 2:
            if  self._state.remaining % 2 is 1:
                self.prefix.append(self.events[-1][3])
            else:
                self.prefix.pop()
            
        if self._state.remaining is 0:
            if self._state.template.value.multiplier is 1:
                    self.prefix.pop()
            self._scstate = ScannerState.SEGMENT_ENDED
            self.handle_segment_ended()
        else:
            self._scstate = ScannerState.WAITING_FOR_HEADER
            self.push_state()
        
    
    def push_state(self):
        '''
            push the current state to stack and prepare for new segment to be read 
        '''
        self._stack.append(self._state)
        self._state = None
        
    def pop_state(self):
        '''
            pop what exists from stack
        '''
        self._state = self._stack.pop()        
         
                    
    def empty_value(self, formattype):
        '''
            returns default empty value 
        :param formattype:
        :param buff:
        :param start:
        :param end:
        '''
        if(formattype in [FormatType.STR_16, FormatType.STR_8, FormatType.STR_32, FormatType.FIXSTR]):
            return ''
        elif(formattype in [ FormatType.INT_16, FormatType.INT_32, FormatType.INT_64, FormatType.INT_8, FormatType.UINT_16]):
            return 0
        elif(formattype in [ FormatType.UINT_16, FormatType.UINT_32, FormatType.UINT_8, FormatType.UINT_64]):
            return 0
        elif(formattype in [ FormatType.FLOAT_32]):
            return float(0)
        elif(formattype in [  FormatType.FLOAT_64]):
            return float(0)
        elif(formattype in [  FormatType.BIN_8, FormatType.BIN_16, FormatType.BIN_32]):
            return b''
        
    def parse_value(self, formattype, buff, start, end):
        '''
            parse the value from the buffer given the interval for the appropraite bytes
        :param formattype:
        :param buff:
        :param start:
        :param end:
        '''
        if(formattype in [FormatType.STR_16, FormatType.STR_8, FormatType.STR_32, FormatType.FIXSTR]):
            return self.parse_str(buff, start, end)
        elif(formattype in [ FormatType.INT_16, FormatType.INT_32, FormatType.INT_64, FormatType.INT_8, FormatType.UINT_16]):
            return self.parse_int(buff, start, end)
        elif(formattype in [ FormatType.UINT_16, FormatType.UINT_32, FormatType.UINT_8, FormatType.UINT_64]):
            return self.parse_uint(buff, start, end)
        elif(formattype in [ FormatType.FLOAT_32]):
            return self.parse_float32(buff, start, end)
        elif(formattype in [  FormatType.FLOAT_64]):
            return self.parse_float64(buff, start, end)
        elif(formattype in [  FormatType.BIN_8, FormatType.BIN_16, FormatType.BIN_32]):
            return self.parse_bin(buff, start, end)
    
    def parse_uint(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return int(binascii.hexlify(buff.read((end - start))), 16)
    
    def parse_int(self, buff, start, end):
        '''
            parse an integer from the buffer given the interval of bytes
        :param buff:
        :param start:
        :param end:
        '''
        num = self.parse_uint(buff, start, end)
        l = (end - start)
        return self.twos_comp(num, l * 8)
    
    def parse_float32(self, buff, start, end):
        '''
            parses float 32 bit
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return struct.unpack('>f', buff.read((end - start)))[0]
    
    def parse_float64(self, buff, start, end):
        '''
            parses float 64 bit
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return struct.unpack('>d', buff.read((end - start)))[0]
    
    def twos_comp(self, val, bits):
        '''
            two complement to get negative
        :param val:
        :param bits:
        '''
        if (val & (1 << (bits - 1))) != 0:  # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)  # compute negative value
        return val  
    
    def parse_str(self, buff, start, end):
        '''
            parse string from the buffer
            
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return buff.read((end - start)) 
    
    def parse_bin(self, buff, start, end):
        '''
            parse binary array
            
        :param buff:
        :param start:
        :param end:
        '''
        buff.seek(start)
        return buff.read((end - start)) 
    
    
    def generate_events(self):
        '''
            returns the generated events for the given segment of bytes
        '''
        tmp = self.events
        self.events = []
        return tmp
    
    def current_state(self):
        '''
            returns the current state
        '''
        return self._state
    

    def register(self, parser):
        self._deserializers[parser.handled_extcode()] = parser
    
    
    
    '''
        No set function to prevent other classes to change state
    '''
    state = property(current_state)
    

        
        
        


def unpack(instream, buffersize=1000, parsers=[]):
    '''
        Creates an iterator instance for the unpacker
    :param instream:
    :param buffersize:
    '''
    return UnpackerIterator(instream, buffersize, parsers)
    
    
    
    
class UnpackerIterator(object):
    
    def __init__(self, instream, buffersize=1000, parsers=[]):
        self._instream = instream
        self._unpacker = StreamUnpacker()
        for parser in parsers:
            self._unpacker.register(parser)
        self._buffersize = buffersize
        self._events = []
        self._idx = 0
    
    def __iter__(self):
        return self

    def __next__(self):
        if self._idx >= len(self._events):
            self._events = []
#             try:                
            while len(self._events) is 0:
                self._idx = 0
                bytes_read = self._instream.read(self._buffersize)
                if not bytes_read:
                    raise StopIteration()
                self._unpacker.process(bytes_read)
                self._events = self._unpacker.generate_events()
#             except :
#                 raise StopIteration()
        event = self._events[self._idx]
        self._idx = self._idx + 1 
        return event
        
        

    next = __next__  # Python 2
    
    
    
    
