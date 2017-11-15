import hashlib
from binascii import hexlify
from struct import pack, unpack, calcsize


class _Frame(object):
    _major_version = 1
    _minor_version = 0
    _version_header = '<BB'
    _version_header_size = calcsize(_version_header)
    _1_0_format = '<32s16s34xI'
    _1_0_format_size = calcsize(_1_0_format)
    _full_1_0_format_header = "{}{}".format(_version_header, _1_0_format[1:])

    @staticmethod
    def hash(topic):
        btopic = topic.encode()
        hashed_obj = hashlib.sha256(btopic)
        hashed = hashed_obj.digest()
        return hashed

    def pack(self, topic, brewer_id, payload):
        fmt = "{}{}s".format(self._full_1_0_format_header, len(payload))
        packed = pack(fmt,
                      self._major_version, self._minor_version,
                      self.hash(topic), bytes.fromhex(brewer_id),
                      len(payload), payload)
        return packed

    def unpack(self, frame):
        # read major/minor versions
        major_version, minor_version = \
            unpack(self._version_header,
                   frame[:self._version_header_size])
        if major_version > self._major_version:
            raise ValueError("Major protocol version: '{}' does not match "
                             "supported version {}".
                             format(major_version, self._major_version))
        parse_start = self._version_header_size

        # start matching minor versions here
        topic, bid_bytes, payload_len = \
            unpack(self._1_0_format,
                   frame[parse_start:parse_start+self._1_0_format_size])
        parse_start += self._1_0_format_size
        payload, = \
            unpack('{}s'.format(payload_len), frame[parse_start:])
        return topic, hexlify(bid_bytes).decode(), payload

        # once subsequent versions are known, above code could test against its
        # version while falling back at the end to newest known version


Frame = _Frame()
