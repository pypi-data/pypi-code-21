from binascii import unhexlify
import re

from gcoin.main import num_to_hex, string_to_hex

from .py2specials import *
from .py3specials import *

OP_RETURN = 0x6a
OP_PUSH_DATA1 = 0x4c
OP_PUSH_DATA2 = 0x4d
OP_PUSH_DATA4 = 0x4e

MAX_SCRIPT_ELEMENT_SIZE = 128000


def script_push_data(data_string):
    data_len = len(from_string_to_bytes(data_string))

    if data_len < OP_PUSH_DATA1:
        script = ''
    elif data_len <= 0xff:
        script = num_to_hex(OP_PUSH_DATA1)
    elif data_len <= 0xffff:
        script = num_to_hex(OP_PUSH_DATA2)
    else:
        script = num_to_hex(OP_PUSH_DATA4)

    script += num_to_hex(data_len)
    script += string_to_hex(data_string)
    return script


def decode_op_return_script(script):
    """
    :params script: script in hex

    :retrun: message in bytes
    """
    script = script.lower()
    if not re.match('^6a[0-9a-f]{4,}', script):
        raise Exception()

    op_return_data = int(script[2:4], 16)
    if op_return_data == OP_PUSH_DATA1:
        return unhexlify(script[6:])
    elif op_return_data == OP_PUSH_DATA2:
        return unhexlify(script[8:])
    elif op_return_data == OP_PUSH_DATA4:
        return unhexlify(script[10:])
    else:
        return unhexlify(script[4:])
