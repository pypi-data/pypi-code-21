
''' read and write csv files using dict-rows
'''

import csv

from pathlib import Path

#----------------------------------------------------------------------------------------------#

class CSVPoser:
    ''' read and write csv files using dict-rows
    '''

    __slots__ = (
        '_input_filepath',
        '_input_file',
        '_input_args',

        '_output_filepath',
        '_output_file',
        '_output_args',

        '_header',
        '_reader',
        '_writer',
        '_overwrite',
        '_fieldmap',
        '_first_output',
        '_output_header',
    )
    def __init__(self, input_args, output_args, overwrite=False, fieldmap = None):
        ''''''

        ### parse input args
        if isinstance(input_args, (Path, str)):
            self._input_filepath     = Path(input_args)
            self._input_args         = dict()

        elif isinstance(input_args, dict):
            self._input_filepath     = Path(input_args['filepath'])
            self._input_args = {
                k:v for k,v
                in input_args.items()
                if k != 'filepath'
            }
        else:
            raise TypeError(input_args)

        ### parse output args
        if isinstance(output_args, (Path, str)):
            self._output_filepath    = Path(output_args)
            self._output_args        = dict()

        elif isinstance(output_args, dict):
            self._output_filepath   = Path(output_args['filepath'])
            self._output_args = {
                k:v for k,v
                in output_args.items()
                if k != 'filepath'
            }
        else:
            raise TypeError(input_args)
        self._output_args.setdefault('dialect', 'unix')

        ###
        self._input_file    = None
        self._output_file   = None
        self._reader        = None
        self._writer        = None
        self._header        = None
        self._overwrite     = overwrite
        self._fieldmap      = fieldmap
        self._first_output  = True
        self._output_header = None

    ################################
    def __enter__(self):

        if self._overwrite == False and self._output_filepath.exists():
            raise FileExistsError(self._output_filepath)

        self._input_file     = open(str(self._input_filepath), 'r')
        self._reader         = csv.reader(self._input_file,  **self._input_args)

        self._header         = next(self._reader)
        if self._fieldmap is not None:
            new_header      = list()
            for key in self._header:
                try:
                    newkey  = self._fieldmap[key]
                    new_header.append(newkey)
                except KeyError:
                    new_header.append(key)
            self._header = new_header

        return self


    ################################
    def __iter__(self):
        return self

    def __next__(self):
        line    = next(self._reader)
        row     = dict(zip(self._header, line))
        return row

    def write(self, row:dict):
        if self._first_output:
            self._output_file   = open(str(self._output_filepath), 'w')
            self._first_output  = False
            self._output_header = row.keys()
            self._writer        = csv.DictWriter(
                self._output_file,
                self._output_header,
                **self._output_args
            )
            self._writer.writeheader()

        self._writer.writerow(row)

    ################################
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._input_file.close()
        if self._output_file is not None:
            self._output_file.close()


#----------------------------------------------------------------------------------------------#
