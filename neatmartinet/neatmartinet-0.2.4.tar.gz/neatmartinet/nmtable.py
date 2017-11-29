# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 13:44:12 2017
This script is adding a few complentary features on pandas
"""
import numpy as np
import pandas as pd

import neatmartinet as nm

# %%

nadict = nm.nadict


# %%
def map_values(myserie, mydict=None):
    '''
    Takes as input a panda Series and a dictionary
    Returns then a cleaned pandas.Series
    Simple implementation of pandas.Series.replace method
    :param myserie: pandas.Series to be cleaned
    :param mydict: pandas.Series used as dictionary
    :return: new pandas.Series with values replaced
    '''
    if mydict is None:
        print('Error: missing dict')
    myserie_cleaned = myserie.replace(nadict)
    myserie_cleaned = myserie_cleaned.replace(mydict)
    possiblevalues = mydict.unique()
    unknownvalues = [c for c in myserie_cleaned.unique() if not c in possiblevalues]
    if len(unknownvalues) > 0:
        print('Unknown values: ')
        print(unknownvalues)
    return myserie_cleaned


# %%
def checkcolumns(newcolumns, referencecolumns, coldict=None):
    '''
    Check the columns of a new dataframe against reference columns expected
    :param newcolumns: newcolumns as given by pandas.Dataframe.columns
    :param referencecolumns: referencecolumns (could be a list)
    :param coldict: optional, default None, dictionary to rename columns
    :return: new column names as pandas.Series
    '''
    newcolumns = pd.Series(newcolumns)
    referencecolumns = pd.Series(referencecolumns)
    if coldict is not None:
        newcolumns = newcolumns.replace(coldict)

    unknownvalues = [c for c in newcolumns if not c in referencecolumns]
    if len(unknownvalues) > 0:
        print('Unknown columns: ')
        print(unknownvalues, '\n')

    missingvalues = [c for c in referencecolumns if not c in newcolumns]
    if len(missingvalues) > 0:
        print('Missing columns: ')
        print(missingvalues, '\n')
    x = newcolumns.value_counts()
    x = x[x > 1]
    if x.shape[0] > 0:
        print('Duplicate Columns: ')
        print(x)
        print('\n')
    return newcolumns


# %%
def checkjointures(myserie, possiblevalues):
    '''
    Check the list of categories in a column against a provided standard list
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: None
    print:
    - if all values are matching, a simple message indicating evrything is correct
     - the percentage of rows and the percentage of unique values matching standard values
     - the number of rows and the number of unique values that are unknown in the standard values
     - example of non-matching values and the number of occurences
    '''
    matchingvalues = myserie[myserie.isin(possiblevalues)]
    unknownvalues = myserie[myserie.isin(possiblevalues) == False]
    if unknownvalues.shape[0] == 0:
        print('100% of values match')
    else:
        percentrowmatching = matchingvalues.shape[0] / myserie.shape[0]
        percentvaluematching = matchingvalues.unique().shape[0] / myserie.unique().shape[0]
        print('{:.0%}'.format(percentrowmatching), 'of rows matching for ', '{:.0%}'.format(percentvaluematching),
              'of values matching.')
        print(unknownvalues.shape[0], 'rows unknowns for ', unknownvalues.unique().shape[0], ' unknown unique values')
        print('Example unknowns:')
        print(unknownvalues.value_counts().iloc[:10])


# %%
def getunknownvalues(myserie, possiblevalues):
    '''
    return unique values from a pandas.Series that are unknown in a list of standard values
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: unknown values as a list
    '''
    myserie = pd.Series(myserie)
    unknownvalues = myserie[myserie.isin(possiblevalues) == False].unique().tolist()
    if len(unknownvalues) == 0:
        return None
    else:
        return unknownvalues


# %%
def getmatchingvalues(myserie, possiblevalues):
    '''
    return unique values from a pandas.Series that are matching a list of standard values
    :param myserie: pandas.Series to be checked
    :param possiblevalues: list of standard values
    :return: matching values as a list
    '''
    myserie = pd.Series(myserie)
    matchingvalues = myserie[myserie.isin(possiblevalues)].unique().tolist()
    if len(matchingvalues) == 0:
        return None
    else:
        return matchingvalues

# %%
def checkuniqueid(myserie):
    '''
    check if each value in a pandas.Series is unique
    :param myserie: pandas.Series to be checked
    :return: boolean
    '''
    if myserie.unique().shape[0] == myserie.shape[0]:
        return True
    else:
        print('{:.0%}'.format(myserie.unique().shape[0] / myserie.shape[0]), ' of values unique')
        return False


# %%
# noinspection PyDictCreation
def checkna(myserie):
    '''
    counts the occurence of null values in a pandas.Series
    :param myserie: pandas.Series to be checked
    :return: dict, number and percentage of null values 
    '''
    mydict = {'nanValues' : myserie.isnull().sum() }
    mydict['percentNonNull'] = '{:.0%}'.format(1 - myserie.isnull().sum() / myserie.shape[0])
    return mydict


# %%
def summarize(X):
    '''
    
    :param X: DataFrame or Serie
    :return: print summarize on screen as a Dataframe
    '''
    if type(X) == pd.DataFrame:
        return __summarize_df__(X)
    else:
        return __summarize_serie__(X)


# %%
def __summarize_df__(mydf):
    result = pd.DataFrame(
        index=['nanValues', 'percentNonNull', 'medianValue', 'minValue', 'maxValue', 'distinctValues', 'percentUnique',
               'exampleValues'],
        columns=mydf.columns)
    for c in mydf.columns:
        result[c] = __summarize_serie__(mydf[c])
    return result


# %%
def __summarize_serie__(myserie):
    '''
    Return a Serie with describing values (nan, unique,..)
    :param myserie: series
    :return: series
    '''
    #simple check to see if serie is a date
    if 'date' in myserie.name.lower():
        a = __describedate__(myserie)
        if a is not None:
            return a
    try:
        #then check to see if serie is a numeric serie
        myserie = myserie.astype(float)
        return __describenum__(myserie)
    except:
        #consider serie as a categorical
        return __describecat__(myserie)


# %%
def __describenum__(myserie):
    '''
    :param myserie: pandas.Series containing numerical values
    :return: number of nan values, minvalue, max value
    '''
    mydict = checkna(myserie)
    mydict['medianValue'] = myserie.dropna().median()
    mydict['minValue'] = myserie.dropna().min()
    mydict['maxValue'] = myserie.dropna().max()
    return pd.Series(mydict, name=myserie.name)


# %%
def __describecat__(myserie):
    '''
    
    :param myserie: pandas.Series containing numerical values
    :return: number of nan values, distinct values, percentage of unique values, examples
    '''
    mydict = checkna(myserie)
    mydict['distinctValues'] = myserie.unique().shape[0]
    mydict['percentUnique'] = '{:.0%}'.format(myserie.unique().shape[0] / myserie.shape[0])
    mydict['exampleValues'] = list(myserie.value_counts(dropna=False).index[:3])
    return pd.Series(mydict, name=myserie.name)


# %%
def __describedate__(myserie):
    '''
    
    :param myserie: pandas.Series containing dates values
    :return: number of nan values, minvalue, max value
    '''
    try:
        myserie = nm.convert_str_to_date(myserie)
    except:
        try:
            myserie = pd.to_datetime(myserie)
        except:
            return None
    mydict = checkna(myserie)
    mydict['maxValue'] = myserie.dropna().max()
    mydict['minValue'] = myserie.dropna().min()
    s = pd.to_timedelta(myserie.dropna() - myserie.dropna().min(), unit='ms').median()
    s = pd.to_datetime(myserie.dropna().min() + s)
    mydict['medianValue'] = s
    return pd.Series(mydict, name=myserie.name)


# %%
def generate_sample_dataframe(nrows=5):
    '''
    generate a sample dataframe
    :param nrows: number of rows of the dataframe
    :return: A pandas.DataFrame
    -float_col
    -float_withna_col
    -date_col
    -cat_col
    -parentcat_col
    -mixed_col
    
    '''
    df = pd.DataFrame(np.random.random((nrows, 1)))
    df.columns = ['float_col']
    df['float_col_hasna'] = np.random.choice([-1.0, 0.0, 0.7, 2.0, 3.0, np.nan], size=nrows)

    ##
    a = pd.datetime.today()
    d = []
    for c in range(nrows):
        delta = '{:.0f}'.format(np.random.uniform(-180, +180))
        b = a + pd.Timedelta(delta + ' days')
        d.append(b)
    df['date_col'] = d
    df['date_col'] = pd.to_datetime(df['date_col'].dt.date)
    if nrows > 2:
        df.loc[2, 'date_col'] = pd.to_datetime(np.nan)
    ###
    df['cat_col'] = np.random.choice(['foo', 'bar', 'baz', None], size=nrows)
    
    df['parentcat_col'] = df['cat_col'].replace({'foo': 'bing', 'bar': 'bing', 'baz': 'weez'})
    df['parentcat_col'] = df['parentcat_col'].fillna('weez')

    df['mixed_col'] = np.random.choice([1, 'foo', 2, 4.5, 'bar', pd.datetime.today(), None], size=nrows)

    return df


# %%
def aggregateby_category(s):
    '''
    This function should be applied on a grouped by data
    :param s: the groupbedby serie
    :return: the most common value (not na)
    example: gb['cat'].apply(lambda r:aggregateby_category(r))
    '''
    s = s.dropna()
    if len(s) == 0:
        return None
    else:
        return s.value_counts().index[0]


# %%
def aggregateby_value(s, aggfunc=None, isdate=False, dropna=True):
    '''
    This function should be applied on a grouped by data
    :param s: the groupedby serie
    :param aggfunc: aggregation function such as np.min
    :param isdate: if the serie is a date, default Faulse
    :param dropna: should we drop na values defautl True
    :return: the return of the aggfunc function
    '''
    if s.isnull().sum() > 0 and dropna == False:
        return None
    s = s.dropna()
    if len(s) == 0:
        return None
    if isdate:
        if aggfunc == np.min or aggfunc == np.max:
            return aggfunc(s)
        else:
            r = aggfunc(pd.to_timedelta(s - s.min(), unit='ms'))
            return pd.to_datetime(s.min() + r)
    else:
        return aggfunc(s)
        # %%

def splitdate(s):
    """
    Takes a date series
    Args:
        s (pd.Series): date serie

    Returns:
        pd.DataFrame
    returns a serie with _year,_month,_day,_dayofweek
    """
    s2=pd.to_datetime(s)
    df=pd.DataFrame(index=s2.index)
    df[s.name+'_year']=s2.dt.year
    df[s.name + '_month'] = s2.dt.month
    df[s.name + '_day'] = s2.dt.day
    df[s.name + '_dayofweek'] = s2.dt.weekday
    return df


def check_column_same(a, b):
    if set(a) == set(b):
        return True
    else:
        common_set = np.intersect1d(a, b)
        missing_a_columns = list(filter(lambda x: x not in common_set, b))
        if len(missing_a_columns) > 0:
            print('unknown columns from', b.name, 'not in', a.name, ':', missing_a_columns)
        missing_b_columns = list(filter(lambda x: x not in common_set, a))
        if len(missing_b_columns) > 0:
            print('unknown columns from', a.name, 'not in', b.name, ':', missing_b_columns)
        return False


def find_missing_keys_in_index(keys, ref_list, verbose=True):
    """
    Takes as input the a list of keys, and check if they are present in a reference list
    For example, make sure that all of the keys are in the index before launching a loop
    Args:
        keys (iterable): list of keys to be checked
        ref_list (iterable): list of reference keys
        verbose (bool): whether or not to print the statements

    Returns:
        bool: If True, then keys are missing
    """
    incorrect_keys = list(filter(lambda x: x not in ref_list, keys))
    if len(incorrect_keys) > 0:
        if verbose:
            print('those keys are missing in the index:', incorrect_keys)
        return True
    else:
        return False