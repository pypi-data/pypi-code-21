
import os
import pandas as pd
from numpy import nan, float64, issubdtype, number

from .ext_pandas import convert_sas_date_to_pandas_date, load_sas, left_merge_latest

def compustat_keep_mask(df):
    return (df['indfmt'] == 'INDL') & (df['datafmt'] == 'STD') & \
           (df['popsrc'] == 'D')    & (df['consol'] == 'C')
    
def add_q_or_y(get, freq, cols):
    """
    Takes a list of get vars and adds q or y to work with quarterly file
    """
    if freq in ('q', 'quarterly'):
        return q_or_y(get, cols)
    else:
        return get
    
def q_or_y(get, cols):
    """
    Checks compustat cols to see which extension ('q', 'y', none) is appropriate and adds it.
    For use with quarterly data.
    """
    out_list = []
    for g in get:
        if g in ('fqtr','cusip','fyr','tic','conm'):
            out_list.append(g)
            continue
        
        q = g + 'q'
        y = g + 'y'
        if q in cols:
            name = q
        elif y in cols:
            name = y
        else:
            raise ValueError('variable {} does not have a quarterly counterpart'.format(g))
        out_list.append(name)
    return out_list

def create_q_from_y(df, var_y):
    """
    Single variable conversion
    Creates a compustat quarterly "q" variable from a compustat quarterly "y" variable. "q" variables
    are for just what happened in the quarter, while "y" variables are year to date. 
    
    Note: inplace
    """
    var = var_y[:-1] #gets name of variable without y
    df[var_y + '_lag'] = df[var_y].shift(1)
    df.loc[(df['fqtr'] > 1) & (df['gvkey'] == df['gvkey_lag']), var + 'q'] = \
                df[var_y] - df[var_y + '_lag']
    df.loc[df['fqtr'] == 1, var + 'q'] = df[var_y]
    
#     var = var_y[:-1] #gets name of variable without y
#     df[var_y + '_lag'] = df[var_y].shift(1)
#     df.loc[df['fqtr'] > 1, var + 'q'] = df[var_y] - df[var_y + '_lag']
#     df.loc[df['fqtr'] == 1, var + 'q'] = df[var_y]
    
def create_qs_from_ys(df, get, freq):
    """
    Dataframe conversion
    Creates compustat quarterly "q" variablse from a compustat quarterly "y" variables. "q" variables
    are for just what happened in the quarter, while "y" variables are year to date. 
    
    Note: will make edits to prior df even though returns a new df
    """
    if freq in ('q', 'quarterly'):
        y_get = [g for g in get if g.endswith('y')]
        df['gvkey_lag'] = df['gvkey'].shift(1)
        [create_q_from_y(df, g) for g in y_get]
        return df.drop(y_get + ['fqtr', 'gvkey_lag'] + [c + '_lag' for c in y_get], axis=1)
    else:
        return df
    
def check_freq(freq):
    freq = freq.lower()
    assert freq in ('a','q','annual','quarterly')
    return freq

def freq_to_name(freq, debug):
    if freq in ('a','annual'):
        name = 'funda'
    elif freq in ('q', 'quarterly'):
        name = 'fundq'
    if debug:
        name += '_test'
    name += '.sas7bdat'
    return name
    
def keep_relevant_data_compustat(df, get=['sale'], freq='a'):
    get = add_q_or_y(get, freq, df.columns) #adds 'q' or 'y' to getvars if freq='q'
    mask = compustat_keep_mask(df)
    keepvars = ['gvkey','datadate']
    if freq in ('q', 'quarterly'):
        keepvars += ['fqtr'] #need for converting 'y' variables to 'q' variables
    keepvars += get
    comp_y = df.loc[mask, keepvars].drop_duplicates(
        subset=['gvkey', 'datadate']).reset_index(drop=True)
    #comp_y includes 'y' vars, need to convert to 'q' vars 
    return create_qs_from_ys(comp_y, get, freq)

def convert_date_compustat(df):
    df['datadate'] = convert_sas_date_to_pandas_date(df['datadate'])
    
def load_compustat(freq, get=['sale'], debug=False, comp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\Compustat'):
    freq = check_freq(freq)
    name = freq_to_name(freq, debug)
    path = os.path.join(comp_dir, name)
    comp = load_sas(path, dtype={'gvkey':str})
    comp = keep_relevant_data_compustat(comp, get=get, freq=freq)
    convert_date_compustat(comp)
    return comp

def merge_compustat(df, compdf, datevar='Date'):
    return left_merge_latest(df, compdf, 'gvkey',
                            left_datevar=datevar, right_datevar='datadate')

# def merge_compustat(df, compdf, datevar='Date'):
#     many = df.merge(compdf, on='gvkey', how='left')
#     lt = many.loc[many[datevar] >= many['datadate']] #left with datadates less than date

#     #find rows within groups which have the maximum datadate (soonest before given date)
#     data_rows = lt.groupby(['gvkey',datevar], as_index=False)['datadate'].max() \
#         .merge(lt, on=['gvkey', datevar, 'datadate'], how='left')
    
#     return df.merge(data_rows, on=['gvkey',datevar], how='left')

def convert_numeric_gvkey_to_string(gvkey):
    """
    Converts a single numeric gvkey to string
    """
    str_gvkey = str(int(gvkey))
    num_zeroes = 6 - len(str_gvkey)
    return '0' * num_zeroes + str_gvkey

def convert_gvkey_col(gvkey):
    """
    Converts a column of numeric gvkeys to string
    """
    if pd.isnull(gvkey): return nan
    else:
        return convert_numeric_gvkey_to_string(gvkey)
    
def convert_gvkey(df, gvkeyvar):
    """
    Renames gvkeyvar to 'gvkey' and converts to string if necessary
    
    Note: this is inplace
    """
    if gvkeyvar != 'gvkey':
        df.rename(columns={gvkeyvar: 'gvkey'}, inplace=True)
    if issubdtype(df['gvkey'].dtype, number):
        df['gvkey'] = df['gvkey'].apply(convert_gvkey_col)