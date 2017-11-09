# -*- coding: utf-8 -*-

import codecs
from uuid import uuid4
from warnings import warn
from dominate import tags
from collections import OrderedDict

import logging_helper
from fdutil.type_check import (is_dictionary,
                               is_list,
                               is_list_or_dictionary,
                               is_list_of_dictionaries)
from fdutil.string_tools import make_multi_line_conversion
from fdutil.html import CSS_DIV_ID, SCRIPTS_DIV_ID, uglify_script_or_css
from .row import Row, ROW_NUMBER_HEADING
from .cell import Cell
from .helpers import (table_format_string_to_table_format_dictionary,
                      make_index_headings)
from .constants import (TableSeparators,
                        Justify,
                        CLASSES,
                        HEADING,
                        JUSTIFY,
                        KEY,
                        VALUE,
                        DUMMY,
                        DUMMY_HEADINGS,
                        KEY_VALUE_HEADINGS)
from .table_html import TABLE_CSS
from fdutil.html import (escape_html_text,
                         write_to_html,
                         generate_html_document)

logging = logging_helper.setup_logging()

JIRA_LOGO = u'https://www.atlassian.com/dam/jcr:e33efd9e-e0b8-4d61-a24d-68a48ef99ed5/jirasoftware_rgb_slate.png'


class TableInitMixin(object):

    # Import
    @staticmethod
    def init_from_tree__root_dictionary(tree,
                                        title,
                                        level,
                                        conversions,
                                        table_format):

        table = Table(title=title,
                      headings=KEY_VALUE_HEADINGS,
                      row_numbers=False,
                      conversions=conversions,
                      table_format=table_format,
                      show_column_headings=False)

        # Currently do complex conversionutil here, but may may more sense to do it
        # a row level.
        complex_conversions = [key for key in conversions if is_list_or_dictionary(key)]

        for complex_conversion in complex_conversions:
            if len([True for key in complex_conversion if key in tree]) == len(complex_conversion):
                values = list(conversions[complex_conversion][u'converter'](*[tree[key] for key in complex_conversion]))

                for key in complex_conversion:
                    tree[key] = values.pop(0)

        for field in tree:
            table.add_row({KEY:   field,
                           VALUE: Table.init_from_tree(tree=tree[field],
                                                       level=level + 1,
                                                       field_name=field,
                                                       conversions=conversions,
                                                       table_format=table_format)})

        return table

    @staticmethod
    def init_from_tree__dictionary(tree,
                                   level,
                                   conversions,
                                   table_format):

        if not tree:
            return None  # Empty dict

        headings = {}

        for field in tree:
            headings[field] = None

        table = Table(headings=[{u'heading': heading} for heading in headings],
                      row_numbers=False,
                      conversions=conversions,
                      table_format=table_format)

        complex_conversions = [key
                               for key in conversions
                               if is_list_or_dictionary(key)]

        for complex_conversion in complex_conversions:
            # TODO: Add an explanation of this!
            if len([True for key in complex_conversion
                    if key in tree]) == len(complex_conversion):
                values = list(conversions[complex_conversion][u'converter'](*[tree[key]
                                                                              for key in complex_conversion]))

                for key in complex_conversion:
                    tree[key] = values.pop(0)

        row = {}

        for field in tree:
            row[field] = Table.init_from_tree(tree=tree[field],
                                              level=level + 1,
                                              conversions=conversions,
                                              table_format=table_format)

        table.add_row(row)

        return table

    @staticmethod
    def init_from_tree__dictionaries(tree,
                                     level,
                                     conversions,
                                     table_format,
                                     title=None,
                                     row_numbers=True):

        # If these are highly amorphous dictionaries, it's going to get interesting!
        # Get ALL the keys!
        headings = OrderedDict()

        for record in tree:
            for field in record:
                headings[field] = None

        table = Table(title=title,
                      headings=[{u'heading': heading}
                                for heading in headings],
                      row_numbers=row_numbers,
                      conversions=conversions,
                      table_format=table_format)

        for record in tree:
            row = {}

            for field in headings:
                row[field] = u'-'

            for field_name in record:
                row[field_name] = Table.init_from_tree(tree=record[field_name],
                                                       level=level + 1,
                                                       field_name=field_name,
                                                       conversions=conversions,
                                                       table_format=table_format)

            table.add_row(row)

        return table

    @staticmethod
    def init_from_tree__list(tree,
                             level,
                             conversions,
                             table_format,
                             title=None):

        table = Table(title=title,
                      headings=DUMMY_HEADINGS,
                      row_numbers=False,
                      conversions=conversions,
                      table_format=table_format,
                      show_column_headings=False)

        for record in tree:
            table.add_row({DUMMY: Table.init_from_tree(tree=record,
                                                       level=level + 1,
                                                       conversions=conversions,
                                                       table_format=table_format)})

        return table

    @staticmethod
    def init_from_tree(tree,
                       title=None,
                       level=0,
                       field_name=None,
                       conversions=None,
                       row_numbers=True,
                       table_format=None):

        """

        :rtype: object
        """

        conversions = conversions if conversions else {}

        if isinstance(tree, Cell):
            # We've reached a leaf node that has already been processed. Return it.
            return tree

        elif is_dictionary(tree):
            if level == 0:
                return Table.init_from_tree__root_dictionary(tree=tree,
                                                             title=title,
                                                             level=level,
                                                             conversions=conversions,
                                                             table_format=table_format)

            else:
                return Table.init_from_tree__dictionary(tree=tree,
                                                        level=level,
                                                        conversions=conversions,
                                                        table_format=table_format)

        elif is_list(tree):
            if is_list_of_dictionaries(tree):
                return Table.init_from_tree__dictionaries(tree=tree,
                                                          title=title if level == 0 else None,
                                                          level=level,
                                                          conversions=conversions,
                                                          row_numbers=row_numbers,
                                                          table_format=table_format)

            else:
                return Table.init_from_tree__list(tree=tree,
                                                  level=level,
                                                  title=title if level == 0 else None,
                                                  conversions=conversions,
                                                  table_format=table_format)

        else:
            # Not a cell, not a dictionary, not a list,
            # it must be a unprocessed leaf.
            return Cell(value=u'-' if tree is None else tree,
                        conversion=None if not conversions else conversions.get(field_name))

    @staticmethod
    def init_from_text(text,
                       conversions=None,
                       table_format=None):

        def is_horizontal_separator_line(line):
            h = table_format[TableSeparators.horizontal]
            v = table_format[TableSeparators.vertical]
            i = table_format[TableSeparators.intersection]

            just_horizontals = line.strip().replace(v, h).replace(i, h)

            return len(just_horizontals) * h == just_horizontals

        lines = [line.strip() for line in text.strip().splitlines()]

        if is_horizontal_separator_line(lines[-1]):
            lines.pop()

        if is_horizontal_separator_line(lines[0]):
            lines.pop(0)

        rows = []

        while not is_horizontal_separator_line(lines[-1]):
            line = lines.pop()

            if line[0] == line[-1] == table_format[TableSeparators.vertical]:
                line = line[1:-1]

            rows.append([part.strip() for part in line.split(table_format[TableSeparators.vertical])])

        rows.reverse()

        lines.pop()

        header_lines = []

        while lines and not is_horizontal_separator_line(lines[-1]):
            line = lines.pop()

            if line[0] == line[-1] == table_format[TableSeparators.vertical]:
                line = line[1:-1]

            header_lines.append(line.split(table_format[TableSeparators.vertical]))

        lines.pop()

        headings = []

        for heading in range(len(header_lines[0])):
            heading_parts = u'\n'.join([header_line[heading].strip() for header_line in reversed(header_lines)])
            headings.append(heading_parts.strip())

        title_lines = []

        while lines and not is_horizontal_separator_line(lines[-1]):
            line = lines.pop()

            if line[0] == line[-1] == table_format[TableSeparators.vertical]:
                line = line[1:-1]

            title_lines.append(line.strip())

        title_lines.reverse()
        title = (u'\n'.join(title_lines)).strip()

        row_numbers = headings[0] == ROW_NUMBER_HEADING

        if row_numbers:
            headings.pop(0)

            for row in rows:
                row.pop(0)

        table = Table(title=title if title else None,
                      headings=[{u'heading': heading}
                                for heading in headings],
                      row_numbers=row_numbers,
                      conversions=conversions,
                      table_format=table_format)

        for row in rows:
            table.add_row(row)

        return table

    @staticmethod
    def init_from_file(filename,
                       conversions=None):
        return Table.init_from_text(codecs.open(filename, u'r', encoding=u'utf8').read(),
                                    conversions=conversions)

    @staticmethod
    def init_from_pasted_excel(pasted_excel,
                               row_numbers=False):
        rows = [row.split() for row in pasted_excel.splitlines()]

        table = Table(headings=[{u'heading':       heading,
                                 u'justification': u'^'}
                                for heading in rows.pop(0)],
                      row_numbers=row_numbers)

        for _ in rows:
            table.add_row(rows.pop(0))

        return table

    @staticmethod
    def init_as_grid(values,
                     title=None,
                     columns=3,
                     max_cell_width=None,
                     unfilled=u'-',
                     justify=Justify.center):

        rows = []
        detected_lists = None

        for value in values:
            if isinstance(value, list) or isinstance(value, tuple):
                if detected_lists in (None, True):
                    detected_lists = True

                else:
                    raise ValueError(u'Cannot mix values and lists:{value}'.format(value=value))

                # value is a row
                if len(value) <= columns:
                    row = [unfilled for _ in range(columns)]

                    for i, cell in enumerate(value):
                        row[i] = cell

                    rows.append(row)

                else:
                    raise ValueError(u'Too many columns in row:{value}'.format(value=value))

            else:
                if detected_lists is True:
                    raise ValueError(u'Cannot mix values and lists:{value}'.format(value=value))

        if not detected_lists:

            # Just a flat list. sort into rows
            rows = []
            column = 0

            while values:
                if column == 0:
                    try:
                        rows.append(row)
                        del row
                    except NameError:
                        pass

                value = values.pop(0)
                try:
                    row
                except NameError:
                    row = {column: unfilled for column in range(columns)}
                finally:
                    row[column] = value

                column = (column + 1) % columns

            try:
                rows.append(row)
            except NameError:
                    pass

        conversions = (None if not max_cell_width
                       else {column: make_multi_line_conversion(max_cell_width)
                             for column in range(columns)})

        return Table(title=title,
                     headings=make_index_headings(width=columns,
                                                  justification=justify),
                     show_column_headings=False,
                     row_numbers=False,
                     rows=rows,
                     show_separators=True,
                     conversions=conversions)


class Table(TableInitMixin):
    LIGHT_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u"┌─┬┐"
        u"│ ││"
        u"├─┼┤"
        u"└─┴┘"
    )

    ROUNDED_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u"╭─┬╮"
        u"│ ││"
        u"├─┼┤"
        u"╰─┴╯"
    )

    DOUBLE_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u"╔═╦╗"
        u"║ ║║"
        u"╠═╬╣"
        u"╚═╩╝"
    )

    TEXT_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u" -- "
        u"| ||"
        u"|-+|"
        u" -- "
    )

    TSV_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u"  \t "
        u"  \t "
        u"  \t "
        u"  \t "
    )

    CSV_TABLE_FORMAT = table_format_string_to_table_format_dictionary(
        u"  , "
        u"  , "
        u"  , "
        u"  , "
    )

    SCRIPTS = []

    INLINE_SCRIPTS = []

    CSS = []

    INLINE_CSS = [
        TABLE_CSS
    ]

    def __init__(self,
                 headings,
                 rows=None,
                 title=None,
                 row_numbers=True,
                 start_row_number=1,
                 conversions=None,
                 table_format=None,
                 show_separators=False,
                 show_summaries=False,
                 show_column_headings=True,
                 empty_table_indication=u'Empty'):

        """
        TODO: Flesh this out

        :param headings: list of dicts:
                         dict: {HEADING: text or Cell,
                                MAX:     maximum width for the column
                                JUSTIFY: one of LEFT_JUSTIFY (default)
                                                CENTRE_JUSTIFY
                                                CENTER_JUSTIFY
                                                RIGHT_JUSTIFY
        :param rows:
        :param title: text or Cell: Title of table. Spans all columns
        :param row_numbers: bool: Show or hide row numbers. Defauls
        :param conversions:
        :param table_format: string: Defines the characters used for text
                                     formatting. See examples above.
        :param show_separators: bool
        :param show_summaries: bool
        :param show_column_headings: bool
        :param empty_table_indication: text or Cell to show if there are no
                                       rows
        """

        # If row_numbers are enabled we will enable the row number column
        if row_numbers:
            headings = [heading for heading in headings]  # Copy so changes don't affect original list
            headings.insert(0, {HEADING: ROW_NUMBER_HEADING})

        self.conversions = {} if conversions is None else conversions
        self.justifications = [heading.get(JUSTIFY, Justify.left) for heading in headings]

        self.heading_classes = [heading.get(CLASSES, []) for heading in headings]

        self.headings = OrderedDict([(heading[HEADING], Cell(heading[HEADING])) for heading in headings])

        self._title = title if isinstance(title, Cell) else Cell(title)

        self.suppress_empty_table_indication = empty_table_indication is None
        self.empty_table_indication = Cell(empty_table_indication)
        self.show_column_headings = show_column_headings
        self.show_separators = show_separators
        self.summaries = Row(headings=self.headings.keys(),
                             row={key: u'' for key in self.headings.keys()}) if show_summaries else None
        self.rows = []
        self.start_row_number = start_row_number
        self._row_count = self.start_row_number
        self.set_table_format(table_format)

        if rows:
            self.add_rows(rows)

    def __len__(self):
        return len(unicode(self).split(u'\n'))

    def __getitem__(self, item):
        return self.rows[item]

    def __setitem__(self, item, value):

        if isinstance(value, Row):
            self.rows[item] = value

        else:
            raise ValueError(u'{v} is not an instance of tableutil.Row'.format(v=value))

    def __unicode__(self):
        return self.text()

    # Modification
    @property
    def title(self):
        return self._title.raw_value

    @title.setter
    def title(self,
              title):
        self._title = Cell(title)

    @property
    def num_cols(self):
        return len(self.headings)

    def update_empty_table_indication(self,
                                      empty_table_indication):
        self.empty_table_indication = Cell(empty_table_indication)

    def add_row(self,
                row,
                classes=None):

        """ Add a row to the table.

        :param row:     Can either be a tableutil.Row object or a dict - { heading: cell }
                        If a dict it can also contain one additional parameter: _classes.  This allows
                        a list of classes to be specified that will be added to the row for HTML output.
        :param classes: Default: None.  a list of classes to be specified that will be added to the
                        row for HTML output. Note: only applies to rows supplied as a dict.
        """

        if isinstance(row, Row):
            row.row_number = self._row_count
            self.rows.append(row)

        else:
            if u'_classes' in row:
                class_list = row.get(u'_classes', [])

                if classes is not None:
                    classes = classes + class_list

                else:
                    classes = class_list

            self.rows.append(Row(headings=self.headings.keys(),
                                 row=row,
                                 row_number=self._row_count,
                                 classes=classes,
                                 conversions=self.conversions))

        self._row_count += 1

    def add_rows(self,
                 rows):
        for row in rows:
            self.add_row(row)

    def add_summary(self,
                    heading,
                    value):
        try:
            self.summaries[heading].value = value
        except KeyError as ke:
            logging.warning(unicode(ke))

    def add_summaries(self,
                      summaries):
        for heading, summary in iter(summaries.items()):  # Prioritises Py3
            self.add_summary(heading=heading,
                             value=summary)

    def sort_by_column(self,
                       column,
                       ascending=True):
        self.rows = sorted(self.rows,
                           key=lambda k: k[column].value,
                           reverse=not ascending)
        self.update_row_numbers()

    def update_row_numbers(self):

        self._row_count = self.start_row_number

        for row in self.rows:
            row.row_number = self._row_count
            self._row_count += 1

    def set_table_format(self,
                         table_format=None):
        if table_format is None:
            table_format = Table.LIGHT_TABLE_FORMAT

        elif not is_dictionary(table_format):
            table_format = table_format_string_to_table_format_dictionary(table_format)

        self.table_format = table_format
        # TODO: Propagate to sub-tables.

    # Export to HTML
    def write_to_html(self,
                      sort_column=None,
                      sort_ascending=True,
                      filename=None,
                      html_folder=None,
                      filehandle=None,
                      jira_helper=True,
                      text_helper=True,
                      open_in_browser=False):

        doc = generate_html_document(title=self.title)

        with doc.getElementById(CSS_DIV_ID):
            if bool(self.CSS):
                for style in self.CSS:
                    tags.link(rel=u'stylesheet', href=style)

            if bool(self.INLINE_CSS):
                for style in self.INLINE_CSS:
                    tags.style(uglify_script_or_css(style))

        with doc.getElementById(SCRIPTS_DIV_ID):
            if bool(self.SCRIPTS):
                for script in self.SCRIPTS:
                    tags.script(type=u'text/javascript', src=script)

            if bool(self.INLINE_SCRIPTS):
                for script in self.INLINE_SCRIPTS:
                    tags.script(uglify_script_or_css(script))

        with doc:
            self.html(sort_column=sort_column,
                      sort_ascending=sort_ascending,
                      jira_helper=jira_helper,
                      text_helper=text_helper)

        return write_to_html(html_document=doc,
                             filename=filename,
                             html_folder=html_folder,
                             filehandle=filehandle,
                             open_in_browser=open_in_browser)

    def log_and_write_to_html(self,
                              filename=None,
                              html_folder=None,
                              filehandle=None,
                              jira_helper=True,
                              text_helper=True,
                              open_in_browser=False,
                              level=logging_helper.DEBUG):

        logging.log(level=level,
                    msg=u'\n' + unicode(self))

        return self.write_to_html(filename=filename,
                                  html_folder=html_folder,
                                  filehandle=filehandle,
                                  jira_helper=jira_helper,
                                  text_helper=text_helper,
                                  open_in_browser=open_in_browser)

    def html(self,
             sort_column=None,
             sort_ascending=True,
             jira_helper=True,
             text_helper=True):  # -> Table (Add type hint when we move to 3.6)

        helper_kwargs = {u'jira_helper': jira_helper,
                         u'text_helper': text_helper}

        if sort_column is not None:
            self.sort_by_column(column=sort_column,
                                ascending=sort_ascending)

        # TODO: Add styles
        # pdb.set_trace()

        table_div_id = uuid4()
        table_id = uuid4()

        _table_col_div = tags.div(_class=u'col')
        _table_div = tags.div(tags.div(_table_col_div,
                                       _class=u'row justify-content-center'),
                              id=table_div_id,
                              _class=u'container-fluid')

        table_kwargs = {
            u'id': table_id,
            u'cellspacing': u'0',
            u'_class': u'table table-bordered table-hover table-responsive table-sm'
        }

        with _table_col_div:

            tags.br()

            self._html_table_popover(text=text_helper,
                                     jira=jira_helper,
                                     table_kwargs=table_kwargs)

            _table = tags.table(**table_kwargs)

            number_of_columns = len(self.headings) if self.rows else 1

            if self.title or (self.rows and self.show_column_headings):

                # Add table header
                _thead = _table.add(tags.thead(_class=u'table-dark sticky-top'))

                with _thead:
                    if self.title:
                        _tr__head_title = tags.tr()
                        _tr__head_title.add(tags.th(self._title.html(**helper_kwargs),
                                                    colspan=number_of_columns))

                    if self.rows and self.show_column_headings:
                        headers = self.headings.values()

                        _tr__head_col_headings = tags.tr()

                        for idx, heading in enumerate(headers):
                            _tr__head_col_headings.add(tags.th(heading.html(**helper_kwargs),
                                                               _class=u' '.join(self.heading_classes[idx])))

            # Add table body
            _tbody = _table.add(tags.tbody())

            with _tbody:
                if self.rows:
                    for row in self.rows:
                        row.html(**helper_kwargs)

                else:
                    if not self.suppress_empty_table_indication:
                        _tr__body_row = tags.tr()
                        _tr__body_row.add(tags.td(self.empty_table_indication.html(**helper_kwargs),
                                                  colspan=number_of_columns))

            if self.rows and self.summaries:

                if not self.summaries.is_empty:
                    # Add table footer
                    _tfoot = _table.add(tags.tfoot(_class=u'table-secondary'))

                    with _tfoot:
                        self.summaries.html(**helper_kwargs)

        return _table_div

    def _html_table_popover(self,
                            table_kwargs,
                            text=True,
                            jira=True):
        """

        :param table_kwargs:
        :param text: False: Does not add text to exports
                     True: Adds text representation of this table to the exports
                     String: Adds the string as the text used in export.
                             (Allows for customisation)
        :param jira: False: Does not add jira to exports
                     True: Adds JIRA representation of this table to the exports
                     String: Adds the string as the text used in export.
                             (Allows for customisation)
        :return:
        """

        # TODO: this may have to be converted back from a popover, perhaps into an extra footer row?

        if text or jira:
            # Add popover kwargs to
            table_kwargs.update({
                u'data_toggle': u'popover',
                u'data_html': u'true',
                u'data_placement': u'bottom',
                u'data_original_title': u'Click to export to:'
            })

            popover_div_id = uuid4()

            tags.script(u"clickable_popover('{table_id}', '{popover_id}');".format(table_id=table_kwargs.get(u'id'),
                                                                                   popover_id=popover_div_id))

            _popover_div = tags.div(id=popover_div_id,
                                    style=u'display: none;')

            with _popover_div:
                title = self.title[0] if type(self.title) is list else self.title

                if jira:
                    escaped_jira = escape_html_text(self.jira() if jira is True else jira)

                    tags.a(tags.img(border=0,
                                    alt=u'Jira',
                                    width=100,
                                    src=JIRA_LOGO),
                           href=u'javascript:open_document(\'<pre>{jira}</pre>\', '
                                u'\'Jira ({title})\')'.format(jira=escaped_jira,
                                                              title=title))
                    tags.br()

                if text:
                    escaped_text = escape_html_text(unicode(self) if text is True else text)
                    tags.a(u'Formatted Text',
                           href=u'javascript:open_document(\'<pre>{text}</pre>\', '
                                u'\'Text ({title})\')'.format(text=escaped_text,
                                                              title=title))
                    tags.br()

    # Export to Jira
    def jira(self,
             sort_column=None,
             sort_ascending=True):

        if sort_column is not None:
            self.sort_by_column(column=sort_column,
                                ascending=sort_ascending)

        # TODO: Add styles
        table_lines = []

        if self.title:
            table_lines.append(u'|| {value} ||\n'.format(value=self._title.jira()))

        if self.rows:
            if self.show_column_headings:
                headers = self.headings.values()

                table_lines.append(u'|| {headers} ||'.format(headers=u' || '.join([heading.jira()
                                                                                   for heading in headers])))

            for row in self.rows:
                table_lines.append(row.jira())

            if self.rows and self.summaries:
                if not self.summaries.is_empty:
                    table_lines.append(self.summaries.jira())

        else:
            if not self.suppress_empty_table_indication:
                table_lines.append(u'| {eti} |'.format(eti=self.empty_table_indication.jira()))

        return u'\n'.join(table_lines)

    # Export to Text
    def write_to_textfile(self,
                          filepath):
        with codecs.open(filepath, u'w', encoding=u'utf8') as f:
            f.write(unicode(self))

    def row_cell_text_widths(self):
        heading_widths = {heading: value.width for heading, value in iter(self.headings.items())}  # Prioritises Py3

        if self.rows:
            row_widths = [row.cell_widths for row in self.rows]
            row_widths.append(heading_widths)

            if self.summaries is not None:
                row_widths.append(self.summaries.cell_widths)

            max_widths = [max([r[heading] for r in row_widths]) for heading in self.headings.keys()]

        else:
            max_widths = [headings.width for headings in self.headings.values()]

        return max_widths

    def text_width(self):

        title_width = max([len(title_line) for title_line in self._title.text()]) if self._title else 0

        row_width = ((sum(self.row_cell_text_widths()) if self.rows else self.empty_table_indication.width)  # Content
                     + (self.num_cols - (0 if self.num_cols == 0 else 1)))                                   # Col divs

        return title_width if title_width >= row_width else row_width

    def as_text(self,
                *args,
                **kwargs):
        warn(u'Table.as_text is deprecated, please use table.text instead.')
        return self.text(*args, **kwargs)

    def text(self,
             show_title=True,
             table_format=None,
             solid_borders=True,
             sort_column=None,
             sort_ascending=True):

        def _formatted_row(widths,
                           strings,
                           justifications=None,
                           sep=self.table_format[TableSeparators.vertical]):

            if justifications is None:
                justifications = [Justify.left for _ in range(len(widths))]

            row_parts = []

            for (string,
                 width,
                 justification) in zip(strings,
                                       [width for width in widths],
                                       justifications):
                row_parts.append((u'{string:'
                                  u'{fill}{justification}{width}}'.format(string=string,
                                                                          fill=self.table_format[TableSeparators.space],
                                                                          width=width,
                                                                          justification=justification)))

            return sep.join(row_parts)

        def _formatted_rows(widths,
                            cells,
                            justifications=None):

            row_parts = []

            for sub_row in range(max([len(cell) for cell in cells])):
                row_parts.append(
                    _formatted_row(
                        widths=widths,
                        strings=[cell[sub_row] for cell in cells],
                        justifications=justifications))

            return row_parts

        # text body

        if table_format is not None:
            self.set_table_format(table_format)

        table_lines = []

        # Sorting
        if sort_column is not None:
            self.sort_by_column(column=sort_column,
                                ascending=sort_ascending)

        widths = self.row_cell_text_widths()

        text_width = self.text_width()

        # if we need to pad out the rows to match the
        # width of the title, distribute required spaces
        # equally to all columns
        padding = text_width - (sum(widths) + len(widths) - 1)
        if padding > 0:
            col = 0
            while padding:
                padding -= 1
                widths[col] += 1
                col = (col + 1) % len(widths)

        # Outer Borders
        horizontal_outer_border = self.table_format[TableSeparators.horizontal] * text_width

        top_col_border = _formatted_row(widths=widths,
                                        strings=[self.table_format[TableSeparators.horizontal] * width
                                                 for width in widths],
                                        sep=self.table_format[TableSeparators.horizontal_down]
                                        if self.rows
                                        else self.table_format[TableSeparators.horizontal])

        bottom_col_border = _formatted_row(widths=widths,
                                           strings=[self.table_format[TableSeparators.horizontal] * width
                                                    for width in widths],
                                           sep=self.table_format[TableSeparators.horizontal_up]
                                           if self.rows
                                           else self.table_format[TableSeparators.horizontal])

        separator = _formatted_row(widths=widths,
                                   strings=[self.table_format[TableSeparators.horizontal] * width
                                            for width in widths],
                                   sep=self.table_format[TableSeparators.intersection])

        if self.title and show_title:
            for title_line in self._title.text():
                table_lines.append(u'{title_line:^{width}}'.format(title_line=title_line,
                                                                   width=text_width))
            table_lines.append(top_col_border if self.rows else horizontal_outer_border)

        if self.rows:
            if self.show_column_headings:
                headers = self.headings.values()

                header = _formatted_rows(
                        widths=widths,
                        cells=headers,
                        justifications=[Justify.center for _ in range(len(self.justifications))])
                table_lines.extend(header)
                table_lines.append(separator)

            for row in self.rows:
                table_lines.extend(row.text(widths=widths,
                                            justifications=self.justifications,
                                            divider=self.table_format[TableSeparators.vertical]))

                if self.show_separators and row != self.rows[-1]:
                    table_lines.append(separator)

            if self.rows and self.summaries:
                if not self.summaries.is_empty:
                    table_lines.append(separator)
                    table_lines.extend(self.summaries.text(widths=widths,
                                                           divider=self.table_format[TableSeparators.vertical]))

        else:
            # Handle empty table
            if not self.suppress_empty_table_indication:
                table_lines.extend(
                    _formatted_rows(
                        widths=[text_width],
                        cells=[self.empty_table_indication.text()]))


        # Add outer table borders if required
        if solid_borders:
            for idx, row in enumerate(table_lines):
                if row.startswith(u' '):
                    table_lines[idx] = u'{b}{r}{b}'.format(b=self.table_format[TableSeparators.vertical],
                                                           r=row)

                else:
                    table_lines[idx] = u'{lb}{r}{rb}'.format(lb=self.table_format[TableSeparators.vertical_right],
                                                             r=row,
                                                             rb=self.table_format[TableSeparators.vertical_left])

            # Top Border
            table_lines.insert(0, u'{tl}{b}{tr}'.format(tl=self.table_format[TableSeparators.top_left],
                                                        b=horizontal_outer_border
                                                        if self.title and show_title
                                                        else top_col_border,
                                                        tr=self.table_format[TableSeparators.top_right]))

            if not self.suppress_empty_table_indication:
                if self.rows:
                    line = bottom_col_border

                else:
                    line = horizontal_outer_border if self._title and show_title else bottom_col_border

                table_lines.append(u'{bl}{line}{br}'.format(bl=self.table_format[TableSeparators.bottom_left],
                                                            line=line,
                                                            br=self.table_format[TableSeparators.bottom_right]))

        return u'\n'.join(table_lines)

    # Export to CSV
    def csv(self,
            sort_column=None,
            sort_ascending=True,
            delimiter=u','):

        if sort_column is not None:
            self.sort_by_column(column=sort_column,
                                ascending=sort_ascending)

        csv = []

        if self.show_column_headings or True:
            csv.extend([delimiter.join([heading.csv(delimiter=delimiter) for heading in self.headings.values()]),
                        u'\n'])

        for row in self.rows:
            cells = [row[key].csv(delimiter=delimiter) for key in self.headings.keys()]
            csv.append(delimiter.join(cells) + u'\n')

        return u''.join(csv)
