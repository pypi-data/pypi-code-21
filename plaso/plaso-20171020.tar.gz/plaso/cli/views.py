# -*- coding: utf-8 -*-
"""The CLI view classes."""

from __future__ import unicode_literals

import abc

from plaso.lib import py2to3


class BaseTableView(object):
  """Class that implements the table view interface."""

  def __init__(self, column_names=None, title=None):
    """Initializes the table view object.

    Args:
      column_names (Optional[str]): column names.
      title (Optional[str]): title.
    """
    super(BaseTableView, self).__init__()
    self._columns = column_names or []
    self._number_of_columns = len(self._columns)
    self._rows = []
    self._title = title

  def AddRow(self, values):
    """Adds a row of values.

    Args:
      values (list[object]): values.

    Raises:
      ValueError: if the number of values is out of bounds.
    """
    if self._number_of_columns and len(values) != self._number_of_columns:
      raise ValueError('Number of values is out of bounds.')

    self._rows.append(values)

    if not self._number_of_columns:
      self._number_of_columns = len(values)

  @abc.abstractmethod
  def Write(self, output_writer):
    """Writes the table to the output writer.

    Args:
      output_writer (OutputWriter): output writer.
    """


class CLITableView(BaseTableView):
  """Class that implements a command line table view.

  Note that currently this table view does not support more than 2 columns.
  """

  # The maximum width of the table in number of characters.
  # The standard width of Windows cmd.exe is 80 characters.
  _MAXIMUM_WIDTH = 80

  _HEADER_FORMAT_STRING = '{{0:*^{0:d}}}\n'.format(_MAXIMUM_WIDTH)

  def __init__(self, column_names=None, title=None):
    """Initializes the command line table view object.

    Args:
      column_names (Optional[str]): column names.
      title (Optional[str]): title.
    """
    super(CLITableView, self).__init__(column_names=column_names, title=title)
    if self._columns:
      self._column_width = len(self._columns[0])
    else:
      self._column_width = 0

  def _WriteRow(self, output_writer, values):
    """Writes a row of values aligned to the column width.

    Args:
      output_writer (OutputWriter): output writer.
      values (list[object]): values.
    """
    maximum_row_width = self._MAXIMUM_WIDTH - self._column_width - 3

    # The format string of the first line of the column value.
    primary_format_string = '{{0:>{0:d}s}} : {{1:s}}\n'.format(
        self._column_width)

    # The format string of successive lines of the column value.
    secondary_format_string = '{{0:<{0:d}s}}{{1:s}}\n'.format(
        self._column_width + 3)

    if isinstance(values[1], py2to3.STRING_TYPES):
      value_string = values[1]
    else:
      value_string = '{0!s}'.format(values[1])

    if len(value_string) < maximum_row_width:
      output_writer.Write(primary_format_string.format(
          values[0], value_string))
      return

    # Split the column value in words.
    words = value_string.split()

    current = 0

    lines = []
    word_buffer = []
    for word in words:
      current += len(word) + 1
      if current >= maximum_row_width:
        current = len(word)
        lines.append(' '.join(word_buffer))
        word_buffer = [word]
      else:
        word_buffer.append(word)
    lines.append(' '.join(word_buffer))

    # Split the column value across multiple lines.
    output_writer.Write(
        primary_format_string.format(values[0], lines[0]))
    for line in lines[1:]:
      output_writer.Write(secondary_format_string.format('', line))

  def _WriteSeparatorLine(self, output_writer):
    """Writes a separator line.

    Args:
      output_writer (OutputWriter): output writer.
    """
    output_writer.Write('-' * self._MAXIMUM_WIDTH)
    output_writer.Write('\n')

  def AddRow(self, values):
    """Adds a row of values.

    Args:
      values (list[object]): values.

    Raises:
      ValueError: if the number of values is out of bounds.
    """
    super(CLITableView, self).AddRow(values)

    value_length = len(values[0])
    if value_length > self._column_width:
      self._column_width = value_length

  def Write(self, output_writer):
    """Writes the table to the output writer.

    Args:
      output_writer (OutputWriter): output writer.

    Raises:
      RuntimeError: if the title exceeds the maximum width or
                    if the table has more than 2 columns or
                    if the column width is out of bounds.
    """
    if self._title and len(self._title) > self._MAXIMUM_WIDTH:
      raise RuntimeError('Title length out of bounds.')

    if self._number_of_columns not in (0, 2):
      raise RuntimeError('Unsupported number of columns: {0:d}.'.format(
          self._number_of_columns))

    if self._column_width < 0 or self._column_width >= self._MAXIMUM_WIDTH:
      raise RuntimeError('Column width out of bounds.')

    output_writer.Write('\n')

    if self._title:
      header_string = ' {0:s} '.format(self._title)
    else:
      header_string = ''
    header_string = self._HEADER_FORMAT_STRING.format(header_string)
    output_writer.Write(header_string)

    if self._columns:
      self._WriteRow(output_writer, self._columns)
      self._WriteSeparatorLine(output_writer)

    for values in self._rows:
      self._WriteRow(output_writer, values)

    self._WriteSeparatorLine(output_writer)


class MarkdownTableView(BaseTableView):
  """Class that implements a Markdown table view."""

  def Write(self, output_writer):
    """Writes the table to the output writer.

    Args:
      output_writer (OutputWriter): output writer.
    """
    if self._title:
      output_writer.Write('### {0:s}\n\n'.format(self._title))

    if not self._columns:
      self._columns = ['' for _ in range(0, self._number_of_columns)]

    output_writer.Write(' | '.join(self._columns))
    output_writer.Write('\n')

    output_writer.Write(' | '.join(['---' for _ in self._columns]))
    output_writer.Write('\n')

    for values in self._rows:
      values = ['{0!s}'.format(value) for value in values]
      output_writer.Write(' | '.join(values))
      output_writer.Write('\n')

    output_writer.Write('\n')


class ViewsFactory(object):
  """Class that implements the views factory."""

  FORMAT_TYPE_CLI = 'cli'
  FORMAT_TYPE_MARKDOWN = 'markdown'

  _TABLE_VIEW_FORMAT_CLASSES = {
      FORMAT_TYPE_CLI: CLITableView,
      FORMAT_TYPE_MARKDOWN: MarkdownTableView
  }

  @classmethod
  def GetTableView(cls, format_type, column_names=None, title=None):
    """Retrieves a table view.

    Args:
      format_type (str): table view format type.
      column_names (Optional[str]): column names.
      title (Optional[str]): title.

    Returns:
      BaseTableView: table view.
    """
    view_class = cls._TABLE_VIEW_FORMAT_CLASSES.get(format_type, None)
    if not view_class:
      raise ValueError('Unsupported format type: {0:s}'.format(format_type))

    return view_class(column_names=column_names, title=title)
