
from io import StringIO
import sys
import functools

# class WRDS:
    
#     def __init__(self):
#         import wrds
#         self.wrds_obj = wrds
        
#     def get(self, *args, **kwargs):
#         """
#         See docstring of dero.wrds.get
#         """
#         return get(*args, wrds_obj=self.wrds_obj, **kwargs)
    
#     def sql(self, *args, **kwargs):
#         """
#         See docstring of dero.wrds.sql
#         """
#         return sql(*args, wrds_obj=self.wrds_obj, **kwargs)

class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout


def login_if_needed(func):
    """
    This decorator is to be used after importing wrds. Will log in again
    if connection is timed out.
    
    Usage:
    
    import wrds
    
    @login_if_needed
    def get_msi():
        return wrds.sql('select * from CRSP.MSI')
    """

    @functools.wraps(func)
    def func_or_login_and_func(*args,**kwargs):
        import wrds
        kwargs.update({'wrds_obj':wrds})
        with Capturing() as output:
            result = func(*args, **kwargs)
        if any(['Connection reset by peer' in s for s in output]): #connection error
            wrds.CONN = wrds._authenticate(wrds.username, wrds.password)
            return func(*args, **kwargs)
        return result

    return func_or_login_and_func

def get(libname, tablename, getvars=False, where=False, subset=False, distinct=False):
    """
    Executes a standard SQL query to get variables from table. Passing an int to subset
    causes only that many rows to be returned.
    
    Required inputs: (note: none of these are case sensitive)
    libname: str, name of library in wrds
    tablename: str, name of table within library in wrds
    
    Optional inputs:
    getvars: False, str, or list of strs, names of columns to pull from table. If False will
             pull all columns.
    where: False or str, SQL where expression without the word where.
            Examples:
                'permno = 10516 and askhi > 1000'
                'date = "04jan2013"d'
                'date between "07jan2013"d and "08jan2013"d'
    subset: False or int, set to an int to keep that many observations
    distinct: bool, set to true to select distinct
    """
#     if not wrds_obj:
#         import wrds
#         wrds_obj = wrds
    
    if isinstance(getvars, str):
        getvars = [getvars]
    
    select = 'select ' + ('distinct ' if distinct else '')
    
    if getvars:
        var_string =  ', '.join([g.lower() for g in getvars])
    else:
        var_string = '*'
        
    table_string = '.'.join([n.strip().upper() for n in [libname, tablename]])
    query = select + var_string + ' from ' + table_string
    
    if subset:
        query += ' (obs={})'.format(subset)
        
    if where:
        query += ' where ' + where
    
    return sql(query)

@login_if_needed
def sql(*args, **kwargs):
    """
    Replicates wrds.sql with auto-login if necessary. Pass query string and index. Documentation
    from wrds.sql below:
    
    Run a SQL Query on the WRDS Database.
    data = wrds.sql('select * from CRSP.MSI', 'DATE')

    The second argument gives the column name of the index, if you'd like
    your DataFrame to be indexed.
    """
#     if not wrds_obj:
#         import wrds
#         wrds_obj = wrds

    wrds_obj = kwargs.pop('wrds_obj')
    
    return wrds_obj.sql(*args, **kwargs)

def strip_str(x):
     return x.strip() if isinstance(x, str) else x


def tolist_and_strip_outlist(func):
    """
    This decorator works for functions that return a pandas Series. It converts the series to
    a list and strips white space from the output.
    
    """
    @functools.wraps(func)
    def tolist_and_strip(*args,**kwargs):
        result = func(*args, **kwargs)
        return [r.strip() for r in result.tolist()]

    return tolist_and_strip

@tolist_and_strip_outlist
def all_libraries():
    """
    Returns every library in WRDS
    """
    return sql('select distinct libname from dictionary.tables')['libname']


@tolist_and_strip_outlist
def all_tables_in_library(libname):
    """
    Returns every table in a library in WRDS
    """
    return sql('select distinct memname from dictionary.columns ' 
                    'where libname="{}"'.format(libname.upper()))['memname']

@tolist_and_strip_outlist
def _all_columns_in_table(libname, tablename):
    """
    Returns every column in a table in WRDS
    """
    return sql('select name from dictionary.columns ' 
                    'where libname="{}" and memname="{}"'.format(
                        libname.upper(), tablename.upper()))['name']


@tolist_and_strip_outlist
def _all_labels_in_table(libname, tablename):
    """
    Returns every column in a table in WRDS
    """
    return sql('select label from dictionary.columns ' 
                    'where libname="{}" and memname="{}"'.format(
                        libname.upper(), tablename.upper()))['label']

def all_columns_in_table(libname, tablename):
    """
    Args are libname, tablename strings. Returns a dataframe of column names and labels.
    """
    return sql('select name, label from dictionary.columns ' 
                    'where libname="{}" and memname="{}"'.format(
                        libname.upper(), tablename.upper())).applymap(
                            strip_str)
    
def all_tables():
    """
    Returns every table in WRDS
    """
    df = sql('select libname, memname, memlabel, nvar from dictionary.tables '
                  'where not(missing(memlabel))').rename(
                        columns={'nvar':'Number of Columns'})
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)