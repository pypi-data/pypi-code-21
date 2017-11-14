"""Uses Mosaiq SQL to name the linac log files.
"""

import os
import sys
from datetime import datetime
from glob import glob

from dateutil import tz
import attr

import yaml

from trf2csv import decode_header_from_file
from mosaiq_connection import execute_sql, sql_connection
from centre_config import MACHINE_MAP, SQL_USERS, SQL_SERVERS, TIMEZONE

# pylint: disable=C0103

def date_convert(date, timezone):
    """Converts logfile UTC date to the provided timezone.
    The date is formatted to match the syntax required by Microsoft SQL."""

    from_timezone = tz.gettz('UTC')
    to_timezone = tz.gettz(timezone)

    utc_datetime = datetime.strptime(
        date, '%y/%m/%d %H:%M:%S Z').replace(tzinfo=from_timezone)
    local_time = utc_datetime.astimezone(to_timezone)
    string_time = local_time.strftime('%Y-%m-%d %H:%M:%S')

    return string_time


@attr.s
class Patient(object):
    """A class containing patient information extracted from Mosaiq."""
    id = attr.ib()
    last_name = attr.ib()
    first_name = attr.ib()


def get_id_and_name(header, converted_date, cursor, time_alignement_buffer):
    """Identifies the patient details for the provided header.

    Uses the header information provided from a logfile to detect the patient
    who was being treated at that time.
    """

    execute_string = """
        SELECT
            Ident.IDA,
            Patient.Last_Name,
            Patient.First_Name
        FROM TrackTreatment, Ident, Patient, TxField, Staff
        WHERE
            TrackTreatment.Pat_ID1 = Ident.Pat_ID1 AND
            Patient.Pat_ID1 = Ident.Pat_ID1 AND
            TrackTreatment.FLD_ID = TxField.FLD_ID AND
            Staff.Staff_ID = TrackTreatment.Machine_ID_Staff_ID AND
            REPLACE(Staff.Last_Name, ' ', '') = '{0}' AND
            DATEADD(second, -{4}, TrackTreatment.Create_DtTm) <= '{1}' AND
            DATEADD(second, {4}, TrackTreatment.Edit_DtTm) >= '{1}' AND
            TxField.Field_Label = '{2}' AND
            TxField.Field_Name = '{3}'
        """.format(
            header.machine, converted_date,
            header.field_label, header.field_name, time_alignement_buffer)

    sql_result = execute_sql(cursor, execute_string)

    if len(sql_result) > 1:
        for result in sql_result[1::]:
            if result != sql_result[0]:
                raise Exception("Disagreeing entries were found.")

    if not sql_result:
        exception_string = (
            "found for -- \nheader: \n    {}\n"
            "date: \n    {}".format(header, converted_date))
        raise Exception(
            "No Mosaiq entries were {}".format(exception_string))

    patient = Patient(*sql_result[0])


    return patient


def get_centre(header):
    """Uses the machine label within the header to determine the centre.

    Need to know which centre the delivery occured at so that the correct
    Mosaiq SQL database is used."""

    return MACHINE_MAP[header.machine]


def logfilenamer(filepath, cursors, skip_if_exists=True, time_alignement_buffer=30):
    """Creates named metadata for logfiles.

    Takes a filepath and SQL connection cursors and writes out a .yaml file
    containing patient information and other relevant header data.

    If the linac and mosaiq clocks are out of sync the time alignment buffer
    can be increased to allow a greater search window. This is in units of
    seconds.
    """
    metadata_filepath = "{}.yaml".format(os.path.splitext(filepath)[0])

    # Maybe don't include this at all
    # The caller of logfilenamer can determine whether or not it exists...
    if skip_if_exists:
        if os.path.exists(metadata_filepath):
            # print('Skipping (already named) {}'.format(filepath))
            return None

    header = decode_header_from_file(filepath)
    header_dict = attr.asdict(header)

    if header.field_label == '':
        print('Naming (only header, not clinical field name) {}'.format(
            filepath))
        with open(metadata_filepath, 'w') as outfile:
            yaml.dump(header_dict, outfile, default_flow_style=False)

    else:
        print('Naming {}'.format(filepath))
        centre = get_centre(header)

        converted_date = date_convert(header.date, TIMEZONE[centre])
        patient = get_id_and_name(
            header, converted_date, cursors[centre], time_alignement_buffer)
        patient_dict = attr.asdict(patient)

        merged_metadata = {**patient_dict, **header_dict}
        merged_metadata['local_timestamp'] = converted_date
        merged_metadata['centre'] = centre

        with open(metadata_filepath, 'w') as outfile:
            yaml.dump(merged_metadata, outfile, default_flow_style=False)

        return patient


def main():
    """CLI entry point."""
    if len(sys.argv) == 1:
        print(
            "=============================================================\n"
            "Need to provide filename(s).\n\n"
            "Example usage for naming all files in current directory:\n"
            "    logfilenamer *.trf\n"
            "=============================================================")

    glob_strings = sys.argv[1::]

    with sql_connection(SQL_USERS, SQL_SERVERS) as cursors:
        for glob_string in glob_strings:
            filepaths = glob(glob_string)
            for filepath in filepaths:
                logfilenamer(filepath, cursors)


if __name__ == "__main__":
    main()
