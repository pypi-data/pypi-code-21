#!/usr/bin/env python2

import binascii
import unittest

from mock import patch

from plover.machine.keymap import Keymap

from plover_italian_stentura import ItalianStentura


class MockSerial(object):

    inputs = []
    machine = None

    def __init__(self, **params):
        self._opened = True

    def isOpen(self):
        return self._opened

    def close(self):
        assert self._opened
        self._opened = False

    def read(self, size=1):
        assert self._opened
        data = self.inputs.pop(0)
        assert len(data) <= size
        return data


class ItalianStenturaTest(unittest.TestCase):

    def test_decoding(self):
        inputs = [binascii.unhexlify(packet)
                  for packet in '''
                  A90020
                  00

                  05464000

                  A904
                  0400

                  0D065000

                  A1008000

                  05
                  820400

                  17
                  00
                  8000

                  05
                  08
                  00
                  00
                  '''.split()]
        # Mi piace mangiare la pizza.
        expected = 'CHRi/PIAce/CHRAh/PCIAre/HRa/PIsh/SPTa/P*'.split('/')
        keymap_mappings = {
            '#'   : '#',
            'S'   : 'S-',
            'P'   : 'T-',
            'C'   : 'K-',
            'T'   : 'P-',
            'H'   : 'W-',
            'V'   : 'H-',
            'R'   : 'R-',
            'I'   : 'A-',
            'A'   : 'O-',
            '*'   : '*',
            'E'   : '-E',
            'O'   : '-U',
            'c'   : '-F',
            's'   : '-R',
            't'   : '-P',
            'h'   : '-B',
            'p'   : '-L',
            'r'   : '-G',
            'i'   : '-T',
            'e'   : '-S',
            'a'   : '-D',
            'o'   : '-Z',
        }
        serial_params = {
            name: value[0]
            for name, value in ItalianStentura.get_option_info().items()
        }
        keymap = Keymap(ItalianStentura.KEYS_LAYOUT.split(), keymap_mappings.keys())
        keymap.set_mappings(keymap_mappings)
        with patch('plover.machine.base.serial.Serial', MockSerial) as mock:
            machine = ItalianStentura(serial_params)
            def stroke_callbak(steno_keys):
                self.assertEqual(''.join(steno_keys), expected.pop(0))
                if not expected:
                    machine.stop_capture()
            machine.add_stroke_callback(stroke_callbak)
            machine.set_keymap(keymap)
            mock.inputs = inputs
            mock.machine = machine
            machine.start_capture()
            machine.finished.wait()
        self.assertFalse(bool(expected))


if __name__ == '__main__':
    unittest.main()
