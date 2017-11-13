
import os
import pandas as pd
import datetime
from numpy import nan
from dateutil.relativedelta import relativedelta
import sys
import numpy as np
import warnings, timeit
from sas7bdat import SAS7BDAT
import statsmodels.api as sm
from pandas.tseries.offsets import CustomBusinessDay
from multiprocessing.dummy import Pool as ThreadPool
from tkinter import Tk, Frame, BOTH, YES
from pandastable import Table
from itertools import chain

def to_csv(dataframe, path, filename, output=True, action='w', index=True):
    '''
    action='w' for overwrite, 'a' for append
    set index to False to not include index in output
    '''   
    if action == 'a':
        headers = False
    else:
        headers = True
    
    if dataframe is not None: #if dataframe exists
        filepath = os.path.join(path,filename + '.csv')
        f = open(filepath, action, encoding='utf-8')
        if output is True: print("Now saving %s" % filepath)
        try: f.write(dataframe.to_csv(encoding='utf-8', index=index, header=headers)) #could use easier dataframe.to_csv(filepath) syntax, but won't overwrite
        except: f.write(dataframe.to_csv(encoding='utf-8', index=index, header=headers).replace('\ufffd',''))
        f.close()
    else:
        print("{} does not exist.".format(dataframe)) #does nothing if dataframe doesn't exist
    
def convert_sas_date_to_pandas_date(sasdates):
    epoch = datetime.datetime(1960, 1, 1)
    
    if isinstance(sasdates, pd.Series):
        return pd.Series([epoch + datetime.timedelta(days=int(float(date))) if not pd.isnull(date) else nan for date in sasdates])
    else:
        return epoch + datetime.timedelta(days=sasdates)
    
def year_month_from_date(df, date='Date'):
    '''
    Takes a dataframe with a datetime object and creates year and month variables
    '''
    df = df.copy()
    df['Year'] =  [date.year  for date in df[date]]
    df['Month'] = [date.month for date in df[date]]
    
    return df

def expand_time(df, intermediate_periods=False, **kwargs):
    """
    Creates new observations in the dataset advancing the time by the int or list given. Creates a new date variable.
    See _expand_time for keyword arguments.
    
    Specify intermediate_periods=True to get periods in between given time periods, e.g.
    passing time=[12,24,36] will get periods 12, 13, 14, ..., 35, 36. 
    """
    
    if intermediate_periods:
        assert 'time' in kwargs
        time = kwargs['time']
        time = [t for t in range(min(time),max(time) + 1)]
        kwargs['time'] = time
    return _expand_time(df, **kwargs)

def _expand_time(df, datevar='Date', freq='m', time=[12, 24, 36, 48, 60], newdate='Shift Date', shiftvar='Shift'):
    '''
    Creates new observations in the dataset advancing the time by the int or list given. Creates a new date variable.
    '''
    def log(message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    log('Initializing expand_time for periods {}.'.format(time))
    
    if freq == 'd':
        log('Daily frequency, getting trading day calendar.')
        td = tradedays() #gets trading day calendar
    else:
        td = None
    
    def time_shift(shift, freq=freq, td=td):
        if freq == 'm':
            return relativedelta(months=shift)
        if freq == 'd':
            return shift * td
        if freq == 'a':
            return relativedelta(years=shift)
    
    if isinstance(time, int):
        time = [time]
    else: assert isinstance(time, list)
    
    
    log('Calculating number of rows.')
    num_rows = len(df.index)
    log('Calculating number of duplicates.')
    duplicates = len(time)
    
    #Expand number of rows
    if duplicates > 1:
        log('Duplicating observations {} times.'.format(duplicates - 1))
        df = df.append([df] * (duplicates - 1)).sort_index().reset_index(drop=True)
        log('Duplicated.')
    
    log('Creating shift variable.')
    df[shiftvar] = time * num_rows #Create a variable containing amount of time to shift
    #Now create shifted date
    log('Creating shifted date.')
    df[newdate] = [date + time_shift(int(shift)) for date, shift in zip(df[datevar],df[shiftvar])]
    log('expand_time completed.')
    
    #Cleanup and exit
    return df #.drop('Shift', axis=1)

def cumulate(df, cumvars, method, periodvar='Date',  byvars=None, time=None, grossify=False):
    """
    Cumulates a variable over time. Typically used to get cumulative returns. 
    
    NOTE: Method zero not yet working
    
    method = 'between', 'zero', or 'first'. 
             If 'zero', will give returns since the original date. Note: for periods before the original date, 
             this will turn positive returns negative as we are going backwards in time.
             If 'between', will give returns since the prior requested time period. Note that
             the first period is period 0.
             If 'first', will give returns since the first requested time period.
             For example, if our input data was for date 1/5/2006, but we had shifted dates:
                 permno  date      RET  shift_date
                 10516   1/5/2006  110%  1/5/2006
                 10516   1/5/2006  120%  1/6/2006
                 10516   1/5/2006  105%  1/7/2006
                 10516   1/5/2006  130%  1/8/2006
             Then cumulate(df, 'RET', cumret='between', time=[1,3], get='RET', periodvar='shift_date') would return:
                 permno  date      RET  shift_date  cumret
                 10516   1/5/2006  110%  1/5/2006    110%
                 10516   1/5/2006  120%  1/6/2006    120%
                 10516   1/5/2006  105%  1/7/2006    126%
                 10516   1/5/2006  130%  1/8/2006    130%
             Then cumulate(df, 'RET', cumret='first', periodvar='shift_date') would return:
                 permno  date      RET  shift_date  cumret
                 10516   1/5/2006  110%  1/5/2006    110%
                 10516   1/5/2006  120%  1/6/2006    120%
                 10516   1/5/2006  105%  1/7/2006    126%
                 10516   1/5/2006  130%  1/8/2006    163.8%
    byvars: string or list of column names to use to seperate by groups
    time: list of ints, for use with method='between'. Defines which periods to calculate between.
    grossify: bool, set to True to add one to all variables then subtract one at the end
    """    
    def log(message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    log('Initializing cumulate.')
    
    df = df.copy() #don't want to modify original dataframe
    
    if time:
        sort_time = sorted(time)
    else: sort_time = None
        
    if isinstance(cumvars, (str, int)):
        cumvars = [cumvars]
    assert isinstance(cumvars, list)

    assert isinstance(grossify, bool)
    
    if grossify:
        for col in cumvars:
            df[col] = df[col] + 1
        
    def create_windows(periods, method=method, time=sort_time):
        if method.lower() == 'first':
            windows = [[0]]
            windows += [[i for i in range(1, len(periods))]]
            return windows
        elif method.lower() == 'between':
            windows = [[0]]
            t_bot = 0
            for i, t in enumerate(time): #pick each element of time
                if t == 0: continue #already added zero
                windows.append([i for i in range(t_bot + 1, t + 1)])
                t_bot = t
            #The last window is all the leftover periods after finishing time
            extra_windows = [[i for i, per in enumerate(periods) if i not in chain.from_iterable(windows)]]
            if extra_windows != [[]]: #don't want to add empty window
                windows += extra_windows
            return windows
        elif method.lower() == 'zero':
            windows = []
            windows.append(periods[:periods.index(0) + 1]) #add times before 0, as well as 0
            windows.append([0]) #add 0
            windows.append(periods[periods.index(0) + 1:]) #add times after 0
            return windows
    
    def unflip(df, cumvars):
        flipcols = ['cum_' + str(c) for c in cumvars] #select cumulated columns
        for col in flipcols:
            tempdf[col] = tempdf[col].shift(1) #shift all values down one row for cumvars
            tempdf[col] = -tempdf[col] + 2 #converts a positive return into a negative return
        tempdf = tempdf[1:].copy() #drop out period 0
        tempdf = tempdf.sort_values(periodvar) #resort to original order
        
    def flip(df, flip):
        flip_df = df[df['window'].isin(flip)]
        rest = df[~df['window'].isin(flip)]
        flip_df = flip_df.sort_values(byvars + [periodvar], ascending=False)
        return pd.concat([flip_df, rest], axis=0)
    
    def _cumulate2(array_list):
        out_list = []
        for array in array_list:
            out_list.append(np.cumprod(array, axis=0))
        return np.concatenate(out_list, axis=0)

    def split(df, cumvars, periodvar):
        """
        Splits a dataframe into a list of arrays based on a key variable
        """
        df = df.sort_values(['__key_var__', periodvar])
        small_df = df[['__key_var__'] + cumvars]
        arr = small_df.values
        splits = []
        for i in range(arr.shape[0]):
            if i == 0: continue
            if arr[i,0] != arr[i-1,0]: #different key
                splits.append(i)
        return np.split(arr[:,1:], splits)
    
    def window_mapping(col):
        """
        Takes a pandas series of dates as inputs, calculates windows, and returns a series of which
        windows each observation are in. To be used with groupby.transform()
        """
        windows = create_windows(col)
        return [n for i in range(len(col.index)) for n, window in enumerate(windows) if i in window]
    
    def map_windows(df, periodvar=periodvar, byvars=byvars):
        """
        Returns the dataframe with an additional column __map_window__ containing the index of the window 
        in which the observation resides. For example, if the windows are
        [[1],[2,3]], and the periods are 1/1/2000, 1/2/2000, 1/3/2000 for PERMNO 10516 with byvar
        'a', the df rows would be as follows:
             (10516, 'a', '1/1/2000', 0),
             (10516, 'a', '1/2/2000', 1),
             (10516, 'a', '1/3/2000', 1),
        """
        
        df = df.copy() #don't overwrite original dataframe
        
        df = groupby_merge(df, byvars, 'transform', (window_mapping), subset=periodvar)
        
        return df.rename(columns={periodvar + '_transform': '__map_window__'})
        
    
    #####TEMPORARY CODE######
    assert method.lower() != 'zero'
    #########################
    
    if isinstance(byvars, str):
        byvars = [byvars]
    
    assert method.lower() in ('zero','between','first')
    assert not ((method.lower() == 'between') and (time == None)) #need time for between method
    if time != None and method.lower() != 'between':
        warnings.warn('Time provided but method was not between. Time will be ignored.')
    
#     periods = df[periodvar].unique().tolist()
#     windows = create_windows(periods)
    
#     df['window_key'] = df[periodvar].apply(lambda x: [x in window for window in windows].index(True))

    #Creates a variable containing index of window in which the observation belongs
    df = map_windows(df)
    
    if not byvars:  byvars = ['__map_window__']
    else: byvars.append('__map_window__')
    assert isinstance(byvars, list)
    
    #need to determine when to cumulate backwards
    #check if method is zero, there only negatives and zero, and there is at least one negative in each window
    if method.lower() == 'zero': 
        #flip is a list of indices of windows for which the window should be flipped
        flip = [j for j, window in enumerate(windows) \
               if all([i <= 0 for i in window]) and any([i < 0 for i in window])]
        df = flip(df, flip)
        

    log('Creating by groups.')

    #Create by groups
    df['__key_var__'] = '__key_var__' #container for key
    for col in [df[c].astype(str) for c in byvars]:
        df['__key_var__'] += col

    array_list = split(df, cumvars, periodvar)
    
#     container_array = df[cumvars].values
    full_array = _cumulate2(array_list)
    
    new_cumvars = ['cum_' + str(c) for c in cumvars]

    cumdf = pd.DataFrame(full_array, columns=new_cumvars, dtype=np.float64)
    outdf = pd.concat([df, cumdf], axis=1)
    
    if method.lower == 'zero' and flip != []: #if we flipped some of the dataframe
        pass #TEMPORARY
    
    
    
    if grossify:
        all_cumvars = cumvars + new_cumvars
        for col in all_cumvars:
            outdf[col] = outdf[col] - 1
    
    drop_cols = [col for col in outdf.columns if col.startswith('__')]
    
    return outdf.drop(drop_cols, axis=1)

def long_to_wide(df, groupvars, values, colindex=None):
    '''
    
    groupvars = string or list of variables which signify unique observations in the output dataset
    values = string or list of variables which contain the values which need to be transposed
    colindex = variable containing extension for column name in the output dataset. If not specified, just uses the
               count of the row within the group.
    
    NOTE: Don't have any variables named key or idx
    
    For example, if we had a long dataset of returns, with returns 12, 24, 36, 48, and 60 months after the date:
            ticker    ret    months
            AA        .01    12
            AA        .15    24
            AA        .21    36
            AA       -.10    48
            AA        .22    60
    and we want to get this to one observation per ticker:
            ticker    ret12    ret24    ret36    ret48    ret60    
            AA        .01      .15      .21     -.10      .22
    We would use:
    long_to_wide(df, groupvars='ticker', values='ret', colindex='months')
    '''
    
    df = df.copy() #don't overwrite original
    
    #Check for duplicates
    if df.duplicated().any():
        df.drop_duplicates(inplace=True)
        warnings.warn('Found duplicate rows and deleted.')
    
    #Ensure type of groupvars is correct
    if isinstance(groupvars,str):
        groupvars = [groupvars]
    assert isinstance(groupvars, list)
    
    #Ensure type of values is correct
    if isinstance(values,str):
        values = [values]
    assert isinstance(values, list)
    #Use count of the row within the group for column index if not specified
    if colindex == None:
        df['__idx__'] = df.groupby(groupvars).cumcount()
        colindex = '__idx__'
    
    df['__key__'] = df[groupvars[0]].astype(str) #create key variable
    if len(groupvars) > 1: #if there are multiple groupvars, combine into one key
        for var in groupvars[1:]:
            df['__key__'] = df['__key__'] + '_' + df[var].astype(str)
    
    #Create seperate wide datasets for each value variable then merge them together
    for i, value in enumerate(values):
        if i == 0:
            combined = df.copy()
        #Create wide dataset
        raw_wide = df.pivot(index='__key__', columns=colindex, values=value)
        raw_wide.columns = [value + str(col) for col in raw_wide.columns]
        wide = raw_wide.reset_index()

        #Merge back to original dataset
        combined = combined.merge(wide, how='left', on='__key__')
    
    return combined.drop([colindex,'__key__'] + values, axis=1).drop_duplicates().reset_index(drop=True)

def load_sas(filepath, csv=True):  
    sas_name = os.path.basename(filepath) #e.g. dsename.sas7bdat
    folder = os.path.dirname(filepath) #location of sas file
    filename, extension = os.path.splitext(sas_name) #returns ('dsenames','.sas7bdat')
    csv_name = filename + '.csv'
    csv_path = os.path.join(folder, csv_name)
    
    if os.path.exists(csv_path) and csv:
        if os.path.getmtime(csv_path) > os.path.getmtime(filepath): #if csv was modified more recently
            #Read from csv (don't touch sas7bdat because slower loading)
            try: return pd.read_csv(csv_path, encoding='utf-8')
            except UnicodeDecodeError: return pd.read_csv(csv_path, encoding='cp1252')
    
    #In the case that there is no csv already, or that the sas7bdat has been modified more recently
    #Pull from SAS file
    df = SAS7BDAT(filepath).to_data_frame()
    #Write to csv file
    if csv:
        to_csv(df, folder, filename, output=False, index=False)
    return df

def averages(df, avgvars, byvars, wtvar=None, flatten=True):
    '''
    Returns equal- and value-weighted averages of variables within groups
    
    avgvars: List of strings or string of variable names to take averages of
    byvars: List of strings or string of variable names for by groups
    wtvar: String of variable to use for calculating weights in weighted average
    flatten: Boolean, False to return df with multi-level index
    '''
    #Check types
    assert isinstance(df, pd.DataFrame)
    if isinstance(avgvars, str): avgvars = [avgvars]
    else:
        assert isinstance(avgvars, list)
    assert isinstance(byvars, (str, list))
    if wtvar != None:
        assert isinstance(wtvar, str)
    
    df = df.copy()
    g = df.groupby(byvars)
    avg_df  = g.mean()[avgvars]
    
    if wtvar == None:
        if flatten:
            return avg_df.reset_index()
        else:
            return avg_df
    
    for var in avgvars:
        colname = var + '_wavg'
        df[colname] = df[wtvar] / g[wtvar].transform('sum') * df[var]
    
    wavg_cols = [col for col in df.columns if col[-4:] == 'wavg']
    
    g = df.groupby(byvars) #recreate because we not have _wavg cols in df
    wavg_df = g.sum()[wavg_cols]
    
    outdf = pd.concat([avg_df,wavg_df], axis=1)
    
    if flatten:
        return outdf.reset_index()
    else:
        return outdf
    
def portfolio(df, groupvar, ngroups=10, byvars=None, cutdf=None, portvar='portfolio'):
    '''
    Constructs portfolios based on percentile values of groupvar. If ngroups=10, then will form 10 portfolios,
    with portfolio 1 having the bottom 10 percentile of groupvar, and portfolio 10 having the top 10 percentile
    of groupvar.
    
    df: pandas dataframe, input data
    groupvar: string, name of variable in df to form portfolios on
    ngroups: integer, number of portfolios to form
    byvars: string, list, or None, name of variable(s) in df, finds portfolios within byvars. For example if byvars='Month',
            would take each month and form portfolios based on the percentiles of the groupvar during only that month
    cutdf: pandas dataframe or None, optionally determine percentiles using another dataset
    portvar: string, name of portfolio variable in the output dataset
    
    NOTE: Resets index and drops in output data, so don't use if index is important (input data not affected)
    '''
    #Check types
    assert isinstance(df, pd.DataFrame)
    assert isinstance(groupvar, str)
    assert isinstance(ngroups, int)
    if byvars != None:
        if isinstance(byvars, str): byvars = [byvars]
        else:
            assert isinstance(byvars, list)
    if cutdf != None:
        assert isinstance(cutdf, pd.DataFrame)
    else: #this is where cutdf == None, the default case
        cutdf = df
        tempcutdf = cutdf.copy()
        
    def sort_into_ports(df, cutoffs, portvar=portvar, groupvar=groupvar):
        df[portvar] = 0
        for i, (low_cut, high_cut) in enumerate(zip(cutoffs[:-1],cutoffs[1:])):
                rows = df[(outdf[groupvar] >= low_cut) & (df[groupvar] <= high_cut)].index
                df.loc[rows, portvar] = i + 1
        return df

    outdf = df.copy().reset_index(drop=True)
    
    pct_per_group = int(100/ngroups)
    percentiles = [i for i in range(0, 100 + ngroups, pct_per_group)] #percentile values, e.g. 0, 10, 20, 30... 100

    if byvars == None:
        cutoffs = [np.percentile(cutdf[groupvar], i) for i in percentiles] #values of variable associated with percentiles
        return sort_into_ports(outdf, cutoffs)
    else: #here we have to deal with byvars
        #First create a key variable based on all the byvars
        outdf['key'] = 'key' #container for key
        tempcutdf['key'] = 'key'
        for col in [outdf[c].astype(str) for c in byvars]:
            outdf['key'] += col
            tempcutdf['key'] += col
        key_list = outdf['key'].unique().tolist()
        #Now calculate cutoffs. We will have one set of cutoffs for each key.
        outdf2 = pd.DataFrame()
        for key in key_list:
            keydf =    outdf[outdf['key'] == key].copy()
            keycutdf = tempcutdf[tempcutdf['key'] == key]
            cutoffs = [np.percentile(tempcutdf[groupvar], i) for i in percentiles]
            keydf = sort_into_ports(keydf, cutoffs)
            outdf2 = outdf2.append(keydf)
            
        outdf2.drop('key', axis=1, inplace=True)
            
        return outdf2.sort_index()
    
def portfolio_averages(df, groupvar, avgvars, ngroups=10, byvars=None, cutdf=None, wtvar=None,
                       portvar='portfolio', avgonly=False):
    '''
    Creates portfolios and calculates equal- and value-weighted averages of variables within portfolios. If ngroups=10,
    then will form 10 portfolios, with portfolio 1 having the bottom 10 percentile of groupvar, and portfolio 10 having 
    the top 10 percentile of groupvar.
    
    df: pandas dataframe, input data
    groupvar: string, name of variable in df to form portfolios on
    avgvars: string or list, variables to be averaged
    ngroups: integer, number of portfolios to form
    byvars: string, list, or None, name of variable(s) in df, finds portfolios within byvars. For example if byvars='Month',
            would take each month and form portfolios based on the percentiles of the groupvar during only that month
    cutdf: pandas dataframe or None, optionally determine percentiles using another dataset
    wtvar: string, name of variable in df to use for weighting in weighted average
    portvar: string, name of portfolio variable in the output dataset
    avgonly: boolean, True to return only averages, False to return (averages, individual observations with portfolios)
    
    NOTE: Resets index and drops in output data, so don't use if index is important (input data not affected)
    '''
    ports = portfolio(df, groupvar, ngroups=ngroups, byvars=byvars, cutdf=cutdf, portvar=portvar)
    if byvars:
        assert isinstance(byvars, (str, list))
        if isinstance(byvars, str): byvars = [byvars]
        by = [portvar] + byvars
        avgs = averages(ports, avgvars, byvars=by, wtvar=wtvar)
    else:
        avgs = averages(ports, avgvars, byvars=portvar, wtvar=wtvar)
    
    if avgonly:
        return avgs
    else:
        return avgs, ports
    
def reg_by(df, yvar, xvars, groupvar, merge=False):
    """
    Runs a regression of df[yvar] on df[xvars] by values of groupvar. Outputs a dataframe with values of 
    groupvar and corresponding coefficients, unless merge=True, then outputs the original dataframe with the
    appropriate coefficients merged in.
    """   
    result_df = pd.DataFrame()
    
    if isinstance(xvars, str):
        xvars = [xvars]
    assert isinstance(xvars, list)
    
    for group in df[groupvar].unique():
        tempdf = df[df[groupvar] == group][xvars + [yvar]].dropna() #will fail with nans
        X = tempdf[xvars]
        y = tempdf[yvar]

        model = sm.OLS(y, X)
        result = model.fit()
        
        this_result = pd.DataFrame(result.params).T
        this_result[groupvar] = group

        result_df = result_df.append(this_result) #  Or whatever summary info you want
    
    result_df.columns = ['coef_' + col if col != groupvar else col for col in result_df.columns]
    
    if merge:
        return df.merge(result_df, how='left', on=groupvar)
    
    return result_df.reset_index(drop=True)

def factor_reg_by(df, groupvar, fac=4):
    """
    Takes a dataframe with RET, mktrf, smb, hml, and umd, and produces abnormal returns by groups.
    """
    assert fac in (1, 3, 4)
    factors = ['mktrf']
    if fac >= 3:
        factors += ['smb','hml']
    if fac == 4:
        factors += ['umd']
        
    factor_loadings = reg_by(df, 'RET', factors, groupvar)
    outdf = df.merge(factor_loadings, how='left', on=groupvar) #merge back to sample
    outdf['ABRET'] = outdf['RET'] - sum([outdf[fac] * outdf['coef_' + fac] for fac in factors]) #create abnormal returns
    return outdf

def state_abbrev(df, col, toabbrev=False):
    df = df.copy()
    states_to_abbrev = {
    'Alabama': 'AL', 
    'Montana': 'MT',
    'Alaska': 'AK', 
    'Nebraska': 'NE',
    'Arizona': 'AZ', 
    'Nevada': 'NV',
    'Arkansas': 'AR', 
    'New Hampshire': 'NH',
    'California': 'CA', 
    'New Jersey': 'NJ',
    'Colorado': 'CO', 
    'New Mexico': 'NM',
    'Connecticut': 'CT', 
    'New York': 'NY',
    'Delaware': 'DE', 
    'North Carolina': 'NC',
    'Florida': 'FL', 
    'North Dakota': 'ND',
    'Georgia': 'GA', 
    'Ohio': 'OH',
    'Hawaii': 'HI', 
    'Oklahoma': 'OK',
    'Idaho': 'ID', 
    'Oregon': 'OR',
    'Illinois': 'IL', 
    'Pennsylvania': 'PA',
    'Indiana': 'IN', 
    'Rhode Island': 'RI',
    'Iowa': 'IA', 
    'South Carolina': 'SC',
    'Kansas': 'KS', 
    'South Dakota': 'SD',
    'Kentucky': 'KY', 
    'Tennessee': 'TN',
    'Louisiana': 'LA', 
    'Texas': 'TX',
    'Maine': 'ME', 
    'Utah': 'UT',
    'Maryland': 'MD', 
    'Vermont': 'VT',
    'Massachusetts': 'MA', 
    'Virginia': 'VA',
    'Michigan': 'MI', 
    'Washington': 'WA',
    'Minnesota': 'MN', 
    'West Virginia': 'WV',
    'Mississippi': 'MS', 
    'Wisconsin': 'WI',
    'Missouri': 'MO', 
    'Wyoming': 'WY', }
    if toabbrev:
        df[col] = df[col].replace(states_to_abbrev)
    else:
        abbrev_to_states = dict ( (v,k) for k, v in states_to_abbrev.items() )
        df[col] = df[col].replace(abbrev_to_states)
    
    return df

def create_not_trade_days(tradedays_path= r'C:\Users\derobertisna.UFAD\Desktop\Data\Other SAS\tradedays.sas7bdat'):
    df = dero.load_sas(tradedays_path)
    trading_days = pd.to_datetime(df['date']).tolist()
    all_days = pd.date_range(start=trading_days[0],end=trading_days[-1]).tolist()
    notrade_days = [day for day in all_days if day not in trading_days]
    
    outdir = os.path.dirname(tradedays_path)
    outpath = os.path.join(outdir, 'not tradedays.csv')
    
    with open(outpath, 'w') as f:
        f.write('date\n')
        f.write('\n'.join([day.date().isoformat() for day in notrade_days]))
        
def tradedays(notradedays_path=r'C:\Users\derobertisna.UFAD\Desktop\Data\Other SAS\not tradedays.csv'):
    notrade_days = pd.read_csv(notradedays_path)['date'].tolist()
    return CustomBusinessDay(holidays=notrade_days)

def select_rows_by_condition_on_columns(df, cols, condition='== 1', logic='or'):
    """
    Selects rows of a pandas dataframe by evaluating a condition on a subset of the dataframe's columns.
    
    df: pandas dataframe
    cols: list of column names, the subset of columns on which to evaluate conditions
    condition: string, needs to contain comparison operator and right hand side of comparison. For example,
               '== 1' checks for each row that the value of each column is equal to one.
    logic: 'or' or 'and'. With 'or', only one of the columns in cols need to match the condition for the row to be kept.
            With 'and', all of the columns in cols need to match the condition.
    """
    #First eliminate spaces in columns, this method will not work with spaces
    new_cols = [col.replace(' ','_').replace('.','_') for col in cols]
    df.rename(columns={col:new_col for col, new_col in zip(cols, new_cols)}, inplace=True)
    
    #Now create a string to query the dataframe with
    logic_spaces = ' ' + logic + ' '
    query_str = logic_spaces.join([str(col) + condition for col in new_cols]) #'col1 == 1, col2 == 1', etc.
    
    #Query dataframe
    outdf = df.query(query_str).copy()
    
    #Rename columns back to original
    outdf.rename(columns={new_col:col for col, new_col in zip(cols, new_cols)}, inplace=True)
    
    return outdf

def show_df(df):
    pool = ThreadPool(1)
    pool.apply_async(_show_df, args=[df])
    
def _show_df(df):
    root = Tk()
    frame = Frame(root)
    frame.pack(fill=BOTH, expand=YES)
    pt = Table(parent=frame, dataframe=df)
    pt.show()
    pt.queryBar()
    root.mainloop()
    
def groupby_merge(df, byvars, func_str, *func_args, subset='all', replace=False):
    """
    Creates a pandas groupby object, applies the aggregation function in func_str, and merges back the 
    aggregated data to the original dataframe.
    
    Required Inputs:
    df: Pandas DataFrame
    byvars: str or list, column names which uniquely identify groups
    func_str: str, name of groupby aggregation function such as 'min', 'max', 'sum', 'count', etc.
    
    Optional Input:
    subset: str or list, column names for which to apply aggregation functions
    func_args: tuple, arguments to pass to func
    replace: bool, True to replace original columns in the data with aggregated/transformed columns
    
    Usage:
    df = groupby_merge(df, ['PERMNO','byvar'], 'max', subset='RET')
    """
    
    #Convert byvars to list if neceessary
    if isinstance(byvars, str):
        byvars = [byvars]
    
    #Store all variables except byvar in subset if subset is 'all'
    if subset == 'all':
        subset = [col for col in df.columns if col not in byvars]
        
    #Convert subset to list if necessary
    if isinstance(subset, str):
        subset = [subset]
    
    if func_str == 'transform':
        #transform works very differently from other aggregation functions
        
        #First we need to deal with nans in the by variables. If there are any nans, transform will error out
        #Therefore we must fill the nans in the by variables beforehand and replace afterwards
        df.fillna(value='__tempnan__', inplace=True)
        grouped = df.groupby(byvars)
        func = getattr(grouped, func_str) #pull method of groupby class with same name as func_str
        grouped = func(*func_args)[subset] #apply the class method and select subset columns
        grouped.columns = [col + '_' + func_str for col in grouped.columns] #rename transformed columns
        df.replace('__tempnan__', nan, inplace=True) #fill nan back into dataframe
        full = pd.concat([df, grouped], axis=1)
        
    else: #.min(), .max(), etc.
        grouped = df.groupby(byvars, as_index=False)[byvars + subset]
        func = getattr(grouped, func_str) #pull method of groupby class with same name as func_str
        grouped = func(*func_args) #apply the class method
        #Merge and output
        full = df.merge(grouped, how='left', on=byvars, suffixes=['','_' + func_str])
    
    if replace:
        _replace_with_transformed(full)
    
    return full
    
def _replace_with_transformed(df, func_str='transform'):
    transform_cols = [col for col in df.columns if col.endswith('_' + func_str)]
    orig_names = [col[:col.find('_' + func_str)] for col in transform_cols]
    df.drop(orig_names, axis=1, inplace=True)
    df.rename(columns={old: new for old, new in zip(transform_cols, orig_names)}, inplace=True)
    
def groupby_index(df, byvars, sortvars=None, ascending=True):
    """
    Returns a dataframe which is a copy of the old one with an additional column containing an index
    by groups. Each time the bygroup changes, the index restarts at 0.
    
    Required inputs:
    df: pandas DataFrame
    byvars: str or list of column names containing group identifiers
    
    Optional inputs:
    sortvars: str or list of column names to sort by within by groups
    ascending: bool, direction of sort
    """
    
    #Convert sortvars to list if necessary
    if isinstance(sortvars, str):
        sortvars = [sortvars]
    if sortvars == None: sortvars = []
    
    df = df.copy() #don't modify the original dataframe
    df.sort_values(byvars + sortvars, inplace=True, ascending=ascending)
    df['__temp_cons__'] = 1
    df = groupby_merge(df, byvars, 'transform', (lambda x: [i for i in range(len(x))]), subset=['__temp_cons__'])
    df.drop('__temp_cons__', axis=1, inplace=True)
    return df.rename(columns={'__temp_cons___transform': 'group_index'})

def to_copy_paste(df, index=False, column_names=True):
    """
    Takes a dataframe and prints all of its data in such a format that it can be copy-pasted to create
    a new dataframe from the pandas.DataFrame() constructor.
    
    Required inputs:
    df: pandas dataframe
    
    Optional inputs:
    index: bool, True to include index
    column_names: bool, False to exclude column names
    """
    print('pd.DataFrame(data = [')
    for tup in df.iterrows():        
        data = tup[1].values
        print(str(tuple(data)) + ',')
    last_line = ']'
    if column_names:
        last_line += ', columns = {}'.format([i for i in df.columns]) #list comp to remove Index() around cols
    if index:
        last_line += ',\n index = {}'.format([i for i in df.index]) #list comp to remove Index() around index
    last_line += ')' #end command
    print(last_line)
    
def _join_col_strings(*args):
    strs = [str(arg) for arg in args]
    return '_'.join(strs)

def join_col_strings(df, cols):
    """
    Takes a dataframe and column name(s) and concatenates string versions of the columns with those names.
    Useful for when a group is identified by several variables and we need one key variable to describe a group.
    Returns a pandas Series.
    
    Required inputs:
    df: pandas dataframe
    cols: str or list, names of columns in df to be concatenated
    """
    
    if isinstance(cols, str):
        cols = [cols]
    assert isinstance(cols, list)
    
    jc = np.vectorize(_join_col_strings)
    
    return pd.Series(jc(*[df[col] for col in cols]))

def winsorize(df, pct, subset=None, byvars=None, bot=True, top=True):
    """
    Finds observations above the pct percentile and replaces the with the pct percentile value.
    Does this for all columns, or the subset given by subset
    
    Required inputs:
    df: Pandas dataframe
    pct: 0 < float < 1 or list of two values 0 < float < 1. If two values are given, the first
         will be used for the bottom percentile and the second will be used for the top. If one value
         is given and both bot and top are True, will use the same value for both.
    
    Optional inputs:
    subset: List of strings or string of column name(s) to winsorize
    byvars: str, list of strs, or None. Column names of columns identifying groups in the data.
            Winsorizing will be done within those groups.
    bot: bool, True to winsorize bottom observations
    top: bool, True to winsorize top observations
    
    Example usage:
    winsorize(df, .05, subset='RET') #replaces observations of RET below the 5% and above the 95% values
    winsorize(df, [.05, .1], subset='RET') #replaces observations of RET below the 5% and above the 90% values

    """
    
    #Check inputs
    assert any([bot, top]) #must winsorize something
    if isinstance(pct, float):
        bot_pct = pct
        top_pct = 1 - pct
    elif isinstance(pct, list):
        bot_pct = pct[0]
        top_pct = 1 - pct[1]
    else:
        raise ValueError('pct must be float or a list of two floats')
        
    def temp_winsor(col):
        return _winsorize(col, top_pct, bot_pct, top=top, bot=bot)

    #Save column order
    cols = df.columns
    
    #Get a dataframe of data to be winsorized, and a dataframe of the other columns
    to_winsor, rest = _select_numeric_or_subset(df, subset, extra_include=byvars)

    #Now winsorize
    if byvars: #use groupby to process groups individually
        to_winsor = groupby_merge(to_winsor, byvars, 'transform', (temp_winsor), replace=True)
    else: #do entire df, one column at a time
        to_winsor.apply(temp_winsor, axis=0)
    
    return pd.concat([to_winsor,rest], axis=1)[cols]


def _winsorize(col, top_pct, bot_pct, top=True, bot=True):
    """
    Winsorizes a pandas Series
    """
    if top:
        top_val = col.quantile(top_pct)
        col.loc[col > top_val] = top_val
    if bot:
        bot_val = col.quantile(bot_pct)
        col.loc[col < bot_val] = bot_val
    return col
            
def _select_numeric_or_subset(df, subset, extra_include=None):
    """
    If subset is not None, selects all numeric columns. Else selects subset. 
    If extra_include is not None and subset is None, will select all numeric columns plus 
    those in extra_include.
    Returns a tuple of (dataframe containing subset columns, dataframe of other columns)
    """
    if subset == None:
        to_winsor = df.select_dtypes(include=[np.number, np.int64]).copy()
        subset    = to_winsor.columns
        rest      = df.select_dtypes(exclude=[np.number, np.int64]).copy()
    else:
        if isinstance(subset, str):
            subset = [subset]
        assert isinstance(subset, list)
        to_winsor = df[subset].copy()
        other_cols = [col for col in df.columns if col not in subset]
        rest = df[other_cols].copy()
    if extra_include:
        to_winsor = pd.concat([to_winsor, df[extra_include]], axis=1)
        rest.drop(extra_include, axis=1, inplace=True)
        
    return (to_winsor, rest)