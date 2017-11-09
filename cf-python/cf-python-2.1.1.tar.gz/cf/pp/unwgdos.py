import ctypes

from os     import path   as os_path
from struct import pack   as struct_pack
from struct import unpack as struct_unpack
from numpy  import array  as numpy_array

#from .. import __file__ as cf__file__

_c_char_p = ctypes.c_char_p
_c_int    = ctypes.c_int
_c_float  = ctypes.c_float

_create_string_buffer = ctypes.create_string_buffer

#_dll = ctypes.CDLL(os_path.join(os_path.dirname(os_path.abspath(cf__file__)),
#                                "lib/libunwgdos.so"))

_dll = ctypes.CDLL(os_path.join(os_path.dirname(os_path.abspath(__file__)),
                                "lib/libunwgdos.so"))

_c_unwgdos = _dll.unwgdos

_c_unwgdos.argtypes = (_c_char_p, _c_int, _c_char_p, _c_int, _c_float)

class BinConvert(object):
    '''
Originally written by Alan Iwi.
'''

    def __init__(self, wordsize, byteorder):
        '''
'''
        if wordsize == 4:
            self._intChar   = 'i'
            self._floatChar = 'f'
        elif wordsize == 8:
            self._intChar   = 'q'
            self._floatChar = 'd'
        else:
            raise ValueError('wordsize (%r) must be 4 or 8' % wordsize)

        if byteorder == 'native':
            self._orderChar = '='
        elif byteorder == 'little':
            self._orderChar = '<'
        elif byteorder == 'big':
            self._orderChar = '>'
        else:
            raise ValueError("byteorder (%r) must be 'native', 'big' or 'little'"
                             % byteorder)

        self._wordSize  = wordsize
        self._byteOrder = byteorder
    #--- End: def

    def __repr__(self):
        '''
x.__repr__() <==> repr(x)
'''
        return ("<CF BinConvert: wordsize=%d, byteorder=%r>" %
                (self._wordSize, self._byteOrder))
    #--- End: def

    def formatString(self, dataType, numWords):
        '''
'''
        if dataType is int:
            typeChar = self._intChar
        elif dataType is float:
            typeChar = self._floatChar
        else:
            raise ValueError("dataType %s is not int or float" % dataType)
        
        return "%s%d%s" % (self._orderChar, numWords, typeChar)
    #--- End: def

    # Note: the struct.pack() and struct.unpack() methods called here refer
    # simply to converting between numeric data and its binary representation.
    # Everywhere else in the code, references to "packing" are to the packing
    # methods that the UM provides in order to reduce file size.

    def binToVals(self, dataString, dataType):
        '''

:Parameters:

    dataString : str

    dataType : type
        
:Returns:

    out : tuple

'''
        if dataType is float:
            typeChar = self._floatChar
        elif dataType is int:
            typeChar = self._intChar
        else:
            raise ValueError("dataType %r is not float or int" % dataType)
        
        numWords = len(dataString) / self._wordSize
        format_string = "%s%d%s" % (self._orderChar, numWords, typeChar)

        return struct_unpack(format_string, dataString)
    #--- End: def

    def valsToBin(self, data):
        '''

Return a string containing the data array values packed according to
the appropiate format.

:Parameters:

    data : numpy array

:Returns:

    out : str
        The string containing the data array values.

'''
        format_string = "%s%d%s" % (self._orderChar, data.size, data.dtype.char)
        return struct_pack(format_string, *data)
    #--- End: def

#--- End: class

_converters = {4: BinConvert(4, 'native'),
               8: BinConvert(8, 'native')}        
_converter4 = _converters[4]

def unwgdos(packed_data, input_word_size, unpacked_length, mdi):
    '''

Originally written by Alan Iwi.

:Parameters:

    packed_data : list or str
        List of integers (int or long), or string of raw data.
    
    input_word_size : int
        4 or 8 per packed_data.

    unpacked_length : int
        Number of data items to expect.
    
    mdi : float
        Missing data value to use.

:Returns:

    out : numpy array
        A 1-d array of floats (length unpacked_length).

        '''
    if isinstance(packed_data, basestring):
        string_data_in = packed_data
        nbytes_in = len(string_data_in)
    else:
        string_data_in = _converters[input_word_size].valsToBin(packed_data)
        nbytes_in = len(packed_data) * input_word_size
        assert(nbytes_in == len(string_data_in))

    nin = nbytes_in / 4
    nout = unpacked_length
    nbytes_out = 4 * nout
    string_data_out = _create_string_buffer(nbytes_out)

    status = _c_unwgdos(string_data_in, nin, string_data_out, nout, mdi)
    if status != 0:
        raise RuntimeError("unwgdos returned %d" % status)

    data_out = _converter4.binToVals(string_data_out, float)

    assert(len(data_out) == unpacked_length)
    return numpy_array(data_out)
    

#    if isinstance(packed_data, basestring):
#        string_data_in = packed_data
#        nbytes_in = len(string_data_in)
#    else:
#        string_data_in = _converters[input_word_size].valsToBin(packed_data)
#        nbytes_in = packed_data.size * input_word_size
#        assert(nbytes_in == len(string_data_in))
#        print nbytes_in, len(string_data_in)
#
##    print  'string_data_in =', string_data_in
#    string_data_out = _create_string_buffer(unpacked_length * 4)
#
#    print input_word_size
#    print nbytes_in/input_word_size
#    print nbytes_in
#    print unpacked_length
#    print mdi
#
#    status = _c_unwgdos(string_data_in, nbytes_in/input_word_size,
#                        string_data_out, unpacked_length,
#                        mdi)
#    if status:
#        raise RuntimeError("_c_unwgdos returned %d" % status)
#
#    data_out = _converter4.binToVals(string_data_out, 'f')
#    print 'data_out=', data_out[:100]
#    assert(len(data_out) == unpacked_length)
#    return numpy_array(data_out)
#--- End: def    
