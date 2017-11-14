# mosaiq_connection
# Copyright (C) 2017  CCA Health Care

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A toolbox for executing code on Mosaiq SQL.
"""

import numpy as np

def execute_sql(cursor, sql_string):
    """Executes a given SQL string on an SQL cursor.
    """
    cursor.execute(sql_string)

    data = []

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            data.append(row)

    return data


def patient_fields(cursor, patient_id):
    """Returns all of the patient fields for a given Patient ID.
    """
    return execute_sql(cursor, """
        SELECT
            TxField.FLD_ID,
            TxField.Field_Label,
            TxField.Field_Name,
            TxField.Version,
            TxField.Meterset
        FROM Ident, TxField
        WHERE
            TxField.Pat_ID1 = Ident.Pat_ID1 AND
            Ident.IDA = '{}'
        """.format(patient_id))


def _get_table_item(table, id_label, cursor, column, item_id):
    """Retrieves a given table item.
    """
    return execute_sql(cursor, """
        SELECT
            {0}.{2}
        FROM {0}
        WHERE
            {0}.{1} = '{3}'
        """.format(table, id_label, column, item_id))


def _get_raw_field_item(cursor, label, field_id):
    """Returns an unprocessed treatment field item.
    """
    return _get_table_item('TxField', 'FLD_ID', cursor, label, field_id)


def get_field_item(cursor, label, field_id, astype=float):
    """Returns a processed treatment field item.
    """
    data = _get_raw_field_item(cursor, label, field_id)

    return np.squeeze(data).astype(astype)


def _get_raw_fieldpoint_item(cursor, label, field_id):
    """Returns unprocessed treatment field control point item.
    """
    return _get_table_item('TxFieldPoint', 'FLD_ID', cursor, label, field_id)


def get_fieldpoint_item(cursor, label, field_id, astype=float):
    """Returns a processed treatment field control point item.
    """
    data = _get_raw_fieldpoint_item(cursor, label, field_id)

    return np.squeeze(data).astype(astype)


def get_raw_bytes(cursor, label, field_id):
    """Returns a control point item as bytes.
    """
    return get_fieldpoint_item(cursor, label, field_id, astype=bytes)
