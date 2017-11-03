import csv
from abc import ABCMeta, abstractproperty

from transactionpro.keyword_header_map import HEADER_MAP


class ImportType(object):
    """Base class for all TransactionPro import types."""
    __metaclass__ = ABCMeta

    def __init__(self):
        self._rows = []  # type: List[Dict[str, str]]

    @abstractproperty
    def fields(self):
        # type: () -> Tuple
        """Return tuple of valid kwarg parameters for add_row."""
        pass

    @abstractproperty
    def required_fields(self):
        # type: () -> Tuple
        """Return tuple of fields that must be in add_row;"""
        pass

    def add_row(self, **kwargs):
        """Add a row to the final csv. Must exist in self.field and must
        contain all self.required_fields."""
        for field in self.required_fields:
            if field not in kwargs:
                raise KeyError('Required field {} was not given'.format(field))
        for k in kwargs:
            if k not in self.fields:
                raise KeyError(
                    "Keyword argument {} doesn't exist in self.fields".format(
                        k)
                )
        self._rows.append(kwargs)

    def write_csv_to(self, fileobject):
        """Write csv to file-like object."""
        writer = csv.writer(fileobject)
        # write header
        writer.writerow([HEADER_MAP[field] for field in self.fields])

        # TODO: switch to generator for memory efficiency
        for row in self._rows:
            row_out = []
            for field in self.fields:
                if field in row:
                    row_out.append(row[field])
                else:
                    row_out.append('')
            writer.writerow(row_out)
