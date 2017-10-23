import struct


def tlvs(data):
    while data:
        try:
            type, length = struct.unpack('!HH', data[:4])
            value = struct.unpack('!%is'%length, data[4:4+length])[0]
        except:
            print "Unproper TLV structure found: ", (data,)
            break
        yield type, value
        data = data[4+length:]
