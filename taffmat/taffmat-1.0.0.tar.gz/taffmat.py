# -*- coding: utf-8 -*-
# Copyright (c) 2014-2017 The taffmat developers. All rights reserved.
# Project site: https://github.com/quest/taffmat
# Use of this source code is governed by a MIT-style license that
# can be found in the LICENSE.txt file for the project.
"""Read and write Teac TAFFmat files.

The .dat file is read into a numpy array.
The .hdr file is read into an OrderedDict

Per the Teac LX-10 Instruction Manual, the A/D-converted data
is recored as 2-byte integers from -32,768 to +32,767. Negative
numbers are expressed as 2's complements. The byte order is from
the lower bytes to the higher bytes.

The max ADC values are +/-25,000, which represents +/-100% of
the input range (i.e., slope = range / 25000):

     0.5V = 2e-5
       1V = 4e-5
       2V = 8e-5
       5V = 2e-4
      10V = 4e-4
      20V = 8e-4
      50V = 2e-3

# Notes on the header file format #

* If the voice memo recording is off, then the VOICE_MEMO line will
be absent from the header file.
* The MEMO_LENGTH and MEMO lines are *not* related to the voice memo.
Those are for the memo field. The MEMO_LENGTH line contains
an integer of the number of characters on the MEMO line and
then has 7 zeros comma separated afterwards.
* Some HDR files have two blank lines at the end with the last line containing
three spaces (line above that contains nothing). Other HDR files appear
to just have one blank line at the end with no spaces on it.
* The binary Teac data is stored as int16 (2-bytes) and only
+25,000 to -25,000 and then it's multiplied by the slope,
which we know can be 0.5, 1, 2, 5, 10, 20 or 50 V. Note that,
"a range of +/-131% of the selected range can be obtained for
A/D conversion value; however, the input margin
level is approximately +/-120%." [Source p. 4-5 of Teac manual]

"""

# Standard module imports
from collections import OrderedDict
from datetime import datetime
import logging
import os

# Data analysis related imports
import numpy as np

__version__ = '1.0.0'


def _append_windows_newlines(input_list_of_strings):
    '''Append Windows style newlines to list of strings.

    Takes a list of strings and replaces UNIX style line endings with
    Windows style line endings \\r\\n.

    Args:
        input_list_of_strings: A list of strings.

    Returns:
        A list of strings with Windows newline characters \\r\\n.

    Raies:
        N/A
    '''
    windows_newline_character = '\r\n'
    output_list_of_strings = []
    for line in input_list_of_strings:
        output_list_of_strings.append(line + windows_newline_character)

    return output_list_of_strings


def _apply_slope_and_offset(data_array, number_of_series, slope, y_offset):
    """
    Convert from int16 to float64 and apply the slope and offset
    so the data_array contains the measured values.
    """
    data_array = data_array.astype(np.float64)
    for series in range(0, number_of_series):
        data_array[series] = (data_array[series] * slope[series] +
                              y_offset[series])

    return data_array


def _remove_slope_and_offset(data_array, number_of_series, slope, y_offset):
    """
    Convert data_array from float64 to int16 by removing the slope and offset
    in preparation to writing the TAFFmat .dat file
    """
    # FIXME: There's no reason to pass the number_of_series into this function
    # since the data_array's first dimension tells how many series there are.
    for series in range(0, number_of_series):
        data_array[series] = np.around(
            (data_array[series] - y_offset[series]) / slope[series])

    data_array = data_array.astype('int16')

    return data_array


def _format_exponent_notation(input_number, precision, num_exponent_digits):
    """
    Format the exponent notation. Python's exponent notation doesn't allow
    for a user-defined number of exponent digits.

    Based on [Anurag Uniyal's answer][answer] to the StackOverflow
    question ['Python - number of digits in exponent'][question]

    [question]: http://stackoverflow.com/q/9910972/95592
    [answer]: http://stackoverflow.com/a/9911741/95592
    """
    python_exponent_notation = '{number:.{precision}e}'.format(
        number=input_number,
        precision=precision)
    mantissa, exponent = python_exponent_notation.split('e')
    # Add 1 to the desired number of exponenent digits to account for the sign
    return '{mantissa}e{exponent:+0{exp_num}d}'.format(
        mantissa=mantissa,
        exponent=int(exponent),
        exp_num=num_exponent_digits+1)


def _read_taffmat_hdr(input_hdr_file):
    '''
    Read the TAFFmat .hdr file into a "smart" dictionary containing
    all the header data.
    '''

    # Read in all lines from the .hdr file
    with open(input_hdr_file, 'r') as f_header:
        header_data_all_lines = f_header.readlines()

    # Read the header file into an ordered dictionary using the first
    # word of each line as the key.
    raw_header_data = OrderedDict()
    for line in header_data_all_lines:
        try:
            [key, data] = line.split(' ', 1)
            if key is not '':
                if key.lower() in raw_header_data:
                    raw_header_data[key.lower() + '2'] = data.strip()
                else:
                    raw_header_data[key.lower()] = data.strip()
        except Exception:
            raw_header_data[line.lower().strip()] = ''

    # Create a "smarter" dictionary based on the raw_header_data
    header_data = OrderedDict()
    header_data['dataset'] = raw_header_data['dataset']
    header_data['version'] = int(raw_header_data['version'])
    header_data['series_labels'] = raw_header_data['series'].split(',')
    start_recording_datetime_as_string = (
        raw_header_data['date'] + ' ' + raw_header_data['time'])
    header_data['recording_start_datetime'] = datetime.strptime(
        start_recording_datetime_as_string, '%m-%d-%Y %H:%M:%S.%f')
    header_data['sampling_frequency_hz'] = int(raw_header_data['rate'])
    header_data['vertical_units'] = raw_header_data['vert_units'].split(',')
    header_data['horizontal_units'] = raw_header_data['horz_units']
    header_data['comment'] = raw_header_data['comment']
    header_data['number_of_series'] = int(raw_header_data['num_series'])
    header_data['storage_mode'] = raw_header_data['storage_mode']
    # The file_type lists how the data was recorded and saved in .dat
    # INTEGER = 16 bit A/D = 2-byte integers
    # LONG = 24 bit A/D = 4-byte integers
    header_data['file_type'] = raw_header_data['file_type']
    header_data['slope'] = [
        float(slope) for slope in raw_header_data['slope'].split(',')]
    header_data['x_offset'] = float(raw_header_data['x_offset'])
    header_data['y_offset'] = [
        float(y_offset) for y_offset in raw_header_data['y_offset'].split(',')]
    header_data['number_of_samples'] = int(raw_header_data['num_samps'])
    # The .hdr file will have a row containing just "DATA" to indicate
    # that the entries here on are proprietary to the data recorder.
    # Prior to this point, the header file was in the DADiSP format.
    header_data['device'] = raw_header_data['device']
    # FIXME: The following information is not recorded when recording to
    # a PC. Should update the reading and writing code to handle
    # that scenario.
    slot1_amp = raw_header_data['slot1_amp'].split(',')
    header_data['slot1_amp'] = {}
    header_data['slot1_amp']['id_name'] = slot1_amp[0]
    header_data['slot1_amp']['num_of_channels'] = slot1_amp[1]
    header_data['slot1_amp']['pld_version'] = slot1_amp[2].strip()
    header_data['slot1_amp']['firmware_version'] = slot1_amp[3].strip()
    header_data['slot2_amp'] = {}
    slot2_amp = raw_header_data['slot2_amp'].split(',')
    header_data['slot2_amp']['id_name'] = slot2_amp[0]
    header_data['slot2_amp']['num_of_channels'] = slot2_amp[1]
    header_data['slot2_amp']['pld_version'] = slot2_amp[2].strip()
    header_data['slot2_amp']['firmware_version'] = slot2_amp[3].strip()
    header_data['channel_info'] = []
    for index in range(header_data['number_of_series']):
        raw_key = 'ch{channel_num}_{channel_num}'.format(
            channel_num=index + 1)
        raw_channel_info = raw_header_data[raw_key].split(',')
        header_data['channel_info'].append({
            'channel_num': index + 1,
            'amp_type': raw_channel_info[0],
            'range_setting': raw_channel_info[1],
            'filter_setting': raw_channel_info[2]})
    header_data['id_num'] = int(raw_header_data['id_no'])
    start_time, end_time = raw_header_data['time2'].split(',')
    header_data['start_time'] = int(start_time)
    header_data['stop_time'] = int(end_time)
    header_data['recording_destination'] = raw_header_data['rec_mode']
    # FIXME: Need to properly parse the start trigger and stop condition
    # Right now I'm basically assuming they're not used in the data.
    header_data['start_trigger'] = raw_header_data['start_trigger']
    header_data['stop_condition'] = raw_header_data['stop_condition']
    if 'voice_memo' in raw_header_data:
        # Voice memo was recorded
        header_data['voice_memo_on'] = True
        voice_memo_temp = raw_header_data['voice_memo'].split(',')
        header_data['voice_memo_bits_per_sample'] = voice_memo_temp[0]
        header_data['voice_memo_size_bytes'] = int(voice_memo_temp[1])
    else:
        # Voice memo was not recored
        header_data['voice_memo_on'] = False
    # Determine the version of data recorder used to capture the data
    # FIXME: Instead of saving the FW and PAL versions for the recorder
    # as a string, I should split them out into their own dictionary.
    if 'lx10_version' in raw_header_data:
        header_data['recorder_model'] = 'LX10'
        header_data['recorder_version'] = raw_header_data['lx10_version']
    elif 'lx20_version' in raw_header_data:
        header_data['recorder_model'] = 'LX20'
        header_data['recorder_version'] = raw_header_data['lx20_version']
    elif 'lx110_version' in raw_header_data:
        header_data['recorder_model'] = 'LX110'
        header_data['recorder_version'] = raw_header_data['lx110_version']
    elif 'lx120_version' in raw_header_data:
        header_data['recorder_model'] = 'LX120'
        header_data['recorder_version'] = raw_header_data['lx120_version']
    else:
        header_data['recorder_model'] = 'Unrecognized data recorder model'
        header_data['recorder_version'] = 'Unknown data recorder version'
    # FIXME: Instead of storing the memo_length as a string, I should strip
    # the first number which is the length of the memo. After the memo
    # length, this field will always have seven comma separated zeros
    # (e.g., ",0,0,0,0,0,0,0")
    header_data['memo_length'] = raw_header_data['memo_length']
    header_data['memo'] = raw_header_data['memo']

    return header_data


def change_slope(data_array, series, gain):
    '''Apply gain to the desired series in a data_array

    Args:
        data_array:
        series: integer listing the series to apply the gain (0-based)
        gain: float by which all data for given series will be multiplied

    Return:
        data_array: Return by reference

    Raises:
        N/A
    '''
    data_array[series] = gain * data_array[series]
    return data_array


def _read_taffmat_dat(input_dat_file, file_type, number_of_series,
                      slope, y_offset):
    '''Read the TAFFmat binary .dat file

    Args:
        input_dat_file: Filename of the .dat file
        file_type: INTEGER or LONG as determined by reading the .hdr
            file so we know if the data was recording in 2 or 4-bytes
        number_of_series: Integer from .hdr file stating the number of
            series recorded in the .dat file
        slope: list of floats read from .hdr file (slope = range / 25,000).
            One float per series. The max range of the ADC is +/-25,000
             0.5V = 2e-5
               1V = 4e-5
               2V = 8e-5
               5V = 2e-4
              10V = 4e-4
              20V = 8e-4
              50V = 2e-3
        y_offset: list of floats read from .hdr file. One float per
            series.

    Returns:
        data_array: ndarray with shape series x num_samples

    Raises:
        N/A
    '''

    # Determine if the .dat file saved the data using 2-bytes (int16)
    # or 4-bytes (int32).
    if file_type == 'INTEGER':
        data_size = np.int16
    elif file_type == 'LONG':
        data_size = np.int32
    else:
        data_size = np.int16
    # Read the entire file and reshape the data so that each channel/series
    # is in its own row
    with open(input_dat_file, 'rb') as datfile:
        data_array = np.fromfile(datfile, data_size).reshape(
            (-1, number_of_series)).T

    data_array = _apply_slope_and_offset(data_array,
                                         number_of_series, slope,
                                         y_offset)

    return (data_array)


def _write_taffmat_hdr(header_data, output_hdr_filename):
    '''
    Write the TAFFmat .hdr file
    '''
    logging.info('output_hdr_filename = {}'.format(output_hdr_filename))
    output_hdr_filename_root, output_hdr_filename_extension = \
        os.path.splitext(os.path.basename(output_hdr_filename))

    # Convert "smart" dictionary items into strings that are
    # ready to be saved to the .hdr text file.
    header_output = []
    header_output.append('DATASET {}'.format(output_hdr_filename_root.upper()))
    header_output.append('VERSION {}'.format(header_data['version']))
    header_output.append('SERIES ' + ','.join(
        header_data['series_labels']) + ' ')
    header_output.append(
        'DATE ' + header_data['recording_start_datetime'].strftime('%m-%d-%Y'))
    header_output.append(
        'TIME ' +
        header_data['recording_start_datetime'].strftime('%H:%M:%S.%f')[0:11])
    header_output.append('RATE ' + str(header_data['sampling_frequency_hz']))
    header_output.append(
        'VERT_UNITS ' + ','.join(header_data['vertical_units']) + ' ')
    header_output.append(
        'HORZ_UNITS {}'.format(header_data['horizontal_units']))
    header_output.append('COMMENT {}'.format(header_data['comment']))
    header_output.append(
        'NUM_SERIES {}'.format(header_data['number_of_series']))
    header_output.append('STORAGE_MODE {}'.format(header_data['storage_mode']))
    header_output.append('FILE_TYPE {}'.format(header_data['file_type']))
    header_output.append(
        'SLOPE ' + ','.join([_format_exponent_notation(slope, 6, 3)
                            for slope in header_data['slope']]) + ' ')
    header_output.append('X_OFFSET {:1.1f}'.format(header_data['x_offset']))
    header_output.append(
        'Y_OFFSET ' + ','.join([_format_exponent_notation(y_offset, 6, 3)
                               for y_offset in header_data['y_offset']]) + ' ')
    header_output.append('NUM_SAMPS {}'.format(
                         header_data['number_of_samples']))
    header_output.append('DATA')
    header_output.append('DEVICE {}'.format(header_data['device']))
    header_output.append('SLOT1_AMP {id},{num_ch},{pld_ver},{fw_ver}'.format(
        id=header_data['slot1_amp']['id_name'],
        num_ch=header_data['slot1_amp']['num_of_channels'],
        pld_ver=header_data['slot1_amp']['pld_version'].ljust(8),
        fw_ver=header_data['slot1_amp']['firmware_version'].ljust(8)))
    header_output.append('SLOT2_AMP {id},{num_ch},{pld_ver},{fw_ver}'.format(
        id=header_data['slot2_amp']['id_name'],
        num_ch=header_data['slot2_amp']['num_of_channels'],
        pld_ver=header_data['slot2_amp']['pld_version'].ljust(8),
        fw_ver=header_data['slot2_amp']['firmware_version'].ljust(8)))
    for index in range(header_data['number_of_series']):
        channel_key = 'CH{channel_num}_{channel_num}'.format(
            channel_num=index + 1)
        header_output.append(
            '{channel_key} {amp_type},{range_setting},{filter_setting}'.format(
                channel_key=channel_key,
                amp_type=header_data['channel_info'][index]['amp_type'],
                range_setting=header_data[
                    'channel_info'][index]['range_setting'],
                filter_setting=header_data[
                    'channel_info'][index]['filter_setting']))
    header_output.append('ID_NO {id_num}'.format(id_num=header_data['id_num']))
    header_output.append('TIME {start},{end}'.format(
        start=header_data['start_time'],
        end=header_data['stop_time']))
    header_output.append('REC_MODE {rec_mode} '.format(
        rec_mode=header_data['recording_destination']))
    header_output.append('START_TRIGGER {trigger}  '.format(
        trigger=header_data['start_trigger']))
    header_output.append('STOP_CONDITION {condition}  '.format(
        condition=header_data['stop_condition']))
    header_output.append('ID_END')
    if header_data['voice_memo_on']:
        header_output.append('VOICE_MEMO {bits},{size}'.format(
            bits=header_data['voice_memo_bits_per_sample'],
            size=header_data['voice_memo_size_bytes']))
    header_output.append('{model}_VERSION {ver}'.format(
        model=header_data['recorder_model'],
        ver=header_data['recorder_version']))
    header_output.append('MEMO_LENGTH {memo_len}'.format(
        memo_len=header_data['memo_length']))
    header_output.append('MEMO {memo}'.format(memo=header_data['memo']))
    header_output.append('')

    header_output = _append_windows_newlines(header_output)

    # Write the .hdr file
    with open(output_hdr_filename, 'w') as f_header:
        f_header.writelines(header_output)

    return


def _write_taffmat_dat(data_array, number_of_series, slope, y_offset,
                       output_dat_filename):
    '''
    Write the .dat TAFFmat file
    WARNING: Changes data_array in calling code!!!
    '''

    # Convert data_array into int16 values by removing the offset
    # and slope, such that +/-100% = +/-25,000 int16
    data_array = _remove_slope_and_offset(
        data_array, number_of_series, slope, y_offset)

    # Write the binary data file.
    with open(output_dat_filename, 'wb') as datfile:
        data_array.T.reshape((-1, number_of_series)).tofile(datfile)

    return


def read_taffmat(input_file):
    '''Read the TAFFmat .hdr and .dat files

    Read the Teac TAFFmat text header file (.hdr) and the binary
    data file (.dat).

    Args:
        input_file: Filename consisting of either just the base
            filename or can include the .dat or .hdr suffix

    Returns:
        A tuple containing the data_array (ndarray with shape
        of series x num_samples),
        time_vector (ndarray), and header_data (dictionary)

    Raises:
        N/A
    '''
    # If the input_file contains the extension .dat or .hdr,
    # strip that off to create the input_file_basename
    # and then create both the .dat and .hdr filenames
    input_file_basename, input_file_extension = os.path.splitext(
        input_file)

    if input_file_extension.lower() in ['.dat', '.hdr']:
        # The input_file contained the extension of .dat or .hdr
        input_dat_file = '{base}.DAT'.format(base=input_file_basename)
        input_hdr_file = '{base}.HDR'.format(base=input_file_basename)
    else:
        # The input_file didn't contain an extension, so append .dat and .hdr
        # TODO: Add unit tests to make sure we're properly handling
        # input_file with .dat, .hdr, or no extension
        input_dat_file = '{base}.DAT'.format(base=input_file)
        input_hdr_file = '{base}.HDR'.format(base=input_file)

    if (not os.path.isfile(input_dat_file) or
            not os.path.isfile(input_hdr_file)):
        # The .dat or .hdr file doesn't exist, so exit
        # FIXME(mdr): Throw an exception with a reasonable error!!!
        # Right now I'll get "TypeError: 'bool' object is not iterable"
        # if the file doesn't exist. That wasted 15 minutes.
        # FIXME: What error code, if any should I be returning?
        # sys.exit('Input files do not exist')
        return False

    # Read the hdr file
    header_data = _read_taffmat_hdr(input_hdr_file)

    # Read the dat file
    data_array = _read_taffmat_dat(
        input_dat_file, header_data['file_type'],
        header_data['number_of_series'],
        header_data['slope'],
        header_data['y_offset'])

    # Create the time vector
    time_vector = np.linspace(
        0,
        (header_data['number_of_samples'] /
            header_data['sampling_frequency_hz']),
        header_data['number_of_samples'])

    # Return a tuple
    return (data_array, time_vector, header_data)


def write_taffmat(data_array, header_data, output_base_filename):
    '''
    Write the TAFFmat .dat and .hdr files
    '''

    # Determine the output file names
    output_hdr_filename = '{base}.HDR'.format(base=output_base_filename)
    output_dat_filename = '{base}.DAT'.format(base=output_base_filename)

    _write_taffmat_hdr(header_data, output_hdr_filename)
    _write_taffmat_dat(data_array, header_data['number_of_series'],
                       header_data['slope'], header_data['y_offset'],
                       output_dat_filename)

    return


def write_taffmat_slice(data_array, header_data, output_base_filename,
                        starting_data_index, ending_data_index):
    '''
    Write the TAFFmat .dat and .hdr given the starting and ending
    data points to include in the .dat file.

    The only change to the .hdr file from the given header_data
    dictionary is that the number of samples will be recalculated
    based on the starting and ending data points to be written.
    '''

    # TODO(mdr): Add a check to determine if the data_array is beyond
    # the range in the header.and if so log it.

    # Since slices are simply views into the original array, we need
    # to copy the array before performing the ADC conversion required
    # by the LX-10 when storing data as integers.
    data_array_copy = data_array.copy()

    # Create copies of the originals
    sliced_data_array = data_array_copy[
        :, starting_data_index:ending_data_index+1]
    sliced_header_data = header_data

    # Calculate number of samples
    new_number_of_samples = ending_data_index + 1 - starting_data_index

    # Update header_data with the new number of samples
    sliced_header_data['number_of_samples'] = new_number_of_samples

    # Since we're saving a slice, the voice memo will not be the
    # same length, so just disable the voice memo (i.e., remove
    # VOICE_MEMO line from .HDR file)
    sliced_header_data['voice_memo_on'] = False

    # Rename the DATASET to the new filename
    sliced_header_data['dataset'] = (
        os.path.basename(output_base_filename).upper())

    # Write the sliced TAFFmat data
    write_taffmat(sliced_data_array, sliced_header_data, output_base_filename)

    return
