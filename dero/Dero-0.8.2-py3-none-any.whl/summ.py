
import numpy as np

def summary_stats(df, pct_vars=None, int_vars=None, float_vars=None, count=False):
    """
    Generates a transposed df.describe() table where pct_vars are formatted with two
    decimal percentages, int_vars are formatted with zero decimal places, and float_
    vars are formatted with two decimal places.
    
    """
    stats = ['mean', 'std', 'min', '25%','50%','75%','max']
    all_vars = _if_lists_exist_then_combine(pct_vars, int_vars, float_vars)
    summ = df[all_vars].replace([np.inf, -np.inf], np.nan).dropna().describe().T
    apply_formatting(summ, stats, pct_vars=pct_vars, int_vars=int_vars, float_vars=float_vars)
    
#     formats = _if_vars_list_exists_then_add_to_format_dict(pct_vars, int_vars, float_vars)
    
#     _apply_formatting_from_format_dict(summ, formats, stats)

    if count:
        #Format count column individually
        summ['count'] = summ['count'].apply(lambda x: '{0:.0f}'.format(x))
    else:
        summ.drop('count', axis=1, inplace=True)
        
    return summ

def summ_vars_single_stat_by_groups(df, groupvar, pct_vars=None, int_vars=None, float_vars=None, stat='mean'):
    """
    Generates a table where groups are columns and rows are variables, where the values
    are a single summary stat
    """
    all_vars = _if_lists_exist_then_combine(pct_vars, float_vars, int_vars)

    group = df.groupby(groupvar)[all_vars]
    func = getattr(group, stat) #gets .mean(), .median(), etc.
    summ = func().T #applies .mean(), .median(), etc.
    apply_formatting(summ, summ.columns, pct_vars=pct_vars,
                               float_vars=float_vars, int_vars=int_vars)
    return summ

def apply_formatting(df, cols, pct_vars=None, int_vars=None, float_vars=None):
    """
    Applies percentage, integer, and float formatting to a summary table. Variables must
    be in rows, with statistics in columns.
    
    Note: inplace
    """
    formats = _if_vars_list_exists_then_add_to_format_dict(pct_vars, int_vars, float_vars)
    
    _apply_formatting_from_format_dict(df, formats, cols)

def _if_lists_exist_then_combine(*args):
    out = []
    for a in args:
        if a:
            out += a
    return out

def _if_vars_list_exists_then_add_to_format_dict(pct_vars, int_vars, float_vars):
    formats = {
        0: '{:.2%}',
        1: '{0:.0f}',
        2: '{0:.2f}'
    }
    for i, var_list in enumerate([pct_vars, int_vars, float_vars]):
        if var_list:
            formats[tuple(var_list)] = formats.pop(i) #replaces int key with tuple of vars
    return formats

def _apply_formatting_from_format_dict(df, formats, cols):
    """
    Note: inplace
    """
    for k in formats: #apply appropriate format to stats columns but not count column
        if not isinstance(k, int): #skip empty lists - these are marked by an integer
            df.loc[list(k), cols] = df.loc[list(k), cols].applymap(
                lambda x: formats[k].format(x))