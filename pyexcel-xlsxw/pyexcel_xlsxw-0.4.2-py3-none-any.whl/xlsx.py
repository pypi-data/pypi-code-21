"""
    pyexcel_xlsxw
    ~~~~~~~~~~~~~~~~~~~

    The lower level xlsx file format writer using xlsxwriter

    :copyright: (c) 2016 by Onni Software Ltd & its contributors
    :license: New BSD License
"""
from pyexcel.renderer import Renderer
import pyexcel_io.constants as constants
from pyexcel_io._compact import isstream
from pyexcel_io._compact import BytesIO
import xlsxwriter


class SheetWriter(object):
    """
    Generic sheet writer
    """

    def __init__(self, native_book, native_sheet, name, **keywords):
        if name:
            sheet_name = name
        else:
            sheet_name = constants.DEFAULT_SHEET_NAME
        self._native_book = native_book
        self._native_sheet = native_sheet
        self._keywords = keywords
        self.set_sheet_name(sheet_name)

    def set_sheet_name(self, name):
        """
        Set sheet name
        """
        pass

    def write_row(self, array):
        """
        write a row into the file
        """
        raise NotImplementedError("Please implement write_row()")

    def write_array(self, table):
        """
        For standalone usage, write an array
        """
        for row in table:
            self.write_row(row)

    def close(self):
        """
        This call actually save the file
        """
        pass


class BookWriter:
    """
    Standard book writer
    """
    def __init__(self):
        self._file_alike_object = None
        self._keywords = None

    def open(self, file_name, **keywords):
        """
        open a file with unlimited keywords for writing

        keywords are passed on to individual writers
        """
        self._file_alike_object = file_name
        self._keywords = keywords

    def open_stream(self, file_stream, **keywords):
        """
        open a file stream with unlimited keywords for writing

        keywords are passed on to individual writers
        """
        if not isstream(file_stream):
            raise IOError()
        self.open(file_stream, **keywords)

    def write(self, incoming_dict):
        for sheet_name in incoming_dict:
            sheet_writer = self.create_sheet(sheet_name)
            if sheet_writer:
                sheet_writer.write_array(incoming_dict[sheet_name])
                sheet_writer.close()

    def create_sheet(self, sheet_name):
        """
        implement this method for easy extension
        """
        raise NotImplementedError("Please implement create_sheet()")


class XLSXSheetWriter(SheetWriter):
    """
    xlsx and xlsm sheet writer
    """
    def set_sheet_name(self, name):
        self.current_row = 0

    def write_row(self, array):
        """
        write a row into the file
        """
        for i in range(0, len(array)):
            self._native_sheet.write(self.current_row, i, array[i])
        self.current_row += 1


class XLSXWriter(BookWriter):
    """
    xlsx and xlsm writer
    """
    def __init__(self):
        BookWriter.__init__(self)
        self._native_book = None

    def open(self, file_name, **keywords):
        """
        Open a file for writing

        Please note that this writer configure xlsxwriter's BookWriter to use
        constant_memory by default.

        :param keywords: **default_date_format** control the date time format.
                         **constant_memory** if true, reduces the memory
                         footprint when writing large files. Other parameters
                         can be found in `xlsxwriter's documentation
                         <http://xlsxwriter.readthedocs.io/workbook.html>`_
        """
        keywords.setdefault('default_date_format', 'dd/mm/yy')
        keywords.setdefault('constant_memory', True)
        BookWriter.open(self, file_name, **keywords)

        self._native_book = xlsxwriter.Workbook(
            file_name, keywords
         )

    def create_sheet(self, name):
        return XLSXSheetWriter(self._native_book,
                               self._native_book.add_worksheet(name), name)

    def close(self):
        """
        This call actually save the file
        """
        self._native_book.close()


class XlsxRenderer(Renderer):
    file_types = ['xlsx']

    def get_io(self):
        return BytesIO()

    def render_sheet_to_file(self, file_name, sheet, **keywords):
        sheet_name = constants.DEFAULT_SHEET_NAME
        if sheet.name:
            sheet_name = sheet.name
        data = {sheet_name: sheet.to_array()}
        writer = XLSXWriter()
        writer.open(file_name)
        writer.write(data)
        writer.close()

    def render_book_to_file(self, file_name, book, **keywords):
        writer = XLSXWriter()
        writer.open(file_name)
        writer.write(book.to_dict())
        writer.close()

    def render_sheet_to_stream(self, file_stream, sheet, **keywords):
        sheet_name = constants.DEFAULT_SHEET_NAME
        if sheet.name:
            sheet_name = sheet.name
        data = {sheet_name: sheet.to_array()}
        writer = XLSXWriter()
        writer.open_stream(file_stream)
        writer.write(data)
        writer.close()

    def render_book_to_stream(self, file_stream, book, **keywords):
        writer = XLSXWriter()
        writer.open_stream(file_stream)
        writer.write(book.to_dict())
        writer.close()
