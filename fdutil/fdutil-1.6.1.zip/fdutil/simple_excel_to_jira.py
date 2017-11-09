# encoding : UTF-8

from pyperclip import copy, paste

__author__ = u'Hywel Thomas'
__copyright__ = u'Copyright (C) 2016 Hywel Thomas'


def make_jira_table_row(row,
                        header = False):
    delimiter = u'||' if header else u'|'
    return u"{delimiter}{row}{delimiter}".format(delimiter = delimiter,
                                                 row       = delimiter.join(row))


def excel_in_clipboard_to_jira_in_clipboard():
    excel = paste()

    rows = [row.split(u'\t') for row in excel.splitlines()]
    jira = [make_jira_table_row(header = True,
                                row    = rows.pop(0))]
    for row in rows:
       jira.append(make_jira_table_row(row = row))

       copy(u'\n'.join(jira))


excel_in_clipboard_to_jira_in_clipboard()
