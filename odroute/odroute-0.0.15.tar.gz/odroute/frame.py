# -*- coding: utf-8 -*-
import struct
import math

# The ZMQ frames from the audio encoder are expected
# to have the following format, in pseudo C struct, no alignment,
# little-endian. See ODR-DabMux' src/input/Zmq.h for reference.
#
#   uint16_t version; // we support version=1 now
#   uint16_t encoder; // see ZMQ_ENCODER_XYZ
#
#   /* length of the 'data' field */
#   uint32_t datasize;
#
#   /* Audio level, peak, linear PCM */
#   int16_t audiolevel_left;
#   int16_t audiolevel_right;
#
#   /* Data follows the header */
#   uint8_t data[datasize];

class ZMQFrameDecoder(object):
    """
    Decode a frame and extract the header information
    """

    def __init__(self):
        self.version = self.encoder = self.datasize = self.audiolevel_left = self.audiolevel_right = None

    def load_frame(self, frame):
        frame_header = "<HHIhh"

        headersize = struct.calcsize(frame_header)
        if len(frame) > headersize:
            # > instead of >= because we want to ensure there's also payload
            # TODO check that length of payload matches

            unpacked = struct.unpack(frame_header, frame[:headersize])
            self.version, self.encoder, self.datasize, self.audiolevel_left, self.audiolevel_right = unpacked
        else:
            self.version = self.encoder = self.datasize = self.audiolevel_left = self.audiolevel_right = None

    def version_is_valid(self):
        # See ODR-DabMux' src/input/Zmq.cpp for reference
        return self.version == 1

    def get_audio_levels(self):
        """
        Returns a tuple with left and right audio levels, or (None, None) if frame is not valid
        """
        if not self.version_is_valid():
            return (None, None)
        else:
            int16_max = 0x7FFF
            if self.audiolevel_left:
                dB_l = int(20*math.log10(float(self.audiolevel_left) / int16_max))
            else:
                dB_l = -90

            if self.audiolevel_right:
                dB_r = int(20*math.log10(float(self.audiolevel_right) / int16_max))
            else:
                dB_r = -90

            return (dB_l, dB_r)


