import uuid
import itertools
import math

import formatted_text
from base import _Component

class TableColumn(object):
    """ Represent a column in table

    :param ~eureqa.analysis.components.table_builder.TableBuilder parent_table: the containing table
    :param list col_data: data for this column. Can be either a list of str or a list of float
    :param str col_name: name of this column
    """

    def __init__(self, parent_table, col_data, col_name):
        self._parent_table = parent_table
        self._col_data = col_data
        self._column_name = col_name
        self.column_header = col_name
        self._sort_values = None
        self._sort_col_name = col_name
        self._rendered_values = None
        self._rendered_col_name = col_name
        self.searchable = True
        self._width = 1
        self.filterable = False
        self._filter_only = False
        self.filter_name = col_name

    @property
    def column_name(self):
        """The name of this column"""

        return self._column_name

    @column_name.setter
    def column_name(self, new_name):
        """Change the name of this column

        :param str new_name: The new name of the column
        """

        try:
            self._parent_table._change_col_name(self._column_name, new_name)
        except KeyError:
            pass  # if this is an orphan column, ignore and continue

        if self._rendered_col_name == self._column_name:
            self._rendered_col_name = new_name
        if self._sort_col_name == self._column_name:
            self._sort_col_name = new_name
        self._column_name = new_name

    @property
    def sort_values(self):
        """A list of values specifying how the column is sorted"""

        return self._sort_values

    @sort_values.setter
    def sort_values(self, sort_values):
        """Change how the column is sorted

        Note the input must be a list of numbers. The input could be a pandas.Series only if the index runs from 0 to (n-1)

        :param a list of numbers sort_values: the value for each row used for sorting
        """

        self._sort_col_name = str(uuid.uuid4())

        # Backend expects no nans/infs, so we replace nan/-inf with (min(values)-1) and +inf with (max(values)+1).
        # Also we cap the magnitude of all values at a value which is smaller than the largest value JS can represent.
        self._sort_values = sort_values
        largest_value = 2**52
        smallest_value = -largest_value
        set_to_min = []
        set_to_max = []
        for i in xrange(len(self._sort_values)):
            value = self._sort_values[i]
            # ignore strings -- the processing we need to do only applies to numeric values
            if not isinstance(value, float) and not isinstance(value, int):
                continue
            if (math.isnan(value) or (math.isinf(value) and value < 0)) or (value < smallest_value):
                set_to_min.append(i)
            elif (math.isinf(value) and value > 0) or (value > largest_value):
                set_to_max.append(i)
        for i in set_to_min:
            self._sort_values[i] = smallest_value
        for i in set_to_max:
            self._sort_values[i] = largest_value

    @property
    def rendered_values(self):
        """A list of values specifying how the column is rendered"""

        return self._rendered_values

    @rendered_values.setter
    def rendered_values(self, rendered_values):
        """Change how the column is rendered

        :param a list of str or numbers: the value for each row used for rendering
        """
        self._rendered_values = rendered_values
        self._rendered_col_name = str(uuid.uuid4())

    @property
    def width(self):
        """ The width of this column"""

        return self._width

    @width.setter
    def width(self, width):
        """ Change the width of this column

        :param double width: a number representing the percentage of whole table width for this column
        """

        if width <= 0:
            raise RuntimeError("Column width must be larger than zero")
        self._width = width

    @property
    def filter_only(self):
        """ Whether this column is only for filtering, if True this column doesn't appear in the table"""

        return self._filter_only

    @filter_only.setter
    def filter_only(self, filter_only):
        """ Change whether this column is only for filtering

        :param bool filter_only: whether or not this column should be set to filter only
        """

        self._filter_only = filter_only
        self.filterable = True

        # filter_only columns don't show up in the table component, it would be
        # very confusing if you can search on them
        self.searchable = False

    def _get_data_columns(self, analysis):
        cols_name = [str(self._column_name)]
        cols_data = [self._col_data]
        cols_comp = []

        if self._sort_values is not None:
            cols_name.append(self._sort_col_name)
            cols_data.append(self._sort_values)

        if self._rendered_values is not None:
            comp_ref_and_comp_def_by_row = [
                    formatted_text._get_component_ref_and_defs_for_value(rendered_value, analysis, associate_with_analysis=False)
                    for rendered_value in self._rendered_values]
            comp_ref, comp_def = itertools.izip(*comp_ref_and_comp_def_by_row)  # transpose it into 2 columns

            cols_name.append(self._rendered_col_name)
            cols_data.append(comp_ref)
            cols_comp = comp_def

        return cols_data, cols_name, cols_comp
