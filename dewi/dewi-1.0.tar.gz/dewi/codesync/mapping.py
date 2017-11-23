# Copyright 2016-2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import typing

MAPPING_ENTRY_TYPE = typing.Tuple[str, typing.Union[str, int]]


class InvalidMappingDefEntry(Exception):
    pass


class Mapping:
    pass


class Mapper:
    MAPPING_CLASS = Mapping

    @classmethod
    def create(cls,
               line: str,
               fields: typing.List[MAPPING_ENTRY_TYPE],
               min_num_of_columns: int,
               delimiter: str = ';') -> Mapping:
        columns = cls._split_line(line, delimiter)
        if len(columns) < min_num_of_columns:
            raise InvalidMappingDefEntry(
                "Not enough column is specified for current line; line='{ln}', columns='{cols}', min='{min}'".format(
                    ln=line, min=min_num_of_columns, cols=columns))

        if len(columns) > len(fields):
            raise InvalidMappingDefEntry(
                "Unexpected column in current line; line='{ln}', max='{mx}', count='{cnt}'".format(
                    ln=line, mx=len(fields), cnt=len(columns)))

        mapping = Mapping()
        for i in range(0, len(columns)):
            setattr(mapping, fields[i][0], columns[i] if len(columns[i]) or i < min_num_of_columns else fields[i][1])

        for i in range(len(columns), len(fields)):
            setattr(mapping, fields[i][0], fields[i][1])

            return mapping

    @classmethod
    def _split_line(cls, line: str, delimiter: str):
        return line.split(delimiter)
