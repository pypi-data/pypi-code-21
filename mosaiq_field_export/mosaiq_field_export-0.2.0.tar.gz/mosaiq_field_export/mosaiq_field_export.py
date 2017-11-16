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

import os
import json
import datetime
import struct

import numpy as np
import pandas as pd

from mosaiq_connection import (
    sql_connection as _sql_connection,
    patient_fields as _patient_fields,
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


def display_fields(patient_ids, sql_users, sql_servers):
    """Display all fields stored under a given Patient ID.
    """
    with _sql_connection(sql_users, sql_servers) as cursors:
        for key in sql_servers:
            print('# {} Fields for {}'.format(key.upper(), patient_ids[key]))
            print(_patient_fields(cursors[key], patient_ids[key]))


def display_fields_overview(fields, sql_users, sql_servers):
    """Display an overview for a given list of fields.
    """
    with _sql_connection(sql_users, sql_servers) as cursors:
        for key in sql_servers:
            print('# {} fields overview'.format(key.upper()))
            fields_overview = create_fields_overview(
                cursors[key], fields[key])
            print(fields_overview)
            print("Combined MU: {}".format(np.sum(
                fields_overview['Total MU'].values.astype(float))))


def _pull_fields_sql_data(fields, sql_users, sql_servers):
    """Pull the SQL data for all of the fields provided in the list.
    """
    with _sql_connection(sql_users, sql_servers) as cursors:
        data = dict()
        for key, cursor in cursors.items():
            data[key] = pull_sql_data(cursor, fields[key])

    return data


def _create_directory(directory):
    """Creates a directory if it doesn't already exist.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def msq2csv(directory, fields, sql_users, sql_server):
    """Pull the data for the given fields and save to a set of csv files.
    """
    _create_directory(directory)
    centre_data = _pull_fields_sql_data(fields, sql_users, sql_server)

    timestamp = '{:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
    timestamped_directory = os.path.join(directory, timestamp)
    _create_directory(timestamped_directory)

    for centre_key, data_container in centre_data.items():
        centre_directory = os.path.join(
            timestamped_directory, centre_key)
        _create_directory(centre_directory)

        testing_file_contents = [
            (item['filename'], item.pop('contents'))
            for item in data_container['testing']
        ]

        filepath = os.path.join(centre_directory, 'testing_metadata.json')
        with open(filepath, 'w') as file:
            file.write(json.dumps(
                data_container['testing'], indent=4, sort_keys=True))

        for file_name, file_contents in data_container['storage'].items():
            filepath = os.path.join(centre_directory, file_name)
            file_contents.to_csv(filepath)

        for file_name, file_contents in testing_file_contents:
            filepath = os.path.join(centre_directory, file_name)
            file_contents.to_csv(filepath)
