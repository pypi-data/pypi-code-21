# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime


# NOTE: some older files have spaces (or other odd characters) in their header names
# This function is intended to get rid of those pesky issues and normalize the names
def _normalize_header_names(df):
    for col_name in df.columns:
        new_name = col_name.strip()
        new_name = new_name.replace(' ', '')
        new_name = new_name.replace('(', '_')
        new_name = new_name.replace(')', '')
        new_name = new_name.replace('.', '')
        new_name = new_name.replace('\xb0', '')  # unicode degrees symbol
        new_name = new_name.lower()
        if (new_name != col_name):
            df.rename(columns = {col_name: new_name}, inplace=True)

def _parse_header_line(line_str):
    key = None
    val = None
    pieces = line_str.split(':', 1)
    if len(pieces) > 0:
        key = pieces[0].strip()
    if len(pieces) > 1:
        val = pieces[1].strip()
    
    return key, val

def get_header_row_count(filepath):
    header_row_count = -1
    with open(filepath, 'r') as fid:
        # first line *should* always be the number of header rows
        line = fid.readline()
        k, v = _parse_header_line(line)
        if k != 'Header Rows':
            header_row_count = 1
            while ':' in line:
                line = fid.readline()
                header_row_count += 1
        else:
            header_row_count = int(v)

    return header_row_count

def get_header_data(filepath):
    header_row_count = get_header_row_count(filepath)
    
    header = {}
    with open(filepath, 'r') as fid:
        line_number = 1

        while line_number < header_row_count:
            line = fid.readline()
            k, v = _parse_header_line(line)
            header[k] = v

            line_number += 1

    return header


def parse_eng_tools_log(filepath):

    df = pd.read_csv(filepath, parse_dates=['timestamp'])
    _normalize_header_names(df)

    # calculate elapsed time values
    df['elapsedtime'] = pd.to_timedelta(df['timestamp']).dt.seconds.astype(float)
    df['elapsedtime'] = df['elapsedtime'] - df['elapsedtime'][0]
    
    return df


def parse_experiment_file(filepath):

    header_row_count = get_header_row_count(filepath)
    header_data = get_header_data(filepath)

    df = pd.read_csv(filepath, parse_dates=['elapsedtime'], skiprows=header_row_count-1)
    _normalize_header_names(df)   

    # convert from time type to float (as seconds)
    df.elapsedtime = pd.to_timedelta(df.elapsedtime).dt.seconds.astype(float)

    # add header data to dataframe
    for k, v in header_data.items():
        df[k] = v

    # add Timestamp entry to dataset (StartDate + ElapsedTime)
    start_date = 0   
    if 'Start Date' in header_data:
        start_date_str = header_data['Start Date']
        start_date = datetime.strptime(start_date_str, '%m/%d/%Y %I:%M:%S %p')
    df['timestamp'] = start_date
    df['timestamp'] = df['timestamp'] + pd.to_timedelta(df['elapsedtime'])
    
    return df        


def parse_analysis_file(filepath):

    header_row_count = get_header_row_count(filepath)
    header_data = get_header_data(filepath)

    df = pd.read_csv(filepath, header=header_row_count-1)

    # add header data to dataframe
    for k, v in header_data.items():
        df[k] = v

    _normalize_header_names(df)
    df.rename(columns = {
            'elapsedtime_sec': 'elapsedtime',
            'time_sec': 'elapsedtime',
            'temperature_c': 'temperature',
            'stirringspeed_rpm': 'stirringspeed',
            'ndfiltervalue': 'ndfilter',
            'relmolweight': 'mwnorm',
            'absmolweight': 'mwabs',
            'arfitresidual': 'arresidual',
            }, inplace=True)

    # add Timestamp entry to dataset (StartDate + ElapsedTime)
    #start_date = 0   
    #if 'Start Date' in header_data:
    #    start_date_str = header_data['Start Date']
    #    start_date = datetime.strptime(start_date_str, '%m/%d/%Y %I:%M:%S %p')
    #df['timestamp'] = start_date
    #df['timestamp'] = df['timestamp'] + pd.to_timedelta(df['elapsedtime'], unit='s')
    
    return df 
