import re

class SDO_Read_Config:

    def __init__(self, file_name):
        self.__file_name = file_name
        self.__file_handler = self._open_file()
        self.__re_csv_line = r'(-?0x[\da-fA-F]+|-?\d+\.?\d?),?'
        self.__re_comment = r'#.+'
        self.__re_compile = re.compile(self.__re_csv_line)


    def _open_file(self):
        return open(self.__file_name, 'r')

    def _close_file(self):
        self.__file_handler.close()

    def _remove_comments(self, line):
        return re.sub(self.__re_comment, '', line)

    def _parse_line(self, line):
        return self.__re_compile.findall(line)

    def _convert_str_to_number(self, value):
        if '.' in value:
            return float(value)
        if 'x' in value:
            if value[0] == '-':
                return int(value[1:], 16) * -1
            return int(value, 16)
        return int(value)


    def _restructure_array(self, array):
        slave_count = len(array[0])-2
        slave_config_values = [[],[],[],[],[],[]]

        for line in array:
            for node in range(slave_count):
                slave_config_values[node].append([int(line[0], 16), int(line[1]), self._convert_str_to_number(line[node+2]) ] )

        return slave_config_values

    def parse_file(self):
        sdo_array = []
        for line in self.__file_handler:
            res = self._remove_comments(line)
            res = self._parse_line(res)
            if res and len(res) >= 3:
                sdo_array.append(res)

        self._close_file()

        sdo_array = self._restructure_array(sdo_array)

        return sdo_array