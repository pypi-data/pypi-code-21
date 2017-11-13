# mosaiq_field_export
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


"""A toolbox for extracting field data from Mosaiq SQL.
"""

import struct

import numpy as np
import pandas as pd

from mosaiq_connection import (
    get_fieldpoint_item as _get_fieldpoint_item,
    get_field_item as _get_field_item,
    get_raw_bytes as _get_raw_bytes
)


def _unpack_raw_mlc(raw_bytes):
    """Convert MLCs from Mosaiq SQL byte format to cm floats.
    """
    mlc_pos = np.array([
        [
            struct.unpack('<h', control_point[2*i:2*i+2])
            for i in range(len(control_point)//2)
        ]
        for control_point in raw_bytes
    ]) / 100

    return mlc_pos


def _get_mu(cursor, field_id):
    """Convert Mosaiq MU storage into MU delivered per control point.
    """
    total_mu = _get_field_item(cursor, 'Meterset', field_id)
    cumulative_percentage_mu = _get_fieldpoint_item(
        cursor, '[Index]', field_id)

    cumulative_mu = cumulative_percentage_mu * total_mu / 100
    # assert (
    #     np.shape(cumulative_mu)[0] <= 1
    # ), "There is only one MU item within field id {}".format(
    #     field_id)
    mu = np.concatenate([[0], np.diff(cumulative_mu)])
    return mu


def _get_mlc_a(cursor, field_id):
    """Pull the MLC positions of bank A.
    """
    raw_bytes = _get_raw_bytes(cursor, 'A_Leaf_Set', field_id)

    return _unpack_raw_mlc(raw_bytes)


def _get_mlc_b(cursor, field_id):
    """Pull the MLC positions of bank B.
    """
    raw_bytes = _get_raw_bytes(cursor, 'B_Leaf_Set', field_id)

    return _unpack_raw_mlc(raw_bytes)


def _get_gantry_angle(cursor, field_id):
    """Pull the gantry angle.
    """
    return _get_fieldpoint_item(cursor, 'Gantry_Ang', field_id)


def _get_collimator_angle(cursor, field_id):
    """Pull the collimator angle.
    """
    return _get_fieldpoint_item(cursor, 'Coll_Ang', field_id)


def _get_coll_y1(cursor, field_id):
    """Pull the Y1 jaws position.
    """
    return _get_fieldpoint_item(cursor, 'Coll_Y1', field_id)


def _get_coll_y2(cursor, field_id):
    """Pull the Y2 jaws position.
    """
    return _get_fieldpoint_item(cursor, 'Coll_Y2', field_id)


def _get_couch_angle(cursor, field_id):
    """Retrieve the couch angle.
    """
    return _get_fieldpoint_item(cursor, 'Couch_Ang', field_id)


def _pull_function_no_stack(function, cursor, fields):
    """Return a list of the results of a function repeated for all fields.
    """
    return [
        function(cursor, field)
        for field in fields
    ]


def _pull_function(function, cursor, fields):
    """Return a numpy array of the results of a function repeated over fields.
    """
    return np.hstack(_pull_function_no_stack(function, cursor, fields))


def _get_field_label(cursor, field_id):
    """Get the label of a field.
    """
    return _get_field_item(cursor, 'Field_Label', field_id, astype=str)


def _get_field_name(cursor, field_id):
    """Get the name of a field.
    """
    return _get_field_item(cursor, 'Field_Name', field_id, astype=str)


def _get_total_mu(cursor, field_id):
    """Get the total MUs.
    """
    return _get_field_item(cursor, 'Meterset', field_id, astype=str)


def _pull_mlc(cursor, fields):
    """Pull the MLCs from both banks for every field.
    """
    mlc_a = np.concatenate(
        _pull_function_no_stack(_get_mlc_a, cursor, fields), axis=0)
    mlc_b = np.concatenate(
        _pull_function_no_stack(_get_mlc_b, cursor, fields), axis=0)

    return mlc_a, mlc_b


def create_fields_overview(cursor, fields):
    """Create a table overview of the selected fields.
    """
    return pd.DataFrame(
        columns=[
            'Mosaiq SQL Field ID',
            'Field Label',
            'Field Name',
            'Total MU'],
        data=np.vstack([
            fields,
            _pull_function(_get_field_label, cursor, fields),
            _pull_function(_get_field_name, cursor, fields),
            _pull_function(_get_total_mu, cursor, fields)
        ]).T
    )


def pull_sql_data(cursor, fields):
    """Retrieve the SQL data and return within a metadata filled dictionary.
    """
    mu = _pull_function(_get_mu, cursor, fields)
    mlc_a, mlc_b = _pull_mlc(cursor, fields)

    gantry_angles = _pull_function(_get_gantry_angle, cursor, fields)
    collimator_angles = _pull_function(_get_collimator_angle, cursor, fields)

    coll_y1 = _pull_function(_get_coll_y1, cursor, fields)
    coll_y2 = _pull_function(_get_coll_y2, cursor, fields)
    couch_angle = _pull_function(_get_couch_angle, cursor, fields)

    scalar_control_point_data = pd.DataFrame(
        columns=[
            'MU',
            'Gantry Angle',
            'Collimator Angle',
            'Y1 Jaw',
            'Y2 Jaw',
            'Couch Angle'
        ],
        data=np.vstack([
            mu, gantry_angles, collimator_angles, coll_y1, coll_y2, couch_angle
        ]).T
    )

    mlc_a_df = pd.DataFrame(data=np.squeeze(mlc_a))
    mlc_b_df = pd.DataFrame(data=np.squeeze(mlc_b))

    fields_overview = create_fields_overview(cursor, fields)

    data_container = {
        'storage': {
            'fields.csv': fields_overview
        },
        'testing': [
            {
                'filename': 'mlc_a.csv',
                'contents': mlc_a_df,
                'file_test': {
                    'whole_file': {
                        'name': 'MLC A',
                        'method': 'exact_match'
                    }
                }
            },
            {
                'filename': 'mlc_b.csv',
                'contents': mlc_b_df,
                'file_test': {
                    'whole_file': {
                        'name': 'MLC B',
                        'method': 'exact_match'
                    }
                }
            },
            {
                'filename': 'scalar_control_point_data.csv',
                'contents': scalar_control_point_data,
                'file_test': {
                    'column_by_column': [
                        {
                            'name': 'MU',
                            'method': 'absolute_difference_less_than',
                            'args': (0.05,)
                        },
                        {
                            'name': 'Gantry Angle',
                            'method': 'exact_match'
                        },
                        {
                            'name': 'Collimator Angle',
                            'method': 'exact_match'
                        },
                        {
                            'name': 'Y1 Jaw',
                            'method': 'exact_match'
                        },
                        {
                            'name': 'Y2 Jaw',
                            'method': 'exact_match'
                        },
                        {
                            'name': 'Couch Angle',
                            'method': 'exact_match'
                        }
                    ]
                }
            }
        ]
    }

    return data_container