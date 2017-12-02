"""
Helper functions for copying and pasting tables.
Handles junk data that may be appended at the end of Microsoft Excel
clipboard text.
"""
import threading

import pyperclip


__all__ = ['ClipboardValidationError', 'put_clipboard', 'get_clipboard'
           'get_table', 'put_table', 'parse_table_string']

_lock = threading.Lock()


# noinspection PyBroadException
def get_clipboard():
    with _lock:
        return pyperclip.paste()


def empty_clipboard():
    with _lock:
        pyperclip.copy('')


def put_clipboard(new):
    with _lock:
        pyperclip.copy(new)


def parse_table_string(string):
    """
    Convert string copied from excel into list of lists
    :param string:  Text copied from excel.
    :type string: str
    :return:
    :rtype:
    """
    formatted = _parse_valid_string(string)

    rows = formatted.splitlines()
    matrix = [row.split('\t') for row in rows]
    if not len(matrix):
        return

    _trim_empty_rows(matrix)
    _trim_empty_columns(matrix)
    new_matrix = _parse_valid_cells(matrix)
    return new_matrix


def get_table():
    """
    Parse clipboard text copied from excel and convert to list of lists.
    :return: list of lists
    """
    table_string = get_clipboard()
    return parse_table_string(table_string)


def put_table(matrix):
    """
    Convert iterable of iterables to string and add to clipboard
    :param matrix:
    :type matrix:
    :return:
    :rtype:
    """
    values = '\n'.join(['\t'.join(row) for row in matrix])
    put_clipboard(values)


class ClipboardValidationError(ValueError, pyperclip.PyperclipException):
    pass


def _parse_valid_string(formatted):
    formatted = formatted.encode('utf-8', "ignore")
    formatted = formatted.rstrip(b'\x00')
    formatted = formatted.decode('utf-8')
    if formatted is None or not ('\n' in formatted):
        raise ClipboardValidationError()
    formatted = formatted[:-2] if '\0' in formatted[:-2] else formatted
    return formatted


def _trim_empty_rows(matrix):
    # END AT 0 to avoid removing inner list.
    for i in range(len(matrix) - 1, 0, -1):
        row = matrix[i]
        if not any(row):
            del matrix[i]
        else:
            break


def _trim_empty_columns(matrix):
    if len(matrix):
        for i in range(len(matrix[0]) - 1, -1, -1):
            if not any([row[i] for row in matrix]):
                for row in matrix:
                    del row[i]
            else:
                break


def _parse_valid_cells(matrix):
    len_ = len(matrix[0])
    new_matrix = []
    for row in matrix:
        if not len(row) == len_:
            try:
                row[0].encode().decode('ascii')
            except UnicodeDecodeError:
                continue
            else:
                if not len(new_matrix) + 1 == len(matrix):
                    if '\x00' in row[0]:
                        continue
                    else:
                        raise ClipboardValidationError()
        else:
            new_matrix.append(row)
    return new_matrix
