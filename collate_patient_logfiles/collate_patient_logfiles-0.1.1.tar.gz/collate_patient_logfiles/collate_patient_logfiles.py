"""Collate patient logfiles.
"""

import os
import json
import string

from glob import glob
import attr
import yaml

import numpy as np
import pandas as pd

# import tqdm


Y1_LEAF_BANK_NAMES = [
    'Y1 Leaf {}/Scaled Actual (mm)'.format(item)
    for item in range(1, 81)
]

Y2_LEAF_BANK_NAMES = [
    'Y2 Leaf {}/Scaled Actual (mm)'.format(item)
    for item in range(1, 81)
]

def get_header_dataframe(header_files):
    """Creates a dataframe containing all of the logfile headers.

    This is slow. It should be run through a database instead.
    """

    header_data = {}

    for file_name in header_files:
        with open(file_name, 'r') as stream:
            data = yaml.load(stream)
            if data['field_label'] != '':
                data['file_name'] = file_name
                header_data[data['local_timestamp']] = data

    header_dataframe = pd.DataFrame.from_dict(header_data, orient='index')

    return header_dataframe


def get_patient_dataframe(header_dataframe, patient_id):
    """Gets patient dataframe given a patient id.
    """
    patient_dataframe = header_dataframe[header_dataframe['id'] == patient_id]
    return patient_dataframe


def timestamp_convert(field_dataframe):
    """Pull timestamps out of dataframe and convert to numpy"""
    time_stamps = field_dataframe['local_timestamp'].values
    time_stamps = time_stamps.astype(np.datetime64)

    return time_stamps


def load_logfiles(field_dataframe):
    """Loads up the logfiles for a given patient dataframe.

    This is also really slow. This should also be in a database.
    """
    time_stamps = timestamp_convert(field_dataframe)

    extension_removed = [
        os.path.splitext(item)[0]
        for item in field_dataframe['file_name']
    ]

    decoded_logfile = [
        "{}_python_decode.csv".format(item)
        for item in extension_removed
    ]

    for item in decoded_logfile:
        assert os.path.exists(item)

    logfiles = {
        time_stamps[i]: pd.read_csv(item)
        for i, item in enumerate(decoded_logfile)
    }

    return logfiles

@attr.s
class DeliveryData(object):
    """Object for storing patient delivery data for a given treatment.
    """
    machine = attr.ib()
    centre = attr.ib()
    logfile = attr.ib()

    monitor_units = attr.ib()
    gantry = attr.ib()
    collimator = attr.ib()
    mlc1 = attr.ib()
    mlc2 = attr.ib()
    jaw1 = attr.ib()
    jaw2 = attr.ib()


def create_new_delivery_data():
    return DeliveryData(
        machine=[], centre=[], logfile=[],
        monitor_units=np.empty(0), gantry=np.empty(0),
        collimator=np.empty(0), jaw1=np.empty(0),
        jaw2=np.empty(0),
        mlc1=np.empty([80, 0]), mlc2=np.empty([80, 0])
    )


def attrib_append(column, mask, delivery_data, attrib):
    """Append data from a pandas column onto a delivery data attribute.
    """
    values = column.values[mask]
    appended = np.hstack([
        getattr(delivery_data, attrib), values
    ])

    setattr(delivery_data, attrib, appended)


def multiple_appends(logfile, lookup_keys, mask, delivery_data):
    """Append data from a logfile into a DeliveryData based on lookup_keys.
    """
    for attrib, column in lookup_keys.items():
        attrib_append(
            logfile[column], mask,
            delivery_data, attrib)


def pull_single_logfile(delivery_data: DeliveryData, logfile, header):
    """Append a logfile onto a DeliveryData object.
    """
    monitor_units = logfile['Step Dose/Actual Value (Mu)'].values

    diff = np.append([0], np.diff(monitor_units))
    diff[diff < 0] = 0
    mask = diff != 0
    mask[0] = True

    cumulative_monitor_units = np.cumsum(diff)

    combined_monitor_units = np.hstack([
        delivery_data.monitor_units, cumulative_monitor_units[mask]
    ])

    combined_diff = np.append([0], np.diff(combined_monitor_units))
    combined_diff[combined_diff < 0] = 0

    delivery_data.monitor_units = np.cumsum(combined_diff)

    y1_bank = []
    for name in Y1_LEAF_BANK_NAMES:
        y1_bank.append(logfile[name][mask])

    delivery_data.mlc1 = np.hstack([
        delivery_data.mlc1, np.array(y1_bank)
    ])

    y2_bank = []
    for name in Y2_LEAF_BANK_NAMES:
        y2_bank.append(logfile[name][mask])

    delivery_data.mlc2 = np.hstack([
        delivery_data.mlc2, np.array(y2_bank)
    ])

    lookup_keys = {
        'jaw1': 'X1 Diaphragm/Scaled Actual (mm)',
        'jaw2': 'X2 Diaphragm/Scaled Actual (mm)',
        'gantry': 'Step Gantry/Scaled Actual (deg)',
        'collimator': 'Step Collimator/Scaled Actual (deg)'
    }

    multiple_appends(logfile, lookup_keys, mask, delivery_data)

    assert len(header['file_name']) == 1

    delivery_data.machine.append(header['machine'][0])
    delivery_data.centre.append(header['centre'][0])
    delivery_data.logfile.append(header['file_name'][0])


def collate_field_logfile_data(logfiles, field_dataframe):
    """Extract pertinent data from provided logfiles into a data dictionary.
    """
    time_stamps = list(logfiles.keys())
    header_timestamps = timestamp_convert(field_dataframe)

    sorted_timestamps = np.sort(time_stamps)
    time_diff = np.diff(sorted_timestamps)

    less_than_two_hours = np.append(
        [True], time_diff < np.timedelta64(60 * 60 * 2))
    split = np.where(np.invert(less_than_two_hours))[0]
    grouped_timestamps = np.split(sorted_timestamps, split)

    field_data = dict()

    for timestamp_group in grouped_timestamps:
        key = str(timestamp_group[-1])
        field_data[key] = create_new_delivery_data()
        assert not field_data[key].machine, 'Machine should be empty'
        # data[key] = np.array()

        for timestamp in timestamp_group:
            logfile = logfiles[timestamp]

            reference = header_timestamps == timestamp
            assert np.sum(reference) == 1, "Should match one timestamp"
            index = np.where(reference)[0][0]

            header = field_dataframe.iloc[[index]]
            assert len(header.index) == 1, "Should have 1 header entry"

            pull_single_logfile(field_data[key], logfile, header)

    return field_data


def dictionary_merge(dict_a, dict_b, path=None):
    """Merges dict_b into dict_a

    Based off of https://stackoverflow.com/a/7205107/3912576
    """
    if path is None:
        path = []
    for key in dict_b:
        if key in dict_a:
            if isinstance(dict_a[key], dict) and isinstance(dict_b[key], dict):
                dictionary_merge(dict_a[key], dict_b[key], path + [str(key)])
            elif dict_a[key] == dict_b[key]:
                pass # same leaf value
            else:
                raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            dict_a[key] = dict_b[key]


def make_patient_data_plain_objects(patient_data):
    """Convert patient data to be json serializable."""

    for key in patient_data:
        patient_data[key] = patient_data[key].__dict__

        for attribute in patient_data[key]:
            if isinstance(patient_data[key][attribute], np.ndarray):
                patient_data[key][attribute] = np.around(
                    patient_data[key][attribute],
                    decimals=6).tolist()


def get_field_data(field_dataframe):
    """Get patient data for a given id and a dataframe of header files."""

    logfiles = load_logfiles(field_dataframe)
    field_data = collate_field_logfile_data(logfiles, field_dataframe)

    make_patient_data_plain_objects(field_data)

    return field_data


def get_field_dataframe(patient_dataframe, field_label, field_name):
    field_dataframe = patient_dataframe.loc[
        (patient_dataframe['field_label'] == field_label) &
        (patient_dataframe['field_name'] == field_name)
    ]

    return field_dataframe


def make_a_valid_filename(proposed_filename):
    """In the case a field label can't be used as a file name the invalid
    characters can be dropped."""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in proposed_filename if c in valid_chars)

    return filename


def update_data_files(directory, header_glob):
    """Given a list of header file names appends new patient data to an
    existing set of patient data.
    """
    header_files = glob(header_glob)

    if not header_files:
        raise Exception(
            "No files were found that match the provided search string")

    header_dataframe = get_header_dataframe(header_files)
    patient_ids = np.unique(header_dataframe['id'])
    print("Patient IDs to be collated:\n{}".format(patient_ids))

    for i, patient_id in enumerate(patient_ids):
        print("Collating {} ({} of {})".format(
            patient_id, i + 1, len(patient_ids)))

        patient_dataframe = get_patient_dataframe(header_dataframe, patient_id)
        patient_dir = os.path.join(directory, patient_id)
        os.makedirs(patient_dir, exist_ok=True)

        first_names = set(patient_dataframe['first_name'])
        last_names = set(patient_dataframe['last_name'])

        if len(first_names) != 1:
            raise Exception("Patient ID has multiple first names")

        if len(last_names) != 1:
            raise Exception("Patient ID has multiple last names")

        first_name = first_names.pop()
        last_name = last_names.pop()

        patient_dictionary = {
            'patient_id': patient_id,
            'first_name': first_name,
            'last_name': last_name
        }

        fields = set(zip(
            patient_dataframe['field_label'], patient_dataframe['field_name']))

        for field in fields:
            field_label = field[0]
            field_name = field[1]

            field_dictionary = {
                'field_label': field_label,
                'field_name': field_name
            }

            proposed_field_filename = '_'.join(field)
            field_filename = make_a_valid_filename(
                "{}.json".format(proposed_field_filename))

            data_filename = os.path.join(patient_dir, field_filename)

            if os.path.exists(data_filename):
                with open(data_filename, 'r') as file:
                    data = json.load(file)

                if data['field'] != field_dictionary:
                    raise Exception(
                        "Field data does not match data loaded from disk")

                if data['patient'] != patient_dictionary:
                    raise Exception(
                        "Patient data does not match data loaded from disk")

            else:
                data = dict()
                data['deliveries'] = dict()
                data['field'] = field_dictionary
                data['patient'] = patient_dictionary

            field_dataframe = get_field_dataframe(
                patient_dataframe, field_label, field_name)

            new_field_data = get_field_data(field_dataframe)

            dictionary_merge(data['deliveries'], new_field_data)

            with open(data_filename, 'w') as file:
                json.dump(data, file)

    print("Complete")
