
from sas7bdat import SAS7BDAT
import pandas as pd
import os, datetime, warnings, sys

from .ext_pandas import expand_time, cumulate, convert_sas_date_to_pandas_date, reg_by, factor_reg_by, load_sas, \
                    long_to_wide, year_month_from_date, join_col_strings
    
from .compustat import convert_gvkey, load_compustat, merge_compustat


def replace_missing_csv(csv_list, missing_rep):
    '''
    Replaces missing items in a CSV with a given missing representation string.
    '''
    full_list = []
    for line in csv_list:
        line_list = line.split(',')
        new_line_list = []
        for item in line_list:
            if item == '': #if the item is missing
                item = missing_rep
            new_line_list.append(item)
        full_list.append(new_line_list)
    return full_list

def merge_dsenames(df, on='TICKER', get='PERMNO', date='Date', 
                   other_byvars=None, 
                   crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
    '''
    Merges with dsenames file on on variable (TICKER, PERMNO, PERMCO, NCUSIP, CUSIP6), to get get variable (same list).
    Must have a Date variable in df.
    
    Default is to match on TICKER and pull PERMNO.
    
    Required inputs:
    df: pandas dataframe containing any of (TICKER, PERMNO, PERMCO, NCUSIP, CUSIP6)
    
    Optional inputs:
    on: str, column name to merge on, one of (TICKER, PERMNO, PERMCO, NCUSIP, CUSIP6)
    get: str or list, column or columns to get from dsenames, any of (TICKER, PERMNO, PERMCO, NCUSIP, CUSIP6)
         that aren't already in on
    date: str, column name of date variable
    other_byvars: any other variables signifying groups in the data, prevents from collapsing those groups
    '''
    #Make get a list
    if isinstance(get, str):
        get = [get]
    assert isinstance(get, list)
    
    #Make other byvars a list
    if not other_byvars:
        other_byvars = []
    if isinstance(other_byvars, str):
        other_byvars = [other_byvars]
    assert isinstance(other_byvars, list)
    
    assert on not in get #can't get what we already have
    
    #Pull from CRSP dsenames file
    file = 'dsenames'
    fullpath = os.path.join(crsp_dir, file + '.sas7bdat')
    names_df = load_sas(fullpath)
    
    #Convert NCUSIP to CUSIP6
    if on == 'CUSIP6' or 'CUSIP6' in get:
        names_df['CUSIP6'] = names_df['NCUSIP'].apply(lambda x: x if pd.isnull(x) else x[:6])
    
    names_df['start'] = convert_sas_date_to_pandas_date(names_df['NAMEDT'])
    names_df['end'] = convert_sas_date_to_pandas_date(names_df['NAMEENDT'])
    names_df['end'] = names_df['end'].fillna(datetime.date.today())
    
    
    #Now perform merge
    merged = df[[on, date] + other_byvars].merge(names_df[['start','end', on] + get], how='left', on=on)
    #Drop out observations not in name date range
    valid = (merged[date] >= merged['start']) & (merged[date] <= merged['end'])
    #However if there is not a match, doing merged[valid] would drop the observation instead of leaving nan
    #Therefore, take merged[valid] and merge back again to original
    new_merged = df.merge(merged[valid].drop(['start','end'],axis=1), how='left', on=[on, date] + other_byvars)
    new_merged = new_merged.reset_index(drop=True)
    
    if 'PERMNO' in get:
        #Dsenames has no record of which permno is the primary link when a firm has multiple share classes.
        #To get this information, we must merge ccmxpf_linktable. We want to keep only primary links.
        dups = new_merged[[date, on] + other_byvars].duplicated(keep=False) #series of True or False of whether duplicated row
        if dups.any(): #this means we got more than one permno for a single period/firm/byvars
            duplicated = new_merged[dups].reset_index() #puts index in a column for later use
            not_duplicated = new_merged[~dups]
            
            #Take duplicated, merge to ccmxpf_linktable to get gvkey, and the ones which do not have gvkeys are
            #the non-primary links
            with_gvkey = get_gvkey_or_permno(duplicated, date) #default is to get gvkey with permno
            removed_duplicates = with_gvkey[~pd.isnull(with_gvkey['GVKEY'])].drop('GVKEY', axis=1)
            
            #Set index back
            removed_duplicates.set_index('index', inplace=True)
            
            #Now append back together and sort
            full = not_duplicated.append(removed_duplicates)
            new_merged = full.sort_index()
    
    return new_merged.reset_index(drop=True)

def get_gvkey_or_permno(df, datevar, get='GVKEY', other_byvars=None,
                        crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
    """
    Takes a dataframe containing either GVKEY or PERMNO and merges to the CRSP linktable to get the other one.
    """    
    if get == 'GVKEY':
        rename_get = 'gvkey'
        l_on = 'PERMNO'
        r_on = 'lpermno'
    elif get == 'PERMNO':
        rename_get = 'lpermno'
        l_on = 'GVKEY'
        r_on = 'gvkey'
    else:
        raise ValueError('Need get="GVKEY" or "PERMNO"')
        
    #Make other byvars a list
    if not other_byvars:
        other_byvars = []
    if isinstance(other_byvars, str):
        other_byvars = [other_byvars]
    assert isinstance(other_byvars, list)
    
    link_name = 'ccmxpf_linktable.sas7bdat'
    link_path = os.path.join(crsp_dir, link_name)
    
    link = load_sas(link_path)
    link['linkdt'] = convert_sas_date_to_pandas_date(link['linkdt'])
    link['linkenddt'] = convert_sas_date_to_pandas_date(link['linkenddt'])
    #If end date is missing, that means link is still active. Make end date today.
    link['linkenddt'] = link['linkenddt'].fillna(datetime.date.today())
    
    #Remove links with no permno so that they don't match to nans in the input df
    link.dropna(subset=['lpermno'], inplace=True)
    
    merged = df.merge(link[['lpermno','gvkey', 'linkdt', 'linkenddt','linkprim']], how='left', left_on=l_on, right_on=r_on)

    valid = (merged[datevar] >= merged.linkdt) & \
            (merged[datevar] <= merged.linkenddt) & \
            (merged.linkprim == 'P')
        
    merged = merged[valid].drop(['linkdt','linkenddt', 'linkprim', r_on], axis=1).drop_duplicates()
    merged.rename(columns={rename_get:get}, inplace=True)
    
    #Now merge back to the original again to ensure that rows are not deleted
    new_merged = df.merge(merged[['PERMNO','GVKEY', datevar] + other_byvars],
                          how='left', on=[l_on, datevar] + other_byvars)
    
    return new_merged


class GetCRSP:
    
    def __init__(self, debug=False, crsp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\CRSP'):
        self.debug = debug
        self.crsp_dir = crsp_dir
        self.loaded_m = False
        self.loaded_d = False
        self.crsp_dfs = {} #container for both monthly and daily crsp df
        
    
    def pull_crsp(self, df, coid='PERMNO', freq='m', get=['PRC','SHROUT'], date='Date', other_byvars=None,
                 time=None, wide=True,
                 abret=False, window=None, cumret=False, includefac=False, includecoef=False, 
                 drop_first=False):
        '''
        Pulls prices and returns from CRSP. Currently supports the monthly file merging on PERMNO.

        WARNING: Will overwrite variables called "Year" and "Month" if merging the monthly file

        coid = string, company identifier (currently supports 'GVKEY', 'TICKER', 'PERMNO', 'PERMCO', 'NCUSIP')
        freq = 'm' for monthly, 'd' for daily
        get = 'PRC', 'RET', 'SHROUT', 'VOL', 'CFACPR', 'CFACSHR', or a list combining any of these
        date = name of datetime column in quotes
        other_byvars = other by vars in dataset besides company identifier and date. Used for long_to_wide
        time = list of integers or None. If not None, will pull the variables for a time difference of the time
               numbers given, and put them in wide format in the output dataset. For instance time=[-12,0,12] with
               freq='m' and get='RET' would pull three returns per observation, one twelve months prior, one contemporaneous,
               and one twelve months later, naming them RET-12, RET0, and RET12. If freq='d' in the same example, it would be
               twelve days prior, etc.
        abret = 1, 3, 4, or False. If 1, 3, or 4 is passed and 'RET' is in get, will calculate abnormal returns according to CAPM,
                3 or 4 factor model, respectively. 
        window = Integer or None. Must provide an integer if abret is not False. This is the number of prior periods to use
                 for estimating the loadings in factor models. For instance, if freq='m', window=36 would use the prior
                 three years of returns to estimate the loadings.
        cumret = 'between', 'zero', 'first', or False. time must not be None and RET in get for this option to matter. 
                 When pulling returns for multiple periods, gives the option to cumulate returns. If False, will just return 
                 returns for the individual periods. 
                 If 'zero', will give returns since the original date. 
                 If 'between', will give returns since the prior requested time period.
                 If 'first', will give returns since the first requested time period.
                 For example, if our input data was for date 1/5/2006, and in the CRSP table we had:
                     permno  date       RET
                     10516   1/5/2006   10%
                     10516   1/6/2006   20%
                     10516   1/7/2006    5%
                     10516   1/8/2006   30%
                 Then get_crsp(df, time=[1,3], get='RET', cumret=None) would return:
                     permno  date       RET1  RET3
                     10516   1/5/2006   20%   30%
                 Then get_crsp(df, time=[1,3], get='RET', cumret='between') would return:
                     permno  date       RET1  RET3
                     10516   1/5/2006   20%   36.5%
                 Then get_crsp(df, time=[1,3], get='RET', cumret='zero') would return:
                     permno  date       RET1  RET3
                     10516   1/5/2006   20%   63.8%
                 The output for cumret='first' would be the same as for cumret='zero' because the first period is period zero.
                 Had time been =[-1, 1, 3], then returns would be calculated from period -1 to period 1, and period -1 to period 3. 
        includefac = Boolean, True to include factors in output
        includecoef = Boolean, True to include factor coefficients in output
        wide = True for output data to be wide form, False for long form. Only applies when time is not None.
        drop_first = bool, set to True to drop observations for first time. Can only be used when time != None, and
                     when cumret != False. This is a
                     convenience function for estimating cumulative return windows. For example, if time = [-1, 1], 
                     then the typical output would include both cum_RET-1 and cum_RET1. All we actually care about is the
                     cumulative return over the window, which is equal to cum_RET1. drop_first=True will drop out 
                     RET-1 and cum_RET-1 from the output.
        debug: bool, set to True to restrict CRSP to only PERMNOs 10516 (gvkey=001722) and 10517 (gvkey=001076)

        Typical usage:
        Calculating a return window with abnormal returns included:
            get_crsp(df, get='RET', freq='d', time=[-1, 1], cumret='between', abret=4, window=250, drop_first=True)
        '''  
        self.df = df.copy()
        self.coid = coid
        self.freq = freq
        self.get = get
        self.date = date
        self.other_byvars = other_byvars
        self.time = time
        self.wide = wide
        self.abret = abret
        self.window = window
        self.cumret = cumret
        self.includefac = includefac
        self.includecoef = includecoef
        self.drop_first = drop_first
        
        self._log('Initializing pull_crsp function')
    
        self._clear_old_variables()
        self._check_inputs()
        self._load_crsp()
        
        if self.time == None and self.abret == False: 
            return self._merge_crsp(self.df, self.date) #if we're not doing anything special, just merge CRSP
        
        if self.time:
            self._handle_time()
        else:
            self._handle_no_time()
            
        self._create_key()
        
        if self.abret:
            self._handle_abret()
        else:
            self.long_df = self._merge_crsp(self.long_df, date='Shift Date') #time but not abret        
        
        if self.cumret:
            self._handle_cumret()
        
        self.long_df.drop('key', axis=1, inplace=True)
        
        if self.wide:
            return self._long_to_wide()
        else:
            return self._output_long()
    
    def _clear_old_variables(self):
        """
        If pull_crsp is run multiple times, values of variables would still be set
        """
        try: del self.long_df
        except AttributeError: #long_df not set yet
            pass
        
        
    
    def _output_long(self):
        if self.debug:
            return self.long_df
        for var in ['Shift','Shift Date']:
            try:
                self.long_df.drop(var, axis=1, inplace=True)
            except ValueError:
                pass
        return self.long_df
    
    def _long_to_wide(self):
        self._log('Reshaping long to wide.')
        byvars = [self.coid, self.date]
        if self.other_byvars: #add other byvars for correct long_to_wide
            byvars += self.other_byvars
#         if self.freq == 'm':
#             self.long_df.drop(['Year','Month'], axis=1, inplace=True)
        try:
            self.long_df.drop('Shift Date', axis=1, inplace=True)
        except ValueError: #this is the case where time was not shifted
            #Therefore need to create a colindex which is just 0 for the current time period
            self.long_df['Shift'] = 0
        
        widedf = long_to_wide(self.long_df.reset_index(drop=True),
                              groupvars=byvars, values=self.get, colindex='Shift')
        #chop off zeros from contemporaneous
        return widedf.rename(columns={name: name[:-1] for name in widedf.columns \
                                      if name.endswith('0') and name[:name.find('0')] in self.get}) 
    
    def _handle_cumret(self):
        self._log('Cumret detected.')
        cumvars = ['RET']
        if self.abret: cumvars += ['ABRET']
        self.get += ['cum_' + str(c) for c in cumvars] #get will be used in the end for pivot, need to add pivoting variables
        with warnings.catch_warnings(): #cumulate will raise a warning if time is supplied when method is not between
            warnings.simplefilter('ignore') #suppress that warning
            self._log('Cumulating returns with method {} for time {}.'.format(self.cumret, self.time))
            byvars = ['PERMNO', self.date]
            if self.other_byvars:
                byvars += self.other_byvars
                
            self.long_df = cumulate(self.long_df, cumvars, periodvar='Shift Date', method=self.cumret,
                               byvars=byvars, time=self.time, grossify=True)
            
            
            
            ###########TEMP
#             import pdb
#             pdb.set_trace()
            
            
            
            ############
            
        #Now need to remove unneeded periods
        keep_time = self.time
        if self.drop_first:
            keep_time = self.time[1:]
        self.long_df = self.long_df[self.long_df['Shift'].isin(keep_time)]
            
    def _handle_abret(self):
        self._log('Abret detected.')
        assert isinstance(self.abret, int) and not isinstance(self.abret, bool) #True evaluates as int
        assert isinstance(self.window, int)
        
        facs = ['mktrf']
        if self.abret >= 3:
            facs += ['hml','smb']
        if self.abret == 4:
            facs += ['umd']
        if self.abret not in (1,3,4):
            raise ValueError('Currently only supports 1, 3, and 4-factor models (mktrf, hml, smb, umd)')
        
        prior_wind = [i for i in range(0,-self.window - 1,-1)] #e.g. if window = 3, prior_wind = [0, -1, -2, -3]
        self._log('Creating abret window periods.')
        self.long_df = expand_time(self.long_df, datevar=self.newdate, 
                                   freq=self.freq, time=prior_wind, 
                                   newdate='Window Date', shiftvar='Wind')
        self._log('Merging with CRSP to get abret window data as well as regular data.')       
        self.long_df = self._merge_crsp(df=self.long_df, date='Window Date') 
        self._log('Getting Fama-French factors, then running regressions.')
        self.long_df = get_abret(self.long_df, 'key', fulldatevar='Window Date', freq=self.freq,
                                 abret_fac=self.abret, includecoef=self.includecoef,
                                 includefac=self.includefac)
        
        self._log('Dropping unneeded observations (abret window dates).')
        if self.time:
            #keep only observations for shift dates
            self.long_df = self.long_df[self.long_df['Window Date'] == self.long_df['Shift Date']].reset_index(drop=True) 
        else: #didn't get multiple times per period
            #keep only original observations
            self.long_df = self.long_df[self.long_df['Window Date'] == self.long_df[self.date]].reset_index(drop=True)
        self.get += ['ABRET'] #get will be used in the end for pivot, need to add pivoting variables
        
        drop = ['Wind', 'Window Date'] #variables to be dropped
        coefs = ['coef_' + fac for fac in facs]
        if self.includefac: self.get += facs + ['rf']
        if self.includecoef: self.get += coefs + ['const']
        self.long_df.drop(drop, axis=1, inplace=True)
        
    
    def _create_key(self):
        if self.other_byvars:
            self.byvars += self.other_byvars
        self.long_df['key'] = join_col_strings(self.long_df,self.byvars)
    
    def _handle_time(self):
        self._log('Time detected.')
        #Next section only runs if time is not None
        #Ensure time is of the right type
        if isinstance(self.time, int): self.time = [self.time]
        assert (isinstance(self.time, list) and isinstance(self.time[0], int))
        intermediate_periods = False
        if self.cumret:
            self._log('Cumret detected, will generate intermediate periods.')
            intermediate_periods = True
        self._log('Generating periods {} {}'.format(self.time, '+ itermediate' if intermediate_periods else ''))
        self.long_df = expand_time(self.df, intermediate_periods=intermediate_periods, 
                                   datevar=self.date, freq=self.freq, time=self.time)
        self._log('Finished generating periods. Generating key.')
        self.byvars = ['PERMNO', self.date, 'Shift Date']
        self.newdate = 'Shift Date'
        
    def _handle_no_time(self):
        self.long_df = self.df.copy()
        self._log('Generating key.')
        self.byvars = ['PERMNO', self.date]
        self.newdate = self.date
    
    def _check_inputs(self):
        self._log('Checking inputs.')
        
#         if self.debug:
#             self._log('All inputs: ')
#             self._log(str(self.__dict__))

        #Check get
        if isinstance(self.get, list):
            self.get = [item.upper() for item in self.get]
#             for item in self.get:
#                 assert item in ['PRC','RET','SHROUT','VOL','CFACPR','CFACSHR']
        elif isinstance(self.get, str):
            self.get = self.get.upper()
#             assert self.get in ['PRC','RET','SHROUT','VOL','CFACPR','CFACSHR']
            self.get = [self.get]
        else:
            raise ValueError('''Get should be a list or str containing 'PRC','RET','SHROUT','VOL','CFACPR', or 'CFACSHR'.''')

        #Check to make sure inputs make sense
        assert not ((self.abret == False) and (self.window != None)) #can't specify window without abret
        assert not ((self.abret != False) and (self.window == None)) #must specify window with abret
        assert not ((self.abret == False) and (self.includefac == True)) #cannot include factors unless calculating abnormal returns
        assert not ((self.abret == False) and (self.includecoef == True)) #cannot include factor coefs unless calculating abnormal returns
        assert not ((self.abret != False) and ('RET' not in self.get)) #can't calculate abnormal returns without getting returns
        assert not (self.cumret and ('RET' not in self.get)) #can't cumulate returns without getting returns
        assert not (self.cumret and (self.time == None)) #can't cumulate over a single period
        assert not ((self.drop_first == True) and (self.time == None)) #can't drop first shifted time period if there are none
        assert not ((self.drop_first == True) and (len(self.time) == 1)) #can't drop first shifted time period if there's only one
        assert not ((self.drop_first == True) and (self.cumret == False)) #no reason to drop first shifted time period if we're not cumulating


        #Check to make sure company identifier is valid
        assert self.coid in ('GVKEY','TICKER', 'PERMNO', 'PERMCO', 'NCUSIP', 'CUSIP6')
        if self.coid != 'PERMNO':
            self._log('Company ID is not PERMNO. Getting PERMNO.')
            if self.coid == 'GVKEY':
                self.df = get_gvkey_or_permno(self.df, self.date, get='PERMNO',
                                              other_byvars=self.other_byvars) #grabs permno from ccmxpf_linktable
                self._log('Pulled PERMNO from ccmxpf_linktable.')
            else: #all others go through dsenames
                self.df = merge_dsenames(self.df, on=self.coid, date=self.date,
                                        other_byvars=self.other_byvars) #grabs permno
                self._log('Pulled PERMNO from dsenames.')

        #Check to make sure no columns currently in the dataframe have the same name as columns
        #we will be adding
        for col in self.get:
            if col in self.df.columns:
                self.df.rename(columns={col: col + '_old'}, inplace=True)

        #Ensure other_byvars is a list
        if isinstance(self.other_byvars, str):
            self.other_byvars = [self.other_byvars]
        assert isinstance(self.other_byvars, (list, type(None)))
    
    def _load_crsp(self):
        if self.freq.lower() == 'm':
            if not self.loaded_m:
                self.__load_crsp()
            self.loaded_m = True
        if self.freq.lower() == 'd':
            if not self.loaded_d:
                self.__load_crsp()
            self.loaded_d = True
        
    def __load_crsp(self):
        #Check frequency
        if self.freq.lower() == 'm':
            filename = 'msf'
        elif self.freq.lower() == 'd':
            filename = 'dsf'
        else: raise ValueError('use m or d for frequency')
        if self.debug: filename += '_test' #debug datasets only have permnos 10516, 10517

        #Load in CRSP file
        self._log('Loading CRSP dataframe...')
        filepath = os.path.join(self.crsp_dir, filename + '.sas7bdat')
        self.crsp_dfs[self.freq.lower()] = load_sas(filepath)
        self._log('Loaded.')

        #Change date to datetime format
        self._log('Converting SAS date to Pandas format.')
        self.crsp_dfs[self.freq.lower()]['DATE'] = convert_sas_date_to_pandas_date(
                                                    self.crsp_dfs[self.freq.lower()]['DATE'])
        self._log('Converted.')
    
    def _log(self, message):
        if message != '\n':
            time = datetime.datetime.now().replace(microsecond=0)
            message = str(time) + ': ' + message
        sys.stdout.write(message + '\n')
        sys.stdout.flush()
    
    def _merge_crsp(self, df, date):
        self._log('Merging CRSP to dataframe.')
        df = df.copy()

        #If we are using the monthly file, we need to merge on month and year
        if self.freq.lower() == 'm':
            self.crsp_df = self.crsp_dfs['m']
            self.crsp_df = year_month_from_date(self.crsp_df, date='DATE')
            orig_df_for_merge = year_month_from_date(df, date=date)

            #Now perform merge
            merged = orig_df_for_merge.merge(self.crsp_df[['Month','Year','PERMNO'] + self.get],
                                   how='left', on=['PERMNO','Month','Year'])
            merged.drop(['Month','Year'], axis=1, inplace=True)
            
        if self.freq.lower() == 'd':
            self.crsp_df = self.crsp_dfs['d']
            merged = df.merge(self.crsp_df[['DATE','PERMNO'] + self.get],
                              how='left', right_on=['PERMNO','DATE'],
                              left_on=['PERMNO', date])
            merged.drop('DATE', axis=1, inplace=True)
            
        self._log('Completed merge.')

        #Temp
        return merged

    
def get_ff_factors(df, fulldatevar=None, year_month=None, freq='m',
                   subset=None, ff_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\FF'):
    """
    Pulls Fama-French factors and merges them to dataset
    
    df: Input dataframe
    fulldatevar: String name of date variable to merge on. Specify this OR year and month variable. Must use this
                 and not year_month if pulling daily factors. If merging with monthly factors, will create month
                 and year variables in the output dataset. Warning: Will overwrite any variables called Month
                 and Year in the input data.
    year_month: Two element list of ['yearvar','monthvar']. Specify this OR full date variable.
    freq: 'm' for monthly factors, 'd' for daily
    subset: str or list, names of ff factors to pull. Can specify any of 'mktrf', 'smb', 'hml', 'umd'
    ff_dir: folder containing FF data
    """
   
    #Make sure inputs are correct
    assert isinstance(df, pd.DataFrame)
    assert freq in ('d','m')
    assert isinstance(ff_dir, str)
    assert not (fulldatevar == None and year_month == None)
    assert not (fulldatevar == None and freq == 'd')
    
    df = df.copy()
    
    if not subset:
        subset = ['mktrf', 'smb', 'hml', 'umd']
    if isinstance(subset, str):
        subset = [subset]
    assert isinstance(subset, list)
    for item in subset:
        assert item in ['mktrf', 'smb', 'hml', 'umd']
        
    subset = subset.copy() #don't modify original beyond converting to list
    
    if freq == 'm': 
        ff_name = 'ff_fac_month.sas7bdat'
        drop = False
        if year_month != None:
            left_datevars = year_month
            df_for_merge = df
        else: #fulldatevar specified
            df_for_merge = year_month_from_date(df, date=fulldatevar)
            left_datevars = ['Year','Month']
            drop = True
        right_datevars = ['year','month']
    else: 
        drop = False
        df_for_merge = df
        ff_name = 'ff_fac_daily.sas7bdat'
        left_datevars = fulldatevar
        right_datevars = ['date']
        
    subset += right_datevars + ['rf'] #need to pull date variables and risk free rate as well
        
    path = os.path.join(ff_dir, ff_name)
    ffdf = load_sas(path)
    ffdf['date'] = convert_sas_date_to_pandas_date(ffdf['date']) #convert to date object
    
    merged = df_for_merge.merge(ffdf[subset], how='left', left_on=left_datevars, right_on=right_datevars)
    merged.drop(right_datevars, axis=1, inplace=True)
    
    if drop:
        merged.drop(left_datevars, axis=1, inplace=True)
    
    return merged

def get_abret(df, byvars, fulldatevar='Date', year_month=None, freq='m', abret_fac=4, retvar='RET',
              includecoef=False, includefac=False):
    """
    Takes a dataframe containing a column of returns, dates, and at least one by variable and calculates
    abnormal returns for the model of choice. Returns a dataframe with the abnormal returns merged.
    
    Required inputs:
    df: pandas dataframe
    byvars: str or list of strs, column names of columns on which to form by groups
    fulldatevar: str, name of column containing date variable. If provided, don't provide year_month.
    year_month: list of strs, columns names of year and month variables, e.g. ['Year','Month']. Must
                set fulldatevar to None if year_month is provided.
    freq: 'm' or 'd', 'm' for monthly returns, 'd' for daily returns
    abret_fac: int (1, 3, 4), abnormal return model
    retvar: str, name of return variable
    includecoef: bool, set to True to get factor loadings
    includefac: bool, set to True to get factors and risk free rate
    """
    assert abret_fac in (1, 3, 4)
    factors = ['mktrf']
    if abret_fac >= 3:
        factors += ['smb','hml']
    if abret_fac == 4:
        factors += ['umd']
    
    out = get_ff_factors(df, fulldatevar=fulldatevar, freq=freq, subset=factors, year_month=year_month)
    out = factor_reg_by(out, byvars, fac=abret_fac, retvar=retvar)
    
    if not includefac:
        out.drop(factors + ['rf'], axis=1, inplace=True)
    if not includecoef:
        out.drop(['const'] + ['coef_' + fac for fac in factors], axis=1, inplace=True)
        
    return out

def load_and_merge_compustat(df, get=['sale'], freq='a', gvkeyvar='gvkey', datevar='Date', debug=False,
                             comp_dir=r'C:\Users\derobertisna.UFAD\Desktop\Data\Compustat'):
    """
    Convenience function for both loading and merging compustat to existing dataframe.
    
    Required inputs:
    df: Pandas dataframe containing a date variable and gvkey
    
    Optional inputs:
    get: List of strings, variable names to pull from compustat, not including those needed for
         the merge. Do not add the 'q' or 'y' for quarterly variables, this is done automatically.
         'y' variables will be converted to quarterly values by looking at changes.
    freq: string, 'a' or 'q' for annual or quarterly compustat (funda, fundq)
    gvkeyvar: string, name of variable containing gvkeys
    datevar: string, name of date variable in df on which to merge. Will pull the newest data
             that is before or on this date.
    debug: bool, True to restrict to only gvkeys (001076, 001722)
    comp_dir: string, directory containing compustat files
    """
    convert_gvkey(df, gvkeyvar)
    comp = load_compustat(freq, get=get, debug=debug, comp_dir=comp_dir)
    return merge_compustat(df, comp, datevar=datevar).rename(columns={'gvkey':gvkeyvar})