
import re
import pandas as pd
import numpy as np
import dero

from .ext_pandas import groupby_merge

def load_log_and_produce_timing_dfs(filepath):
    """
    Loads a dero log from filepath and returns a tuple of two pandas dataframes, where the
    first is a listing of each function in order and the amount of time it took,
    and the second is a summary df which sums and averages times by functions (across
    multiple calls)
    """
    with open(filepath, 'r') as f:
        log_list = f.readlines()

    df = parse_logs_for_timing(log_list)
    summ_df = summary_timing_df(df)
    
    return df, summ_df

def compare_log_timing(filepaths, substrings):
    r"""
    Loads multiple logs and produces a summary df with how total and average times per functions on the
    different runs. Use substrings to identify which sample is which.
    
    Required inputs:
    filepaths: list of strs, locations of logs
    substrings: list of strs, must be same length as filepaths list, identifies each sample
    
    Usage:
    filepaths = [
    r'C:\Users\derobertisna.UFAD\Dropbox\UF\Investor Attention\Python\2016-08-08 23.37.24 ia.debug', #20 subset
    r'C:\Users\derobertisna.UFAD\Dropbox\UF\Investor Attention\Python\2016-08-09 00.02.53 ia.debug' #200 subset
    ]
    substrings = ['20', '200']

    dero.logtimer.compare_log_timing(filepaths, substrings)
    
    """
    df_tups = [load_log_and_produce_timing_dfs(fp) for fp in filepaths]
    summ_dfs = [tup[1] for tup in df_tups]
    
    for i, summ_df in enumerate(summ_dfs):
        suff = substrings[i] #get suffix
        summ_df = summ_df.rename(columns={'time_sum':'time_sum' + suff, 'time_mean':'time_mean' + suff})
        if i == 0:
            alldf = summ_df.copy()
            continue
        alldf = alldf.merge(summ_df, on='function', how='outer')
    
    diff_col = 'diff_' + substrings[0] + '_' + substrings[-1]
    alldf[diff_col] = alldf['time_sum' + substrings[-1]] - alldf['time_sum' + substrings[0]]
    return alldf.sort_values(diff_col, ascending=False)

def _parse_log_entry(l):
    """
    Returns an re match object with the contents:
    
    First group: timestamp
    2: module name
    3: logging level
    4: message
    """
    pattern = re.compile(r'(\d*-\d*-\d* \d*:\d*:\d*,\d*) - ([\w.]+) - (\w*) - (.+)')
    return pattern.match(l)

def _parse_timing_entry(l):
    """
    Returns a tuple of full function name, time elapsed strings 
    """
    match = _parse_log_entry(l)
    if not match: return None
    timing_pattern = re.compile(r'([\w.]+) took (.+)[.]')
    function_time = timing_pattern.match(match.group(4))
    if not function_time: return None
    full_function_str = match.group(2) + '.' +  function_time.group(1)
    return full_function_str, function_time.group(2)

def _parse_logs_for_timing(log_list):
    """
    Returns a list of tuples of full function name, time elapsed strings
    """
    return list(filter(lambda x: x, [_parse_timing_entry(l) for l in log_list]))

def parse_logs_for_timing(log_list):
    """
    Returns a tuple of two pandas dataframes, where the first is
    full function name, time elapsed
    and the 
    """
    df = pd.DataFrame(_parse_logs_for_timing(log_list), columns=['function','time'])
    df['time'] = pd.to_timedelta(df['time']).apply(lambda x: x.total_seconds())
    return df.sort_values('time', ascending=False).reset_index().rename(columns={'index':'orig order'})

def summary_timing_df(parsed_df):
    df = groupby_merge(parsed_df, 'function', 'sum', subset='time')
    df = groupby_merge(df, 'function', 'mean', subset='time')
    return df.drop(['time','orig order'], axis=1).drop_duplicates(
        ).sort_values('time_sum', ascending=False)
