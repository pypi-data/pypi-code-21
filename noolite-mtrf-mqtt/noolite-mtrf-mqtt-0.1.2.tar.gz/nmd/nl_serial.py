import time
import logging

import serial

from .utils import Singleton

# Logging config
logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(lineno)s - %(levelname)s - %(message)s')


class NooLiteMessage:
    def __init__(self, ch, cmd, mode, id0, id1, id2, id3):
        self.mode = mode
        self.ch = ch
        self.cmd = cmd
        self.id0 = id0
        self.id1 = id1
        self.id2 = id2
        self.id3 = id3

    def __eq__(self, other):
        return all([
            self.mode == other.mode,
            self.ch == other.ch,
            self.id0 == other.id0,
            self.id1 == other.id1,
            self.id2 == other.id2,
            self.id3 == other.id3
        ])

    def is_id(self):
        return any([
            self.id0 != 0,
            self.id1 != 0,
            self.id2 != 0,
            self.id3 != 0
        ])


class NooLiteResponse(NooLiteMessage):
    def __init__(self, st, mode, ctr, togl, ch, cmd, fmt, d0, d1, d2, d3, id0, id1, id2, id3, crc, sp):
        super().__init__(ch, cmd, mode, id0, id1, id2, id3)
        self.st = st
        self.ctr = ctr
        self.togl = togl
        self.fmt = fmt
        self.d0 = d0
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.crc = crc
        self.sp = sp
        self.time = time.time()

    def __str__(self):
        return '{}'.format(self.to_list())

    def __repr__(self):
        return '{}'.format(self.to_list())

    @property
    def success(self):
        return self.ctr == 0

    def to_list(self):
        return [
            self.st,
            self.mode,
            self.ctr,
            self.togl,
            self.ch,
            self.cmd,
            self.fmt,
            self.d0,
            self.d1,
            self.d2,
            self.d3,
            self.id0,
            self.id1,
            self.id2,
            self.id3,
            self.crc,
            self.sp
        ]


class NooLiteCommand(NooLiteMessage):
    def __init__(self, ch, cmd, mode=0, ctr=0, res=0, fmt=0, d0=0, d1=0, d2=0, d3=0, id0=0, id1=0, id2=0, id3=0):
        super().__init__(ch, cmd, mode, id0, id1, id2, id3)
        self.st = 171
        self.ctr = ctr
        self.res = res
        self.fmt = fmt
        self.d0 = d0
        self.d1 = d1
        self.d2 = d2
        self.d3 = d3
        self.sp = 172

    def __str__(self):
        return '{}'.format(self.to_list())

    def __repr__(self):
        return '{}'.format(self.to_list())

    @property
    def crc(self):
        crc = sum([
            self.st,
            self.mode,
            self.ctr,
            self.res,
            self.ch,
            self.cmd,
            self.fmt,
            self.d0,
            self.d1,
            self.d2,
            self.d3,
            self.id0,
            self.id1,
            self.id2,
            self.id3,
        ])
        return crc if crc < 256 else divmod(crc, 256)[1]

    def to_list(self):
        return [
            self.st,
            self.mode,
            self.ctr,
            self.res,
            self.ch,
            self.cmd,
            self.fmt,
            self.d0,
            self.d1,
            self.d2,
            self.d3,
            self.id0,
            self.id1,
            self.id2,
            self.id3,
            self.crc,
            self.sp
        ]

    def to_bytes(self):
        return bytearray([
            self.st,
            self.mode,
            self.ctr,
            self.res,
            self.ch,
            self.cmd,
            self.fmt,
            self.d0,
            self.d1,
            self.d2,
            self.d3,
            self.id0,
            self.id1,
            self.id2,
            self.id3,
            self.crc,
            self.sp
        ])

    def description(self):
        return {
            'ST':   {'value': self.st, 'description': 'Стартовый байт'},
            'MODE': {'value': self.mode, 'description': 'Режим работы адаптера'},
            'CTR':  {'value': self.ctr, 'description': 'Управление адаптером'},
            'RES':  {'value': self.res, 'description': 'Зарезервирован, не используется'},
            'CH':   {'value': self.ch, 'description': 'Адрес канала, ячейки привязки'},
            'CMD':  {'value': self.cmd, 'description': 'Команда'},
            'FMT':  {'value': self.fmt, 'description': 'Формат'},
            'DATA': {'value': [self.d0, self.d1, self.d2, self.d3], 'description': 'Данные'},
            'ID':   {'value': [self.id0, self.id1, self.id2, self.id3], 'description': 'Адрес блока'},
            'CRC':  {'value': self.crc, 'description': 'Контрольная сумма'},
            'SP':   {'value': self.sp, 'description': 'Стоповый байт'}
        }


class NooliteSerial(metaclass=Singleton):
    def __init__(self, loop, tty_name, input_command_callback_method):
        self.tty = self._get_tty(tty_name)
        self.responses = []
        self.input_command_callback_method = input_command_callback_method
        self.loop = loop

        # Если приходят данные на адаптер, то они обрабатываются в этом методе
        self.loop.add_reader(self.tty.fd, self.inf_reading)

    def inf_reading(self):
        while self.tty.in_waiting >= 17:
            in_bytes = self.tty.read(17)
            resp = NooLiteResponse(*list(in_bytes))
            logger.debug('Incoming command: {}'.format(resp))
            self.loop.create_task(self.input_command_callback_method(resp))

    async def send_command(self, ch, cmd, mode=0, ctr=0, res=0, fmt=0, d0=0, d1=0, d2=0, d3=0, id0=0, id1=0, id2=0, id3=0):
        command = NooLiteCommand(ch, cmd, mode, ctr, res, fmt, d0, d1, d2, d3, id0, id1, id2, id3)

        # Write
        logger.info('> {}'.format(command))
        before = time.time()
        self.tty.write(command.to_bytes())
        logger.info('Time to write: {}'.format(time.time() - before))

    @staticmethod
    def _get_tty(tty_name):
        serial_port = serial.Serial(tty_name, timeout=2)
        if not serial_port.is_open:
            serial_port.open()
        serial_port.flushInput()
        serial_port.flushOutput()
        return serial_port
