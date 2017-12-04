
import struct

from plover.machine.base import SerialStenotypeBase


STENO_KEY_CHART = (
    None, 'S-', 'T-', 'K-', 'P-', 'W-', 'H-', 'R-',
    None, 'A-', 'O-', '*' , '-E', '-U', '-F', '-R',
    None, '-P', '-B', '-L', '-G', '-T', '-S', '-D',
    None, '-Z', '#' , None, None, None, None, None,
)


def _decode(packet):
    stroke = []
    mask = struct.unpack('<I', packet)[0]
    if (mask & 1) == 0:
        return []
    for n, key in enumerate(STENO_KEY_CHART):
        if key is None:
            continue
        if (mask & (1 << n)) != 0:
            stroke.append(key)
    return stroke


class ItalianStentura(SerialStenotypeBase):

    KEYMAP_MACHINE_TYPE = 'Stentura'

    KEYS_LAYOUT = '''
        #  #  #  #  #  #  #  #  #  #
        S- T- P- H- * -F -P -L -T -D
        S- K- W- R- * -R -B -G -S -Z
              A- O-   -E -U
        ^
    '''

    def run(self):
        self._ready()
        for packet in self._iter_packets(4):
            steno_keys = self.keymap.keys_to_actions(_decode(packet))
            if steno_keys:
                self._notify(steno_keys)
