from multiprocessing import Array
from ..common.encryption import Encryption
class GlobalShareValue(object):
    configer_file_path = Array('i', range(200))
    @staticmethod
    def set_configer_file_path(path):
        _base_str = Encryption.encode_base64(path)

        share_size = len(GlobalShareValue.configer_file_path)
        base_str_size = len(_base_str)

        for i in range(share_size):
            if i >= base_str_size:
                GlobalShareValue.configer_file_path[i] = 0
            else:
                GlobalShareValue.configer_file_path[i] = ord(_base_str[i])
        return

    @staticmethod
    def get_configer_file_path():
        __value = []
        for i in GlobalShareValue.configer_file_path:
            __value.append(chr(i))
        s = ''.join(__value)
        result = Encryption.decode_base64(s)
        return result
