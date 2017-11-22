# coding: utf-8
__all__ = ['merge', 'assemble', 'smooth', 'index']
from datetime import datetime, timedelta # 8.1
from collections import OrderedDict # 8.3
import csv # 14.1
import os # 16.1
import xml.etree.ElementTree as ET # 20.5
import tkinter #25.1
from tkinter.filedialog import askopenfilenames, asksaveasfilename
import sys
from warnings import warn
from contextlib import ExitStack
import inspect 
from scipy.io import loadmat
import numpy as np
import numpy.ma as ma
import pytz
from netCDF4 import Dataset, num2date
    
def merge(fnames, savefname='memory', combine_variables=(), ignore_variables=('time', 'time_bounds'), 
          eliminate_duplicate_variables=True, give_stats=True, complevel=4):
    """Read files and write a NetCDF4 file.
    
    !!! input variables to be described here. See ORACLESmerge for combine_variables and ignore_variables.
     
    # !!! Set eliminate_duplicate_variables False, and the duplicate variables will 
    # !!! be distinguished by a prefix. But the consequences of the name change on 
    # !!! other parts of this code and on data analysis remain to be assessed. For
    # !!! now keep it True.
    """

    ## Prepare to record history and source
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def _setvariableattributes(var, pp, source, timestamp=timestamp): 
        if 'history' not in var.ncattrs():
            var.history = ''
        else:
            var.history = var.history + '\n'
        if 'source' not in var.ncattrs():
            var.source = ''
        else:
            var.source = var.source + '\n'
        var.history = var.history + timestamp + ' ' + pp + ' using ' + inspect.stack()[1][3]
        var.source = var.source + source
    ## Read files, unite variables under a single time array and write a new file
    variables_excluded = []
    keys = []
    # the zeroth file - save it as another file and open it
    # Note that variables are NOT ignored even if they are in ignore_variables 
    if fnames[0]!=savefname: # this allows adding variables to the zeroth file, instead of creating a new save file.
        assemble(fnames[0], savefname)
    if len(fnames)==1:
        return # use merge as assemble
    with Dataset(savefname, 'a') as dataset:
        keys.append(dataset.variables.keys()) # append, not extend
        for key0 in keys[-1]:
            _setvariableattributes(dataset[key0], 'Copied', fnames[0])
        time_bounds = dataset['time_bounds'][:]
        if give_stats:
            stats = ('number_of_samples', 'standard_deviation', '10th_percentile', '25th_percentile', '50th_percentile', '75th_percentile', '90th_percentile')
            percentiles_to_compute = np.array([10., 25, 50, 75, 90])
            statsgroup = dataset.createGroup('stats')
            statsgroup.createDimension('stats', len(stats))
            statsgroup.createDimension('time', dataset.dimensions['time'].size)
            var = statsgroup.createVariable('stats', str, ('stats',))
            var[:] = np.array(stats, dtype='object') 
        # the rest of the files - take their contents, synchronize with the reference time bounds and append the results
        for fname in fnames[1:]:
            prefix = os.path.split(fname)[1].partition('_')[0]
            with assemble(fname) as dataset0:
                keys.append(dataset0.variables.keys()) # append, not extend
                variables = []
                vars0 = []
                dtype = []
                cols = []
                for key0 in keys[-1]:
                    if key0 in ignore_variables or key0 + ' from ' + prefix in ignore_variables:
                        pass
                    elif eliminate_duplicate_variables and any([True for keys in keys[:-1] if key0 in keys]): 
                        variables_excluded.append(key0 + ' from ' + prefix) 
                    else:
                        # register the input variable for merging
                        vars0 = ma.vstack((vars0, dataset0[key0][:])) if len(vars0) else dataset0[key0][:]
                        # prepare the output variable
                        c = [c for c, combine_variable in enumerate(combine_variables) if key0 in combine_variable[0] or key0 + ' from ' + prefix in combine_variable[0]]
                        if c: # to be combined into a matrix
                            varname = combine_variables[c[0]][1]
                            vardimension = combine_variables[c[0]][2]
                            if len(vardimension)>2:
                                raise ValueError('The maximum number of dimension merge creates is two.')
                            elif len(vardimension)==2 and vardimension[1] not in dataset.dimensions.keys():
                                dataset.createDimension(vardimension[1], len(combine_variables[c[0]][0]))
                                # create variable of the same name too, only because doing this later (in ORACLESmerge.ipynb) causes an error
                                dataset.createVariable(vardimension[1], 'f8', (vardimension[1], ))                                
                                if give_stats:
                                    statsgroup.createDimension(vardimension[1], len(combine_variables[c[0]][0]))
                            cols.append(combine_variables[c[0]][0].index(key0) if key0 in combine_variables[c[0]][0] else combine_variables[c[0]][0].index(key0 + ' from ' + prefix))
                        else: # not to be combined but saved as a vector
                            varname = prefix + '_' + key0 if np.any([key0 in keys1 for keys1 in keys[:-1]]) else key0
                            vardimension = dataset0[key0].dimensions
                            cols.append(None)
                        if varname in dataset.variables.keys(): 
                            # the output variable already exists 
                            var = dataset[varname]
                            if give_stats:
                                varstats = statsgroup[varname]
                        else:
                            # determine the least significant digit
                            # Note that the precision of the original values is carried here.
                            # This may not work well if the data do not refer to physical properties.
                            # http://chemistry.bd.psu.edu/jircitano/sigfigs.html
                            # For example, a 0-or-1 flag will remain 0-or-1 after averaging, not allowing values like 0.33 or 0.5.
                            least_significant_digit=dataset0[key0].least_significant_digit if 'least_significant_digit' in dataset0[key0].ncattrs() else None
                            # generate the output variable
                            var = dataset.createVariable(varname, dataset0[key0].datatype, list(vardimension), zlib=True, complevel=complevel, least_significant_digit=least_significant_digit)
                            # copy the attributes 
                            [var.setncattr(attr,dataset0[key0].getncattr(attr)) for attr in dataset0[key0].ncattrs()]
                            if c: # set additional attributes
                                [var.setncattr(attr[0],attr[1]) for attr in combine_variables[c[0]][3]]  
                            # note history and source
                            _setvariableattributes(var, 'Merged', fname)
                            if give_stats:
                                varstats = statsgroup.createVariable(varname, dataset0[key0].datatype, 
                                         ['stats']+list(vardimension),
                                         zlib=True, complevel=complevel, 
                                         least_significant_digit=dataset0[key0].least_significant_digit if 'least_significant_digit' in dataset0[key0].ncattrs() else None)
                                _setvariableattributes(varstats, 'Computed', fname)
                        variables.append(var)
                        # !!! make sure all c values are filled for the matrices
                # synchronize with the reference time array, all variables of the single original file at once
                try:
                    if 'time_bounds' in dataset0.variables.keys():
                        xp = dataset0['time_bounds'][:]
                    else:
                        warn('time_bounds is not given in ' + fname + '. The data are assumed to be instantaneous.')
                        xp = np.vstack((dataset0['time'][:],dataset0['time'][:])).T
                    datacombined0, sum_of_weights0, number_of_elements0, standard_deviation0 = smooth(time_bounds, xp, vars0.T)
                    if give_stats:
                        percentiles0 = ma.empty((np.shape(percentiles_to_compute)[0], np.shape(time_bounds)[0], np.shape(vars0)[0]))
                        percentiles0.mask=True
                        for i, time_bound in enumerate(time_bounds):
                            data1 = vars0.T[(xp[:,0]>=time_bound[0]) & (xp[:,-1]<=time_bound[-1])]
                            if np.any(data1):
                                percentiles0[:,i,:] = np.percentile(data1, percentiles_to_compute, axis=0)
                except ValueError:
                    tb = sys.exc_info()[2]
                    raise ValueError(fname+' ').with_traceback(tb)
                # save each variable
                for v, var in enumerate(variables):
                    if give_stats:
                        varstats = statsgroup[var.name]
                    # Treat the masked data if missing_value is a vector, not a scalar
                    if 'missing_value' in var.ncattrs() and hasattr(var.missing_value, '__len__') and not isinstance(var.missing_value, str): # it's a list, or something like it
                        # Developer's note: Another solution looks promising, has been tested and yet failed. Replacing masked data values to one element of missing_value.
                        # rows = datacombined0[:,v].mask & ~np.in1d(datacombined0[:,v].data, var.missing_value)
                        # datacombined0[rows,v] = ma.array(var.missing_value[0], mask=True)
                        # Raises RuntimeError: cannot assign fill_value for masked array when missing_value attribute is not a scalar
                        # Subtle differences in dtype or least_significant_digit may be the culprit.
                        mv = var.missing_value
                        var.missing_value = mv[0]
                        if give_stats:
                            varstats.missing_value = mv[0]
                    # Assign values
                    # !!! Consolidate the lines below.
                    if isinstance(cols[v], int) and not (len(var.dimensions) == 1 and cols[v] == 0):
                        var[:, cols[v]] = datacombined0[:,v]
                        if give_stats:
                            varstats[0, :, cols[v]] = number_of_elements0[:,v]
                            varstats[1, :, cols[v]] = standard_deviation0[:,v]
                            varstats[2:, :, cols[v]] = percentiles0[:,:,v]
                    else:
                        var[:] = datacombined0[:,v]                        
                        if give_stats:
                            varstats[0, :] = number_of_elements0[:,v]
                            varstats[1, :] = standard_deviation0[:,v]
                            varstats[2:, :] = percentiles0[:,:,v]
                # save headers and note source for the entire dataset
                for ncattr in dataset0.ncattrs():
                    if 'header_' in ncattr:
                        dataset.setncattr_string(ncattr, dataset0.getncattr(ncattr))
                if 'headers' in dataset.ncattrs() and 'headers' in dataset0.ncattrs():
                    dataset.headers = dataset.headers + dataset0.headers
                dataset.source = dataset.source + '\n' + fname 
        # note history
        dataset.history = dataset.history + '\n' + timestamp + ' Merged using ' + inspect.stack()[2][3] + '\n'
    # note the excluded variables
    if variables_excluded:
        warn('The following variables have a duplicate and are excluded.')
        print(tuple(variables_excluded))
    
def assemble(fnames=(), savefname='memory', types=[('All','*')], **subsets):
    """Read files and write a NetCDF4 file.
    
    Examples:
    
    assemble(a_list_of_star_dat_file_paths, a_string_of_a_netCDF4_file_path, 'stardat') # combines raw STAR dat files into a netCDF4 file
    
    from netCDF4 import Dataset
    assemble(Dataset(a_string_of_a_netCDF4_file_path)['SUN'], another_file_name) # copies the SUN group from the netCDF4 file into another
    
    Notes on the use of assemble as part of merge. _readict, which is called for ICARTT-format files, does not minimize the time it takes for combining contents of multiple text files when not involving time adjustment (smoothing) or any numpy operation. Study how _readstardat combines contents *before* netCDF4.Dataset write them appearently via numpy operations.
    """

    # identify source file names, a reader and a savefname
    fnames, reader, savefname = _getfnamesreaderandsavefname(fnames, savefname, types)
    if not fnames or not reader or not savefname:
        return
    
    # read the fnames and write the savefname
    diskless = True if savefname=='memory' else False
    if hasattr(fnames, 'data_model') and fnames.data_model is 'NETCDF4' and fnames.filepath() == 'memory' and savefname == 'memory':
        return fnames
    try:
        dataset = Dataset(savefname, 'w', diskless=diskless, persist=False, format='NETCDF4', clobber='True') # start writing the savefname; do not use the "with", since the netCDF4 file needs to remain open if diskless; diskless is experimental, says netCDF4 instructions, so when it is updated, this code may need to be modified. 
        reader(fnames, dataset, **subsets) # read the fnames and write the savefname
        if diskless: # return the dataset to the memory if a diskless netCDF4 file is requested
            return dataset
        else: 
            dataset.close()
            return None
    except OSError:
        if 'dataset' in locals() and dataset.isopen():
            dataset.close()
        warn('Close the previously loaded dataset first by running dataset.close().')
        warn('Prior to this you may want to save the contents by running dataset.filepath = (path here).')
        raise 
    except:
        if 'dataset' in locals() and dataset.isopen():
            dataset.close()
        raise 

def _getfnamesreaderandsavefname(fnames=(), savefname='', types=('All','*')):
    """get names of fnames, a reader and a savefname."""
    # !!! bring the user interface forward (tried but not working until a second run)
    
    # check the types
    if isinstance(types, str):
        if types.lower() == 'ict':
            types = [("ICARTT Files", "*.ict"), ('All','*')]
            reader = _readict
        elif types.lower() == 'stardat':            
            types = [("STAR Files", "*.dat"), ('All','*')]
            reader = _readstardat
        elif types.lower() == 'nc':            
            types = [("NetCDF  Files", ("*.nc","*.cdf")), ('All','*')]
            import pdb; pdb.set_trace() # check if the type with multiple extensions works with askopenfilenames
            reader = _readnc
    # ask for input files, if fnames are not given
    if not fnames:
        root = tkinter.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.geometry('0x0+0+0')
        root.deiconify()
        root.lift() # a trick described in http://stackoverflow.com/questions/3375227/how-to-give-tkinter-file-dialog-focus/8775120#8775120
        root.focus_force()
        fnames = askopenfilenames(filetypes=types, title='Open files.', parent=root) # this determines the input files unless the user hits cancel
        root.destroy()
    elif isinstance(fnames, str):
        fnames = (fnames,)        
    # determine the reader if it is not given and if fnames are
    if fnames and 'reader' not in locals():
        if hasattr(fnames, 'data_model') and fnames.data_model is 'NETCDF4': 
            reader = _readdataset
        elif not all([os.path.exists(fname) for fname in fnames]):
            raise NotImplementedError('Not all files exist.')
        else:
            exts = set((os.path.splitext(fname)[1].lower() for fname in fnames))
            if len(exts) == 1 and ('.nc' in exts or '.h5' in exts):
                reader = _readnc
            elif len(exts) == 1 and '.cdf' in exts:
                reader = _readnc
            elif len(exts) == 1 and '.ict' in exts:
                reader = _readict
            elif len(exts) == 1 and '.dat' in exts:
                reader = _readstardat # the requirements for this reader should probably be better qualified, since '.dat' is commonly used, not just for STAR instruments.
            elif len(exts) == 1 and '.mat' in exts:
                reader = _readmat # !!! the requirements for this reader should probably be better qualified, since '.mat' is commonly used.
            elif [os.path.splitext(fname)[1] for fname in fnames].count('.xml')==1 and len(fnames)>=2:
                # exactly one xml file is selected, along with one or more data files
                reader = _readiwg1 # !!! to be implemented; Is this an ISO standard?; should this be _readxml?
    # ask for an output file, if a savefname is not given and if fnames are 
    if savefname.lower() in ('disk', 'd'):
        savefname = ''
    if fnames and not savefname:
        root = tkinter.Tk()
        root.withdraw()
        root.overrideredirect(True)
        root.geometry('0x0+0+0')
        root.deiconify()
        root.lift() # a trick described in http://stackoverflow.com/questions/3375227/how-to-give-tkinter-file-dialog-focus/8775120#8775120
        root.focus_force()
        defaultextension = '.nc'
        initialfile = defaultextension
        try: # this clause fails if fnames is not iterable, e.g., a NetCDF4 dataset
            bnames = [os.path.basename(fname) for fname in fnames] # base names without the directory paths 
            # !!! be more flexible: the prefixes should include yyyymmdd for stardat files, though not for ict files... 
            prefixes, suffixes = zip(*[[b[:b.find('_20')], b[b.find('_', b.find('20')+8, b.rfind('.')):]] for b in bnames]) # includes the separators
            if len(set(suffixes)) == 1:
                initialfile = suffixes[0] + initialfile
            if len(set(prefixes)) == 1:
                initialfile = prefixes[0] + initialfile
        except:
            pass
        savefname = asksaveasfilename(defaultextension=defaultextension, title='Save as', initialfile=initialfile, parent=root)
        root.destroy()
    if fnames and savefname.lower() in ('memory', 'm', 'diskless', 'temporary', 'temp', 'np', 'numpy'):
        savefname = 'memory'
    return fnames, reader, savefname
    
def _readict(fnames, dataset, mdi_and_lsd = {'-9999': None, '-9999.9': None, '-9999.99': None}, sep=',', **subsets):   
    """reads ICARTT-formatted files.

    This code first reads the headers of all files and then reads their data arrays. 
    """

    with ExitStack() as stack:
        fobjs = [stack.enter_context(open(fname, 'rU')) for fname in fnames]
        # read the headers
        # Developer's notes: All header lines are saved as they are. In addition, information needed for
        # data organization is extracted. 
        UTC_date_when_data_begin = []
        description_or_name_of_independent_variable = []
        common_header_items = {key: [] for key 
                                  in ('data_interval', 'number_of_variables', 'scale_factors', 
                                      'missing_data_indicators', 'ULOD_FLAG', 'ULOD_VALUE', 
                                      'LLOD_FLAG', 'LLOD_VALUE', 'names')}
        for fobj in fobjs:
            header = ''
            for i, line in enumerate(fobj):
                header = header + line
                if i==0:
                    number_of_lines_in_header = int(line.partition(sep)[0])
                elif i==6:
                    UTC_date_when_data_begin.append(line.replace(' ','').split(sep)[:3])
                elif i==7:
                    common_header_items['data_interval'].append(line)
                elif i==8:
                    description_or_name_of_independent_variable.append(line)
                elif i==9:
                    common_header_items['number_of_variables'].append(int(line))
                    if 'variable_names_and_units' not in locals():
                        variable_names_and_units = [[] for v in range(common_header_items['number_of_variables'][-1])]
                elif i==10:
                    common_header_items['scale_factors'].append(line)
                elif i==11:
                    common_header_items['missing_data_indicators'].append(line)
                elif i>=12 and i<12+common_header_items['number_of_variables'][-1]:
                    variable_names_and_units[i-12].append(''.join(line.splitlines()).split(sep)) 
                elif 'ULOD_FLAG:' in line:
                    common_header_items['ULOD_FLAG'].append(line)
                elif 'ULOD_VALUE:' in line:
                    common_header_items['ULOD_VALUE'].append(line)
                elif 'LLOD_FLAG:' in line:
                    common_header_items['LLOD_FLAG'].append(line)
                elif 'LLOD_VALUE:' in line:
                    common_header_items['LLOD_VALUE'].append(line)
                elif i == number_of_lines_in_header-1: 
                    common_header_items['names'].append(line)
                    dataset.setncattr_string('header_'+os.path.basename(fobj.name).replace('.', '_'), header)
                    break
        # check intra-file header consistency
        # Developer's notes: most items, most obviously UTC_date_when_data_begin, should be allowed 
        # to change from a file to another. But the consolidation of multiple files requires that  
        # certain items be common among them. This includes the number of variables and their names. 
        # The scale factors, missing data indicators, ULOD and LLOD could be allowed to change, albeit 
        # with a complicated coding.
        for key in common_header_items:
            if len(set(common_header_items[key])) != 1:
                raise ValueError('Only files of identical variables can be assembled. ' + key + ' in the header is different between files.')
        data_interval = common_header_items['data_interval'][0].splitlines()[0]  
        scale_factors = ''.join(common_header_items['scale_factors'][0].splitlines()).replace(' ','').split(sep)
        missing_data_indicators = ''.join(common_header_items['missing_data_indicators'][0].splitlines()).replace(' ','').split(sep)
        # !!! ULOD and LLOD items are read, but masks are not applied at this point of code development. 
        ULOD_FLAG = ''.join(common_header_items['ULOD_FLAG'][0][common_header_items['ULOD_FLAG'][0].find('ULOD_FLAG:')+10:].splitlines()).strip()
        ULOD_VALUE = ''.join(common_header_items['ULOD_VALUE'][0][common_header_items['ULOD_VALUE'][0].find('ULOD_VALUE:')+11:].splitlines()).strip()
        LLOD_FLAG = ''.join(common_header_items['LLOD_FLAG'][0][common_header_items['LLOD_FLAG'][0].find('LLOD_FLAG:')+10:].splitlines()).strip()
        LLOD_VALUE = ''.join(common_header_items['LLOD_VALUE'][0][common_header_items['LLOD_VALUE'][0].find('LLOD_VALUE:')+11:].splitlines()).strip()
        if ULOD_VALUE not in ('N/A', 'N/A;'):
            warn(common_header_items['ULOD_VALUE'][0] + ' in ' + fobj.name + ' may not be handled properly.')
        if LLOD_VALUE not in ('N/A', 'N/A;'):
            warn(common_header_items['LLOD_VALUE'][0] + ' in ' + fobj.name + ' may not be handled properly.')
        names = ['time', 'time_bounds'] + ''.join(common_header_items['names'][0].splitlines()).replace(' ','').split(sep)
        bound_offsets = None if float(data_interval) == 0 else [0, float(data_interval)] if 'start' in names[2].lower() else [-float(data_interval)/2, float(data_interval)/2] if 'mid' in names[2].lower() else [-float(data_interval), 0] if 'end' in names[2].lower() else -1
        if bound_offsets == -1:
            bound_offsets = [0, float(data_interval)] 
            warn('Time bounds are not properly expressed in ' + fobj.name + '. The first column is assumed to represent the start time, and the data interval, the time bounds.')
        bound_offsets_least_significant_digit = len(data_interval.partition('.')[2])
        if 'mid' in names[2].lower() and float(data_interval)*10**bound_offsets_least_significant_digit/2!=round(float(data_interval)*10**bound_offsets_least_significant_digit/2): # the cases where the division by two increases the lsd
            bound_offsets_least_significant_digit = bound_offsets_least_significant_digit + 1
        description_or_name_of_independent_variable = [''.join(d.splitlines()).split(sep) for d in description_or_name_of_independent_variable]
        variable_names_and_units.insert(0, description_or_name_of_independent_variable)       
        variable_names_and_units.insert(1, description_or_name_of_independent_variable)       
        # read the data arrays
        # Developer's notes: 
        # "time" is a useful variable when data from multiple days are combined. On other occasions it 
        # is an unnecessary - but hardly harmful - duplicate. 
        arrays = []
        fill_value = '9.969209968386869e+36' # this assumes 'f8' as datatype
        for j, fobj in enumerate(fobjs):
            base_time = datetime.timestamp(datetime(int(UTC_date_when_data_begin[j][0]),int(UTC_date_when_data_begin[j][1]),int(UTC_date_when_data_begin[j][2]), tzinfo=pytz.UTC))
            def _isolateelements(line):
                row = ''.join(line.splitlines()).rstrip(sep).replace(' ','').split(sep) # ntoe the rstrip(sep) is necessary for a minorty of files such as PDI-CDNC_P3_20160831_R0.ict whose lines end with a comma.
                row = [row[0]]+[fill_value if element in (missing_data_indicator, ULOD_FLAG, LLOD_FLAG) else element for element, missing_data_indicator in zip(*(row[1:], missing_data_indicators))]
                return row
            if bound_offsets:
                def _arrangerow(line): # make a closure
                    row = _isolateelements(line)
                    row.insert(0, base_time + float(row[0])) # the zeroth column is assumed to represent the time of the day in seconds 
                    row.insert(1, [float(row[0]) + bound_offsets[0], float(row[0]) + bound_offsets[1]]) # the first column is assumed to represent the time bounds 
                    return row
            else:
                try:
                    boundsindex = [names.index('Start_UTC'), names.index('Stop_UTC')]
                except ValueError:
                    boundsindex = [2, 3]
                    warn('The first two columns of ' + fobj.name + ' are assumed to represent the time bounds.')
                def _arrangerow(line): # make a closure
                    row = _isolateelements(line)
                    row.insert(0, base_time + float(row[0])) # the zeroth column is assumed to represent the time of the day in seconds 
                    row.insert(1, [base_time + float(row[boundsindex[0]-1]), base_time + float(row[boundsindex[1]-1])]) # -1 accounts for the inserts 
                    return row
            arrays.extend([_arrangerow(line) for line in fobj])
        # create dimensions
        dataset.createDimension('time', len(arrays))
        dataset.createDimension('bound', 2)
        # create variables and their attributes
        lsdmethod=2
        if lsdmethod==2:
            least_significant_digits = [max([lsd if lsd or lsd==0 else -9.9 for lsd in col]) for col in zip(*[[-9.9 if c==fill_value else len(c.partition('.')[2]) for c in row[2:]] for row in arrays])]
            least_significant_digits = [None if least_significant_digit==-9.9 else least_significant_digit for least_significant_digit in least_significant_digits]            
        else:
            least_significant_digits = [len(arrays[-1][2].partition('.')[2])] + [mdi_and_lsd[missing_data_indicators[i]] if missing_data_indicators[i] in mdi_and_lsd.keys() else max(len(c.partition('.')[2]),len(missing_data_indicators[i].partition('.')[2])) for i, c in enumerate(arrays[-1][3:])] 
        # If a precision problem did not exist, this line should simply be: least_significant_digits = [len(c.partition('.')[2]) for c in arrays[-1][2:]] # used to be mdi = [float(missing_data_indicators[c-1]) if len(missing_data_indicators[c-1].partition('.')[2]) else int(missing_data_indicators[c-1]) for c in range(len(arrays[-1][2:]))]; least_significant_digits = [len(c.partition('.')[2]) if isinstance(mdi[i], int) else -99999 for i, c in enumerate(arrays[-1][2:])] # If a precision problem did not exist, this line should simply be: least_significant_digits = [len(c.partition('.')[2]) for c in arrays[-1][2:]]
        # mdi_and_lsd added 2017-04-12, to get around the precision problem with -9999.99 missing data indictor (e.g., some items of ORACLES 2016 UND-CAS...R0.ict)
        least_significant_digits.insert(0, least_significant_digits[0])
        lsds = [lsd for lsd in (least_significant_digits[0],bound_offsets_least_significant_digit) if lsd] if bound_offsets else [lsd for lsd in (least_significant_digits[boundsindex[0]-1], least_significant_digits[boundsindex[1]-1]) if lsd] # -1 accounts for the inserts
        least_significant_digits.insert(1, max(lsds) if lsds else None) 
#         least_significant_digits = [None if least_significant_digit==-99999 else least_significant_digit for least_significant_digit in least_significant_digits]
        # Developer's notes: least_significant_digits includes None to overcome the precision issue described in the following website. 
        # http://stackoverflow.com/questions/16845063/how-to-read-netcdf-variable-float-data-into-a-numpy-array-with-the-same-precisio
        if subsets.keys():
            raise NotImplementedError('subsets for _readict.')
        for n, array in enumerate(zip(*arrays)):
            datatype = 'f8' # !!! study the following: # datatype = 'i4' if lsd == 0 else 'f4' if lsd < 7 else 'f8' . Pay attention to fill value too if we replace missing data with it.
            dimension = ('time', 'bound') if n==1 else ('time',)
            var = dataset.createVariable(names[n], datatype, dimension, 
                                     zlib=True, least_significant_digit=least_significant_digits[n]) # !!! allow complevel as an optional input
            if n == 0: # time
                var.units = 'seconds since 1970-01-01 00:00:00.0'
                var.bounds = 'time_bounds' # this attributes indicates the connection to the first variable, per DOE Arm convention section 7.2.3
            elif n == 1 and bound_offsets: # time_bounds
                var.bound_offsets = bound_offsets
            else:
                for z, items in enumerate(zip(*variable_names_and_units[n-1])):
                    if z == 1 and len(set(items)) == 1: # register units if all files agree on what they are
                        var.units = items[0].strip()
                    if z == 2 and len(set(items)) == 1: # register long_name if all files agree on what it is
                        var.long_name = items[0].strip()
                if n > 2: # dependent variables              
                    # !!! check with Michael Diamond to see if missing_data_indicators needs to be converted to int or float 
                    # float() inserted on 20171115. This is in response to an error that the multiple missing values appear connected like -9999-7777-8888. This field used to look like [-9999. -7777. -8888.], before I updated Anaconda, numpy and netCDF4-Python on 20171115. 
                    var.missing_value = [float(missing_data_indicators[n-3]), float(ULOD_FLAG), float(LLOD_FLAG)] # missing_value as a vector; updated 2017/02/24; was var.missing_value = mdi[n-2]                     
#                     var.missing_value = [mdi[n-2], ULOD_FLAG, LLOD_FLAG] # missing_value as a vector; updated 2017/02/24; was var.missing_value = mdi[n-2]                     
                    if scale_factors[n-3] != '1':
                        sf = float(scale_factors[n-3]) if len(scale_factors[n-3].partition('.')[2]) else int(scale_factors[n-3])
                        var.scale_factor = sf
            var[:] = array # convert a list to a numpy array only once for each variable; this seems faster than row-by-row conversion, though the latter method may use less memory.
        # note history and source
        _setglobalattributes(dataset, fnames)
    
def _readstardat(fnames, dataset, **subsets):   
    """Reads STAR dat files.
    
    For information on STAR instruments, see, for example, https://airbornescience.nasa.gov/instrument/4STAR
    For all files but "track", the raw file must have comment lines each starting with "%", a line filled with as many labels as the data columns, before the array of data. The first seven columns of data must be year, month, day, hour, minute, second, milisecond. The last columns labeled Pix# are the raw spectra. The file name has a YYYYMMDD string that starts with '20' and is followed by an underscore, 20160503_001_ or 2STAR_20160706_016_ for example, before the data type like VIS_SUN. 
    This code fuses data from multiple spectrometers (e.g., VIS and NIR), unlike allstarmat.m. 
    The change takes advantage of the recent stability of 4STAR raw data file formats and improves the readability of the codes for subsequent data processing. 
    This code needs to be modified for a combination of spectrometers that generate dissimilar time arrays.
    This code creates a group under the dataset for each operation or scan, and uses another function, _readstardatforagroup, for reading files for each group.

    Yohei, 2016-05-08, 2016-07-14, 2016-08-15, 2016-11-04, 2017-06-05
    """

    # sort the input files without opening them 
    spcnamestochoosefrom = ['VIS', 'NIR'] # spectrometer names as they may appear in raw file names; raw data are to be combined in the order specified here
    if os.path.basename(fnames[0]).startswith('4STARB'):
        # do not flip left and right
        spcwascendingtochoosefrom = [True, True] # the order of wavelengths; If False, the raw data are swapped left and right
    else:
        # flip left and right for the NIR
        spcwascendingtochoosefrom = [True, False] # the order of wavelengths; If False, the raw data are swapped left and right
    operationscontinuous = ['SUN', 'park', 'ZEN', 'MANUAL'] # operations for which data are to be combined between time periods; excludes scans such as 'SKYA', 'SKYP', 'FOVA' and 'FOVP'; 'FORJ' could be either included or excluded. 
    operationsindependentofspc = ['TRACK'] # operations independent of spectrometers; assumed continuous    
    # determine datatype (like VIS_SUN) and operations (like SUN, SKYP, C0)
    # Developer's notes:
    # The sorting by operation allows the code to avoid reading all raw files at once, thereby keeping memory use low.
    # Files are not sorted by file name. The reasons include the insignificance of the possible inconvenience as a result; the shorter code; the expected ease and freedom of manually ordering the input files in the way the user wants.   
    bnames = [os.path.basename(fname) for fname in fnames] # base names without the directory paths 
    prefixes, filens, datatypes = zip(*[[b[:b.find('_', b.find('20')+8)], b[b.find('_', b.find('20')+8)+1:b.find('_', b.find('_', b.find('20')+8)+1)], 
                              b[b.find('_', b.find('_', b.find('20')+8)+1)+1:b.find('.')]] for b in bnames]) # read the letters between the second underscore and the first period
    if all([str(datatype).startswith('C0_') for datatype in datatypes]): # all are C0 files
        spcsused = list(filens) # account for the convention that the c0 file names do not have file numbers such as 001
        fnamessorted = [fnames[spcsused.index(s)] for s in spcnamestochoosefrom if s in spcsused] # order (e.g., ensure that VIS is read before NIR)
        if subsets.keys():
            raise ValueError('subsets for reading c0 files.')
        _readstarc0dat(fnamessorted, dataset)
        # note history and source
        _setglobalattributes(dataset, [fname for fname in fnamessorted])
    elif any([str(datatype).startswith('C0_') for datatype in datatypes]):
        raise ValueError('Do not mix c0 files with other types of STAR files.')
    else: # STAR dat files that are not c0 files
        operations = set([d[d.find('_')+1:] for d in datatypes])
        # sort the operations into three categories - continuous and spectrometer-dependent, scanning and spectrometer-dependent, continuous and spectrometer-independent, calibration 
        operations = [[p for p in operationscontinuous if p in operations], 
                      [p for p in operations if p not in operationscontinuous if p not in operationsindependentofspc], 
                      [p for p in operationsindependentofspc if p in operations]] # place continuous operations at the beginning, those independent of spectrometers at the end, and the rest in the middle; this line of code arranges the saved groups in a semi-fixed order, in addition to facilitating data aggregation
        # match up all spectrometers for each operation; check whether the operations have pairing raw files (e.g., ..._003_VIS_SUN.dat and ..._003_NIR_SUN.dat), unless independent of spc (e.g., TRACK)
        spcsused = set([d[:d.find('_')] for d in datatypes if '_' in d])
        spcnames, spcwascending = zip(*[(s, spcwascendingtochoosefrom[i]) for i, s in enumerate(spcnamestochoosefrom) if s in spcsused])
        fnamessorted = OrderedDict()
        prefixfilensforoperations = {}
        for operation in operations[0]+operations[1]: # operations for all spectrometers
            if any([j for j in datatypes if j == operation]):
                raise ValueError('Specify spectrometer for ' + operation + ' files.')            
            for spcname in spcnames:
                fnamesi, prefixfilensi = zip(*[[fnames[i], prefixes[i]+'_'+filens[i]] for i, j in enumerate(datatypes) if j == spcname + '_' + operation])
                if prefixfilensforoperations.setdefault(operation, prefixfilensi) != prefixfilensi:        
                    raise ValueError('Select ' + operation + ' files for all spectrometers.')
                fnamessorted.setdefault(operation, []).append(fnamesi)
            prefixfilensforoperations[operation] = prefixfilensi
        for operation in operations[2]: # operations independent of spectrometers (e.g., TRACK)
            fnamesi, prefixfilensi = zip(*[[fnames[i], prefixes[i]+'_'+filens[i]] for i, j in enumerate(datatypes) if j == operation])
            prefixfilensforoperations.setdefault(operation, prefixfilensi)
            fnamessorted.setdefault(operation, []).append(fnamesi)
            for spcname in spcnames:
                if any([j for j in datatypes if j == spcname + '_' + operation]):
                    raise ValueError('Do not specify spectrometer for ' + operation + ' files.')
        # read input and write output
        for operation in operations[0]: # continuous operations, dependent on spectrometer
            _readstardatforagroup(fnamessorted[operation], spcnames, spcwascending, dataset.createGroup(operation), **subsets)
            # note history and source
            _setglobalattributes(dataset[operation], [fname for fnames in fnamessorted[operation] for fname in fnames])
        for operation in operations[1]: # scanning operations, dependent on spectrometer
            groupforoperation = dataset.createGroup(operation)
            for j, prefixfilen in enumerate(prefixfilensforoperations[operation]):
                    _readstardatforagroup([[fnames[j]] for fnames in fnamessorted[operation]], spcnames, spcwascending, groupforoperation.createGroup(prefixfilen), **subsets)
                    # note history and source
                    _setglobalattributes(groupforoperation[prefixfilen], [fnames[j] for fnames in fnamessorted[operation]])
        for operation in operations[2]: # operations independent of spectrometer
            if operation != 'TRACK':
                raise NotImplementedError(operation + ' not implemented.')
            _readstartrackdat(fnamessorted[operation], dataset.createGroup(operation), **subsets)
            # note history and source
            _setglobalattributes(dataset[operation], [fname for fnames in fnamessorted[operation] for fname in fnames])                

def _readstarc0dat(fnamessorted, group):
    """Reads STAR c0 dat files.
    
    Note that this code does not reverse the order of rows, even for spectrometers with descending wavelengths (e.g., NIR)."""

    with ExitStack() as stack:
        fobjs = [stack.enter_context(open(fname)) for fname in fnamessorted]
        group.headers = ''
        arrays = []
        for f in range(len(fobjs)):
            for line in fobjs[f]: # the for-loop lasts only for the headers
                group.headers = group.headers + line
                if not line.startswith('%'): # the column header has just been read 
                    namesf = line.split() # note that this line assumes the separator is a blank
                    if namesf != ['Pix', 'Wavelength', 'C0', 'C0err']:
                        raise ValueError('Header of ' + fnamessorted[f] + '.')
                    arrays.extend([line.split() for line in fobjs[f]])
        # create dimensions
        group.createDimension('wavelength', len(arrays))
        # create variables and their attributes
        least_significant_digits = [0] + [len(c.partition('.')[2]) for c in arrays[-1][1:]]
        least_significant_digits[namesf.index('Wavelength')] += 3 # prepare for unit conversion
        for n, array in enumerate(zip(*arrays)):
            datatype = 'f8' # !!! study the following: # datatype = 'i4' if lsd == 0 else 'f4' if lsd < 7 else 'f8' 
            var = group.createVariable(namesf[n], datatype, ('wavelength',), 
                                     zlib=True, least_significant_digit=least_significant_digits[n]) # !!! allow complevel as an optional input
            var[:] = array # convert a list to a numpy array only once for each variable; this seems faster than row-by-row conversion, though the latter method may use less memory.
        group['Wavelength'][:] /= 1000
        group['Wavelength'].units = 'um'
        
def _readstartrackdat(fnamessorted, group, **subsets):
    """Reads STAR TRACK dat files."""
    if subsets.keys():
        raise NotImplementedError('subsets for _readstartrackdat.')
    with ExitStack() as stack:
        fobjs = [stack.enter_context(open(fname)) for fname in fnamessorted[0]]
        arrays = []
        fill_value = '9.969209968386869e+36' # this assumes 'f8' as datatype
        header = ''
        for fobj in fobjs:
            for i, line in enumerate(fobj):
                header = header + line
                if i==0: # get the base date from the file name
                    basedate = line[line.find('20'):line.find('_', line.find('20')+8)]
                elif i==1:
                    break
            base_time = datetime.timestamp(datetime(int(basedate[:4]),int(basedate[4:6]),int(basedate[6:]), tzinfo=pytz.UTC))
            def _arrangerow(line): # make a closure
                row = line.split()
                row.insert(0, base_time+(int(row[1][:2])*60+int(row[1][3:5]))*60+float(row[1][6:])) # avoid running datetime for each line
                row.pop(2)
                return row
            arrays.extend([_arrangerow(line) for line in fobj])
        names = ['time']+header.splitlines()[1].replace('Azim Angle','Azim_Angle').replace('Azim Error','Azim_Error').replace('Azim pos','Azim_Pos').replace('Elev Angle','Elev_Angle').replace('Elev Error','Elev_Error').replace('Elev Pos','Elev_Pos').replace('Time','').split()
        # create dimensions
        group.createDimension('time', len(arrays))
        # create variables and their attributes
        for n, array in enumerate(zip(*arrays)):
            datatype = 'f8' # !!! study the following: # datatype = 'i4' if lsd == 0 else 'f4' if lsd < 7 else 'f8' . Pay attention to fill value too if we replace missing data with it.
            dimension = ('time',)
            var = group.createVariable(names[n], datatype, dimension, 
                                     zlib=True, least_significant_digit=None if n==0 or n==2 else 6) # !!! allow complevel as an optional input
            if n == 0: # time
                var.units = 'seconds since 1970-01-01 00:00:00.0'
            var[:] = array
        group.header = header
            
def _readstardatforagroup(fnamessorted, spcnames, spcwascending, group, **subsets):
    """Reads STAR dat files.

    This code first reads the headers of all files and then reads their data arrays. 
    The code assumes that the first seven columns of each raw file has integer, each expressing year, month, day, hour, minute, second, millisecond. Other variables do not need to exist in all spectrometer files.
    """

    with ExitStack() as stack:
        fobjs = [[stack.enter_context(open(fname)) for fname in fnames] for fnames in fnamessorted]
        # read the headers
        group.headers = ''
        names = ['time', 'time_for_each_spectrometer', 'raw'] # !!! add time_bounds, after the DOE Arm convention 7.2.3., once the arrangement is tested with ict files.
        varforraw = 'Pix0' # the first (left-most) in the raw files among the columns for raw counts  
        missing_value = '-9999' # missing value for raw; !!! should this replace None in the other fields?
        basecol = 0
        nrawcols = [0]
        unsortednames = []
        indices = [[], [() for f in range(len(fobjs))], []]
        for j in range(len(fobjs[0])):
            namesj = []
            for f in range(len(fobjs)):
                for line in fobjs[f][j]: # the for-loop lasts only for the headers
                    group.headers = group.headers + line
                    if not line.startswith('%'): # the column header has just been read 
                        namesf = line.split() # note that this line assumes the separator is a blank
                        namesj.extend(namesf)
                        if not unsortednames: # prepare to arrange the arrays - time, raw counts and all others
                            # time, the first seven columns
                            indices[names.index('time_for_each_spectrometer')][f] = range(basecol, basecol+7)
                            # raw counts, the specifically marked column and all others to its right 
                            rawcol = namesf.index(varforraw)
                            if spcwascending[f]:
                                indices[-1].extend(list(range(basecol+rawcol, basecol+len(namesf))))
                            else: # the raw data are ordered in the descending order of wavelength; reverse the column order
                                indices[-1].extend(list(range(basecol+len(namesf)-1, basecol+rawcol-1, -1)))
                            # all other variables
                            for n, name in enumerate(namesf[7:rawcol]):
                                if name in names:
                                    indices[names.index(name)][f]=basecol+n+7                                    
                                else:
                                    names.insert(-1, name)
                                    indices.insert(-1, [basecol+n+7 if f==i else None for i in range(len(fobjs))])
                            basecol = basecol + len(namesf)
                            nrawcols.append(nrawcols[-1] + len(namesf) - rawcol)
                        break
            # check whether the variable names are the same as those of other files of the same data type, if any
            if not unsortednames:
                unsortednames = namesj
            elif unsortednames != namesj: 
                raise ValueError('The column header of ' + ''.join([fobj[j].name + ' ' for fobj in fobjs]) + 'is different from that in other files of the same data type.')        
        # read the data arrays
        def _resolverow(line):
            row = ''.join([l for l in line]).split()
            return row
        arrays = []
        for fobjsj in zip(*fobjs):
            try:
                base_timestr = fobjsj[0].name[fobjsj[0].name.find('20'):] # estimate the datestamp from the file name, so line-by-line application of datetime may be avoided later.
                base_timestr = base_timestr[:4], base_timestr[4:6], base_timestr[6:8]
                base_time = datetime.timestamp(datetime(int(base_timestr[0]),int(base_timestr[1]),int(base_timestr[2]), tzinfo=pytz.UTC))
            except ValueError:
                base_timestr = None, None, None
                base_time = 0
            # four different cases (all variables common among all spectrometers or not, raw filled or missing), each with a complicated way of reading each line. 
            if all([all([isinstance(i, int) for i in index]) for name, index in zip(names, indices) if name != 'time' and name != 'time_for_each_spectrometer']): # indices does not include an empty item
                def _sortrow(row):
                    try:
                        t = [base_time + (int(row[index[3]]) * 60 +int(row[index[4]])) * 60 + int(row[index[5]]) + int(row[index[6]])/1000 
                             if row[index[0]] == base_timestr[0] and row[index[1]] == base_timestr[1] and row[index[2]] == base_timestr[2]
                             else datetime.timestamp(datetime(*[int(row[i]) for i in index[:-1]], int(row[index[-1]])*1000, tzinfo=pytz.UTC))
                             for index in indices[names.index('time_for_each_spectrometer')]] 
                        row = [t[0]] + [t] + [[row[i] for i in index] for name, index in zip(names, indices) if name not in ('time', 'time_for_each_spectrometer')]
                    except: # for rows with miscallenous data only and no spectrometer counts
                        t = [base_time + (int(row[index[3]-nrawcols[j]]) * 60 +int(row[index[4]-nrawcols[j]])) * 60 + int(row[index[5]-nrawcols[j]]) + int(row[index[6]-nrawcols[j]])/1000 
                             if row[index[0]-nrawcols[j]] == base_timestr[0] and row[index[1]-nrawcols[j]] == base_timestr[1] and row[index[2]-nrawcols[j]] == base_timestr[2]
                             else datetime.timestamp(datetime(*[int(row[i-nrawcols[j]]) for i in index[:-1]], int(row[index[-1]-nrawcols[j]])*1000, tzinfo=pytz.UTC))
                             for j, index in enumerate(indices[names.index('time_for_each_spectrometer')])] 
                        row = [t[0]] + [t] + [[row[i-nrawcols[j]] for j, i in enumerate(index)] for name, index in zip(names, indices) if name not in ('time', 'time_for_each_spectrometer', 'raw')] + [[missing_value for index in indices[names.index('raw')]]]
                    return row
            else: # indices includes an empty item
                def _sortrow(row):
                    try:
                        t = [base_time + (int(row[index[3]]) * 60 +int(row[index[4]])) * 60 + int(row[index[5]]) + int(row[index[6]])/1000 
                             if row[index[0]] == base_timestr[0] and row[index[1]] == base_timestr[1] and row[index[2]] == base_timestr[2]
                             else datetime.timestamp(datetime(*[int(row[i]) for i in index[:-1]], int(row[index[-1]])*1000, tzinfo=pytz.UTC))
                             for index in indices[names.index('time_for_each_spectrometer')]] 
                        row = [t[0]] + [t] + [[row[i] if isinstance(i, int) else None for i in index] for name, index in zip(names, indices) if name not in ('time', 'time_for_each_spectrometer')]
                    except: # for rows with miscallenous data only and no spectrometer counts
                        t = [base_time + (int(row[index[3]-nrawcols[j]]) * 60 +int(row[index[4]-nrawcols[j]])) * 60 + int(row[index[5]-nrawcols[j]]) + int(row[index[6]-nrawcols[j]])/1000 
                             if row[index[0]-nrawcols[j]] == base_timestr[0] and row[index[1]-nrawcols[j]] == base_timestr[1] and row[index[2]-nrawcols[j]] == base_timestr[2]
                             else datetime.timestamp(datetime(*[int(row[i-nrawcols[j]]) for i in index[:-1]], int(row[index[-1]-nrawcols[j]])*1000, tzinfo=pytz.UTC))
                             for j, index in enumerate(indices[names.index('time_for_each_spectrometer')])] 
                        row = [t[0]] + [t] + [[row[i-nrawcols[j]] if isinstance(i, int) else None for j, i in enumerate(index)] for name, index in zip(names, indices) if name not in ('time', 'time_for_each_spectrometer', 'raw')] + [[missing_value for index in indices[names.index('raw')]]]
                    return row
            def _arrangerow(line): # make a closure
                row = _sortrow(_resolverow(line))
                return row    
            arrays.extend([_arrangerow(line) for line in zip(*fobjsj)])
        # create dimensions
        if subsets.keys():
            raise NotImplementedError('subsets for _readstardatforagroup.')
        group.createDimension('time', len(arrays))
        group.createDimension('wavelength', nrawcols[-1])
        group.createDimension('spectrometer', len(fobjs))
        # create variables and their attributes
        if arrays: 
            least_significant_digits = [3] + [3] + [max([len(cc.partition('.')[2]) for cc in c]) for c in arrays[-1][2:]]
        else: # empty sky scans, for example
            least_significant_digits = [None for name in names]
        dimensions = [('time',) if n=='time' else ('time', 'wavelength') if n == 'raw' else ('time', 'spectrometer') for n in names]
        for n, array in enumerate(zip(*arrays)):
            datatype = 'f8' # !!! study the following: # datatype = 'i4' if lsd == 0 else 'f4' if lsd < 7 else 'f8' 
            var = group.createVariable(names[n], datatype, dimensions[n], 
                                     zlib=True, least_significant_digit=least_significant_digits[n]) # !!! allow complevel as an optional input
            if names[n] == 'time' or names[n] == 'time_for_each_spectrometer':
                var.units = 'seconds since 1970-01-01 00:00:00.0'
            if names[n] == 'time_for_each_spectrometer':
                var.long_name = 'time given in raw files of each spectrometer, for record keeping only.'
            elif names[n] == 'raw':
                var.long_name = 'Raw Counts'
                var.missing_value = float(missing_value)
            var[:] = array # convert a list to a numpy array only once for each variable; this seems faster than row-by-row conversion, though the latter method may use less memory.
        var = group.createVariable('spectrometer', str, ('spectrometer',))
        var[:] = np.array(spcnames, dtype='object')
        var = group.createVariable('index_of_spectrometer', 'u1', ('wavelength',))
        var[:] = [s for s in range(len(spcnames)) for i in range(nrawcols[s+1]-nrawcols[s])]
        
def _readdataset(dataset0, dataset, **subsets):
    """Reads a single NetCDF4 dataset (not a NetCDF4 file).
    """

    # Developer's notes: Once nccopy becomes available under NetCDF4-Python and if it takes care
    # of all contents (including user defined types), replace this function with it. Allow it to 
    # select subsets.
    
    # Developer's notes: Future versions may convert the "time" (from DOE ARM's expressions) to base 1970-1-1. This is not necessary, unlike when multiple files with varying time bases are merged. But _readnc must make this adjustment, so _readdataset might as well.
    
    [_readdataset(dataset0[key], dataset.createGroup(key)) for key in dataset0.groups.keys()] # caution: this line risks an infinite loop!
    [dataset.setncattr(k, dataset0.getncattr(k)) for k in dataset0.ncattrs()]
    if 'variables' not in subsets.keys():
        subsets['variables'] = dataset0.variables.keys()
    obj, dimensions = index(dataset0, **subsets)
    [dataset.createDimension(name, np.sum(val)) for name, val in dimensions.items()]
    for name in subsets['variables']:
        variable = dataset0[name]
        var = dataset.createVariable(name, variable.datatype, variable.dimensions,
                                     zlib=True, 
                                     least_significant_digit=variable.least_significant_digit if 'least_significant_digit' in variable.ncattrs() else None)
        try:
            # Developer's note: 
            # The [:] below on the right-hand side may seem unnecessary, but it speeds up the process for some cases.
            # Without this, variable[:,(60, 120)] would be very slow, even though variable[:,(120, 60)] is fast. Very puzzling.
            # This phenomenon is possibly related to (6) in http://unidata.github.io/netcdf4-python/
            # Also, it is to be seen whether the line below causes an error ("cannot assign fill_value for masked array when 
            # missing_value attribute is not a scalar") under the following conditions: 
            # variable[:] is a masked array, missing_value is a vector rather than a scalar, at least one masked element has a 
            # value (.data) that is not among the missing_value. 
            var[:] = variable[:][obj[name]]
        except:
            # !!! to-do: Explicitly reject user defined types like enum, opaque, compound and variablelength 
            warn(name + ' not copied.')
        var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
    # note history and source
    _setglobalattributes(dataset, dataset0.filepath() + ' ' + dataset0.name if 'name' in dataset0.ncattrs() else dataset0.filepath())
#     if dataset0.filepath() == 'memory': # note the history and source only if the dataset originates from the memory. (If it originates from a file, do this in the code where the file is opened - _readnc.)
#         _setglobalattributes(dataset, 'the memory')

def _readnc(fnames, dataset, **subsets):   
    """Reads NetCDF4 files (not NetCDF4 datasets).
    """

    if len(fnames)==1:
        # Simple transfer of the contents.
        # Developer's note: Do not merge _readdataset here. _readdataset has its value as a standalone subfunction when a dataset is assigned as input to assemble.
        with Dataset(fnames[0]) as dataset0:
            # Avoid masked array which is unnecessary for dataset0 and, if missing_value is a vector, would cause an error when saving in dataset.
            # Note that dataset, unlike dataset0, does produce masked arrays.
            dataset0.set_auto_mask(False) 
            _readdataset(dataset0, dataset, **subsets)
    else:
        # Combining requires intra-dataset consistency check on variables and dimensions 
        # (and attributes and groups?), similar to _readict.
        # MFDataset does not treat ARM's time stamps well. It does a great job otherwise.
        # Additional note 2017-11-18: Use MFTime and MFDatasetss. Oops never mind, NetCDF4 is not supported.
                
        # read all files
        i = 0
        for f, fname in enumerate(fnames):
            with Dataset(fname) as dataset0:
                # Avoid masked array which is unnecessary for dataset0 and, if missing_value is a vector, would cause an error when saving in dataset.
                # Note that dataset, unlike dataset0, does produce masked arrays.
                dataset0.set_auto_mask(False) 
                if f==0:
                    # create dimensions
                    if 'variables' not in subsets.keys():
                        subsets['variables'] = dataset0.variables.keys()
                    if 'time' not in subsets['variables']:
                        subsets['variables'] = ['time']+[v for v in subsets['variables']]
                    obj, dimensions = index(dataset0, **subsets)
                    [dataset.createDimension(name, None if name=='time' else np.sum(val)) for name, val in dimensions.items()]
#                     dataset.createDimension('source', len(fnames)) # added for combining multiple files
                    variablestobesaved = {}
                    for name in subsets['variables']:
                        variable = dataset0[name]
                        dimensions = variable.dimensions
#                         if 'time' not in dimensions:
#                             dimensions = dimensions + ('source',)
                        if 'time' in dimensions:
                            var = dataset.createVariable(name, variable.datatype, dimensions,
                                                         zlib=True, 
                                                         least_significant_digit=variable.least_significant_digit if 'least_significant_digit' in variable.ncattrs() else None)
                            var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
                            if name=='time':
                                var.units = 'seconds since 1970-01-01 00:00:00.0'
                                var.long_name = 'Time'
                        else:
                            variablestobesaved[name] = [[] for i in range(len(fnames))] 
#                 # check if the file format is simple enough for this code to handle                
#                     # !!! to-do: Explicitly reject user defined types like enum, opaque, compound and variablelength            
#                     [_readdataset(dataset0[key], dataset.createGroup(key)) for key in dataset0.groups.keys()] # caution: this line risks an infinite loop!
#                     # !!! to-do: copy (append, actually) group attributes            
#     [dataset.setncattr(k, dataset0.getncattr(k)) for k in dataset0.ncattrs()]
                # get the time expression right
                # !!! works if 'base_time' is available (e.g., ARM files) but not necessarily with other netCDF4 files
                obj, _ = index(dataset0, **subsets)
                if 'base_time' in dataset0.variables.keys():
                    dataset['time'][:] = np.concatenate((dataset['time'][:], dataset0['time'][:][obj['time']] + dataset0['base_time'][:]), axis=0)
                else:
                    dataset['time'][:] = np.concatenate((dataset['time'][:], dataset0['time'][:][obj['time']]), axis=0)
#                 dataset['time'][:] = np.concatenate((dataset['time'][:], dataset0['time'][:] + dataset0['base_time'][:]), axis=0)
                i1 = dataset['time'].shape[0]
                for name in subsets['variables']:
                    if name not in dataset.variables.keys() and name not in variablestobesaved.keys():
                        raise ValueError(name + ' exists in ' + fname + ' but not in ' + fnames[0] + '.')
                    if name=='time':
                        pass
                    elif name in dataset.variables.keys() and 'time' in dataset[name].dimensions: 
                        obj1 = [slice(i, i1) if d == 'time' else slice(None) for d in dataset[name].dimensions]
                        dataset[name][obj1] = dataset0[name][:][obj[name]]
                    else:
                        # store the values for the layer corresponding to this source file
#                         dataset[name][...,f] = dataset0[name][:][obj[name]]
                        variablestobesaved[name][f] = dataset0[name][:][obj[name]]
                    # !!! append the attributes
                i = i1
                # arrange and save the variables that do not have time among their dimensions
                if f==len(fnames)-1:
                    for key, val in variablestobesaved.items():
                        dims = [np.shape(val[f]) for f in range(len(fnames))]
                        variationsindims = [False if len(set(dimss))==1 else True for dimss in zip(dims)]
                        if len(set(dims))==1 and np.all([val1==val[0] for val1 in val]):                
                            # same shape and same values - save the zeroth item only
                            variable = dataset0[key]
                            var = dataset.createVariable(key, variable.datatype, variable.dimensions,
                                                         zlib=True, 
                                                         least_significant_digit=variable.least_significant_digit if 'least_significant_digit' in variable.ncattrs() else None)
                            var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
                            var[:] = val[0]
#                        elif len(set(dims))==1 or sum(variationsindims)==1:             
#                            # same shape, or same shapes for all but one dimension - stack on the zeroth or that single axis
#                            axisforstack = variationsindims.index(True) if True in variationsindims else 0
#                            # dimensions = #!!! add along all but the one axis
#                            variable = dataset0[key]
#                            var = dataset.createVariable(key, variable.datatype, dimensions,
#                                                         zlib=True, 
#                                                         least_significant_digit=variable.least_significant_digit if #'least_significant_digit' in variable.ncattrs() else None)
 #                           var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
 #                           try:
 #                               var[:] = [val[f] for f in range(len(fnames))]
 #                           except:
 #                               import pdb; pdb.set_trace()
                        # else - create 'source' as a new dimension and save
                        else:
                            if 'source' not in dataset.dimensions.keys():
                                dataset.createDimension('source', len(fnames)) # added for combining multiple files
                            variable = dataset0[key]
                            var = dataset.createVariable(key, variable.datatype, variable.dimensions+('source',),
                                                         zlib=True, 
                                                         least_significant_digit=variable.least_significant_digit if 'least_significant_digit' in variable.ncattrs() else None)
                            var.setncatts({k: variable.getncattr(k) for k in variable.ncattrs()})
                            # !!! TO BE DONE: bring the zeroth axis (for source) to the last !!!
                            var[:] = val
        # note history and source
        _setglobalattributes(dataset, fnames)

def _readmat(fnames, dataset, **subsets):   
    """Reads mat files.
    """
    if len(fnames)==1:
        if np.any([key for key in subsets.keys() if key!='variables']):
            raise NotImplementedError('Only "variables" is accepted as a key for subsets.')
        if 'variables' not in subsets.keys():
            subsets['variables'] = None
        try:
            dataset0 = loadmat(fnames[0], variable_names=subsets['variables'])
            # get the time
            if 't' in dataset0.keys():
                if 'time' in dataset0.keys():
                    warn('Both t and time exist in the mat file. No conversion is being made.')
                elif min(dataset0['t'])>370:
                    # assume this is the Matlab time
                    dataset0['time'] = np.array([datetime.timestamp(datetime.fromordinal(int(t)) + timedelta(days=t%1) - timedelta(days = 366)) for t in dataset0['t'].squeeze()])
                else:
                    raise NotImplementedError('More time formats to be accepted.')
            # identify the dimensions
            # Do this before the potentially lengthy saving process
            dimensions = ['time', np.shape(dataset0['time'])[0]]
            if 'star' in fnames[0].lower() and 'w' in dataset0.keys():
                # A special treatment for STAR files.
                dimensions.extend(['wavelength', np.shape(dataset0['w'])[1]])
                # Developer's note: Several other variables such as aerosolcols could be organized into a boolean array to have the wavelength dimension.                
            ngkey = []
            if subsets['variables']: 
                ngkey = [key for key in subsets['variables'] if key not in dataset0.keys()]
            for key in dataset0.keys():
                if key[0]!='_':
                    newsize = 1-np.in1d(dataset0[key].squeeze().shape, dimensions[1::2])
                    if np.any(newsize):
                        if dataset0[key].squeeze().ndim==1:
                            dimensions.extend([key, dataset0[key].squeeze().shape[0]])
                        else:
                            ngkey.append(key)
            if ngkey:
                warn('Excluded are ' + ''.join([key + ', ' for key in ngkey])[:-2] + '.') 
            [dataset.createDimension(key, int(val)) for key, val in np.array(dimensions).reshape(-1,2)]
            # store the time variable
            var = dataset.createVariable('time', 'f8', ('time',), zlib=True)
            var[:] = dataset0['time'][:]
            var.units = 'seconds since 1970-01-01 00:00:00.0'
            # store the variables - this may take long
            for key in dataset0:
                if key[0]!='_' and key not in ngkey and key!='time':
                    var = dataset.createVariable(key, 'f8', 
                                                 [keyi for keyi, val in np.array(dimensions).reshape(-1,2) for size in dataset0[key].squeeze().shape if int(val)==size],
                                                 zlib=True)
                    try:
                        var[:] = ma.array(dataset0[key][:], mask=1-np.isfinite(dataset0[key][:]))
                    except:
                        warn(key + ' not copied.')
        except OSError:
            if 'dataset0' in locals() and dataset0.isopen():
                dataset0.close()
    else:
        raise NotImplementedError('_readmat for multiple input files.')
    # note history and source
    _setglobalattributes(dataset, fnames)

def _readiwg1(fnames, dataset, **subsets):   
    """Reads IWG1 files whose format is described in a single xml file.
    """
    
    # read the xml file
    datatype = 'f8' # !!! study the following: # datatype = 'i4' if lsd == 0 else 'f4' if lsd < 7 else 'f8' 
    fill_value = '9.969209968386869e+36' # NetCDF4 default fill value for f8
    names=['time']
    dataset.createDimension('time', 0)
    var = dataset.createVariable('time', datatype, ('time',), 
                           zlib=True, least_significant_digit=3) # milliseconds given in ORACLES IWG1 files
    var.units = 'seconds since 1970-01-01 00:00:00.0'

    tree = ET.parse([fname for fname in fnames if fname.lower().endswith('.xml')][0])
    root = tree.getroot()
    for child in root:
        if len(child)==0 and child.text: # assume a header
            dataset.setncattr(child.tag[child.tag.find('}')+1:], child.text)
        if child.tag[child.tag.find('}')+1:]=='parameter':
            fmt=''
            long_name = ''
            for gc in child:
                if gc.tag[gc.tag.find('}')+1:]=='format':
                    fmt = gc.text
                elif gc.tag[gc.tag.find('}')+1:]=='info':
                    long_name = gc.text
            datatype, least_significant_digit=('f8', int(fmt[fmt.find('.')+1:-1])) if fmt.endswith('f') else ('S1', None)
            names.append(child.attrib['id'] if 'id' in child.attrib.keys() else child.attrib['{http://www.w3.org/XML/1998/namespace}id'] if '{http://www.w3.org/XML/1998/namespace}id' in child.attrib.keys() else '') 
            var = dataset.createVariable(names[-1], datatype, ('time',),
                                        zlib=True, least_significant_digit=least_significant_digit)
            if long_name:
                var.long_name = long_name
    if len(fnames)==2: # only one data file in addition to the xml
        if subsets.keys():
            raise NotImplementedError('subsets for _readiwg1.')
        with open([fname for fname in fnames if not fname.lower().endswith('.xml')][0], newline='') as f:
            # read the file
            arrays = [[datetime.timestamp(datetime.strptime(row[1]+' +0000', '%Y-%m-%dT%H:%M:%S.%f %z'))] + [element if element else fill_value for element in row[1:]] for row in csv.reader(f)]
            arrays = ma.array(arrays, mask=arrays==fill_value)
            # store the time variable
            for n, array in enumerate(zip(*arrays)):
                var = dataset[names[n]]
                var[:] = array # convert a list to a numpy array only once for each variable; this seems faster than row-by-row conversion, though the latter method may use less memory.
#                 if fill_value in array:
#                     var.missing_value = fill_value
    else:
        raise NotImplementedError('_readiwg1 for multiple input files.')
    # note history and source
    _setglobalattributes(dataset, fnames)

def _setglobalattributes(dataset, fnames):
    """Sets global attributes to the dataset, in formats consistent with conventions (NASA, CF, DOE ARM) where possible. 
    """
    
    if isinstance(fnames, str):
        fnames = (fnames,)        
    if 'history' not in dataset.ncattrs():
        dataset.history = ''
    else:
        dataset.history = dataset.history + '\n'
    if 'source' not in dataset.ncattrs():
        dataset.source = ''
    else:
        dataset.source = dataset.source + '\n'
    
    # Developer's note: sys._getframe(), used below, works even when super, a Python built-in, is used, unlike inspect.stack(). It may also be faster, perhaps by milliseconds. 
    dataset.history = dataset.history + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' Assembled using ' + inspect.getframeinfo(sys._getframe(1))[2] + ' and ' + inspect.getframeinfo(sys._getframe(2))[2]
    dataset.source = dataset.source + ''.join([fname + '\n' for fname in fnames]) 
    dataset.source = dataset.source[:-1]
    
def smooth(x, xp, fp, nadj=-1):
    """smoothes data.
    
    x : 2-D sequence of floats with exactly two columns or scalar
    The x-coordinates of the smoothed values (if 2-D) or the length of box filtering (if scalar).
    xp : 2-D sequence of floats with exactly two columns
    The x-coordinates of the data points, with the columns corresponding to the start and end points the data span. No two spans must overlap. 
    fp : sequence of floats, whose zeroth dimension is as long as xp's.
    The y-coordinates of the data points.
    nadj : scalar.
    The adjustment added to the weighted number of samples before it is used as the denominator. None if standard deviation is not asked for. 
    """    
    
# sort input variables

    # nadj
    # if it is 0, compute standard deviation with n as the denominator 
    if nadj == 0:
        pass
    # if it is None, np.nan etc., do not compute standard deviation
    elif not nadj:
        nadj = np.nan

    # x
    # make sure that x is an array, not a list
    x = ma.array(x)
    # if a scalar is given, assume the value represents the span over which average is computed 
    if ma.ndim(x) == 0: 
        x = xp + ma.array([-1., 1.]) / 2 * x
    # x must be a matrix with exactly two columns
    elif x.ndim != 2 or ma.shape(x)[1] != 2:
        raise ValueError('x must be a matrix with exactly two columns.')  

    # xp and fp
    # make sure that they are each an array, not a list
    xp = ma.array(xp)
    fp = ma.array(fp) if len(ma.shape(fp))>1 else ma.array(fp)[:,np.newaxis] # note this is different from np.atleast_2d in the order of axes
    # remove invalid xp rows
    xpinvalid = (np.any(np.isnan(xp), axis=1)) | (np.any(ma.getmaskarray(xp), axis=1)) | (xp[:,0]>=max(x[:,1])) | (xp[:,1]<=min(x[:,0]))
    xp1 = xp[~xpinvalid]
    fp1 = fp[~xpinvalid]
    fp1.mask = ma.getmaskarray(fp1)
    fp1.mask[np.isnan(fp1)] = True # added 2017-04-18. ma.masked_invalid would mask inf too, limiting intentional uses of inf 
    # sort them by xp
    xpindex = ma.argsort(xp1[:,0])
    xp1 = xp1[xpindex]
    fp1 = fp1[xpindex]
    # refuse any double-counting
    if np.any(xp1[:,0] > xp1[:,1]):
        raise ValueError('xp must specify the start and end points of data segments.')   
    # determine whether the fast track can be taken
    # !!! to-do: The slow mode is really slow. So the choice here should not be either-or, but a mix of both. Isolate rows of x that are clearly away from overlapping parts of xp.
    if np.any(xp1[1:,0] < xp1[:-1, 1]):
        warn('xp overlaps. Entering the slow smooth mode.')
        results = _smoothslow(x, xp, fp, nadj)
    else:
        results = _smoothfast(x, xp1, fp1, nadj) 
    return results # average, sum_of_weights, number_of_elements and, if nadj is not None, standard_deviation

def _smoothslow(x, xp, fp, nadj):
    """smooth data slowly but surely."""
    
    average = ma.empty((ma.shape(x)[0], ma.shape(fp)[1])) 
    average.mask=True # mask them all as default
    sum_of_weights = np.zeros_like(average)
    number_of_elements = np.zeros_like(average)
    if not np.isnan(nadj):
        standard_deviation = np.zeros_like(average)
    for n, xx in enumerate(x):
        index = (xp[:,1] > xx[0]) & (xp[:,0] < xx[1])
        deltaxx = xx[1] - xx[0]
        deltaxp = xp[index,1] - xp[index,0]
        deltacenters = np.mean(xp[index],axis=1) - np.mean(xx)
        weight = (deltaxx + deltaxp - 2 * np.abs(deltacenters)) / 2 / deltaxp
        weight[weight > 1] = 1.
        sum_of_weights[n] = ma.sum(weight[:,np.newaxis] * (1-fp[index].mask),axis=0)
        average[n] = ma.sum(weight[:,np.newaxis] * fp[index],axis=0) / sum_of_weights[n]
        number_of_elements[n] = np.sum(1-fp[index].mask,axis=0)
        if not np.isnan(nadj):
            sum_of_thesquared = ma.sum(weight[:,np.newaxis] * np.square(fp[index]),axis=0)
            sum_of_weightssquared = ma.sum(np.square(weight))
            standard_deviation[n] = np.sqrt((sum_of_thesquared - sum_of_weights[n] * np.square(average[n])) * sum_of_weights[n] / (np.square(sum_of_weights[n]) + nadj * sum_of_weightssquared))
    if np.isnan(nadj):
        return average, sum_of_weights, number_of_elements
    else:
        return average, sum_of_weights, number_of_elements, standard_deviation

def _smoothfast(x, xp1, fp1, nadj):
    """smooth fast, using cumulative sum."""

    # start the processing unless xp1 is empty
    # Note that the initialization of the output variables are delayed until later, for the efficient use of memory
    if np.any(xp1):

    # sort input variables further
        # remove duplicates and invalid rows for faster computation
        xinvalid = (np.any(np.isnan(x), axis=1)) | (np.any(ma.getmaskarray(x), axis=1)) | (x[:,0]>=xp1[ma.flatnotmasked_edges(xp1[:,1])[1],1]) | (x[:,1]<=xp1[0,0])
        x1 = x[~xinvalid]
        b = np.ascontiguousarray(x1).view(np.dtype((np.void, x1.dtype.itemsize * x1.shape[1])))
        _, xindex, xindexinverse = ma.unique(b, return_index=True, return_inverse=True)
        x1 = x1[xindex]

        # transpose, for easier computation
        x1 = x1.transpose()

    # determine index and weight

        # Developer's notes: 
        # The index for matching the time stamps xp1 to the reference x1 is determined through interpolation followed by adjustments. 
        # The adjustments, +1 and -1 on index1, are necessary for the special cases where the two time stamps overlap exactly. 
        # In the interpolation, the left and right values with -0.5 prevent the adjustments for the special cases from overshooting.
        # For other cases, the effects of the boundary values are cancelled when ceil and floor are taken.
        index1i = ma.array([np.interp(x1[0], xp1[:,1], range(ma.shape(xp1)[0]), left=-0.5),
         np.interp(x1[1], xp1[:,0], range(ma.shape(xp1)[0]), right=ma.shape(xp1)[0]-0.5)])
        index1 = ma.array([ma.ceil(index1i[0]), ma.floor(index1i[1])]).astype(int)
        index1sa = index1i - index1
        # zero difference (index1sa==0) means that the xp1 is just outside the x1. Do not count such xp1 cases. This is not an intuitive operation when dxp1 is zero.
        index1[0,index1sa[0]==0] = index1[0,index1sa[0]==0] + 1
        index1[1,index1sa[1]==0] = index1[1,index1sa[1]==0] - 1
        index11 = [xp1[index1[0],0]>x1[0], xp1[index1[1],1]<x1[1]]    
        mx1 = ma.mean(x1,axis=0)
        mxp1 = ma.mean(xp1,axis=1)
        dx1 = x1[1]-x1[0]
        dxp1 = xp1[:,1]-xp1[:,0]
        weight1 = (dx1[np.newaxis, :] + dxp1[index1] - 2 * abs(mx1[np.newaxis, :] - mxp1[index1])) / 2 / dxp1[index1]
        weight1[ma.where(index11)] = 1.
        weight1[dxp1[index1]==0] = 1.
    # The code below selects a calculation method based on the number of data entries. For the ranges of x which exactly two data points enter, the calculation accounts for the initial and final entries. For the ranges of x which three or more data points enter, the calculation accounts for the initial and final entries first and those between them second. For the ranges of x which only one data point enters, the single data points are directly treated. The order - two entries, more entrties and single entries - allows efficient use of intermediary matrices: sum1 as well as sum_of_thesquared1 and sum_of_weightssquared1 count the multiple entries, while average1, to which sum1 is converted, better houses the single entries.

    # account for the initial and final entries

    # Address the characteristics unique to the initial and final entries: weights that are not generally unity.
        rows2 = (index1[1]-index1[0] > 0).nonzero()[0]
        weight2 = weight1[:,rows2]
        index2 = index1[:,rows2]
        fp2 = fp1[index2]
        sum2 = ma.sum(weight2[:,:,np.newaxis] * fp2,axis=0)
        number_of_elements2 = np.sum(1-fp2.mask,axis=0)
        sum_of_weights2 = ma.sum(weight2[:,:,np.newaxis] * (1-fp2.mask),axis=0)
        if not np.isnan(nadj):
            sum_of_thesquared2 = ma.sum(weight2[:,:,np.newaxis] * np.square(fp2),axis=0)
            sum_of_weightssquared2 = ma.sum(np.square(weight2)[:,:,np.newaxis] * (1-fp2.mask),axis=0)

    # account for entries between them

    # The ranges of x can include varying numbers of entries. Summing them through a for-loop can be slow. Instead, this section uses cumulative sum. This strategy, which relies on the fact that the index of the entiries is consecutive, allows the summation to be defined by exactly two items: the initial and final entries. The sum of the entries between intial and final ones is the cumsum up to the final entry minus the cumsum up to the initial. 

        rows3 = (index1[1]-index1[0] > 1).nonzero()[0]
        if np.any(rows3):
            # compute the additions
            index3 = index1[:,rows3]
            fp3 = fp1[np.min(index3):np.max(index3)]
            # determine offset to remove, to forestall (unsubstantiated) precision problems
            offset = ma.mean(fp3,axis=0)
            fp3 = fp3 - offset
            index3 = index3 - np.min(index3) # index of fp3 
            csiffp3 = ma.cumsum(np.isfinite(fp3),axis=0)
            csiffp3.mask = False # This unmasks the cases with no valid data, but they are masked again later upon division by zero (the weight)
            csfp3 = ma.cumsum(fp3,axis=0)
            csfp3.mask = False
            number_of_elements3 = csiffp3[index3[1]-1] - csiffp3[index3[0]]
            sum3e = csfp3[index3[1]-1] - csfp3[index3[0]]
            sum3 = sum3e + number_of_elements3 * offset
            sum3.mask = ma.getmaskarray(sum3)
            sum3.mask[number_of_elements3==0] = True # this line makes a difference when ma.sum is taken with sum2[rows23]
            # add to the intermediary variables
            rows23 = np.searchsorted(rows2,rows3)
            sum2[rows23] = ma.sum((sum2[rows23], sum3), axis=0) # used to be: sum2[rows23] + sum3 but this returns masked elements when the first term is masked even if the second term is not.
            number_of_elements2[rows23] = number_of_elements2[rows23] + number_of_elements3
            sum_of_weights2[rows23] = sum_of_weights2[rows23] + number_of_elements3
            if not np.isnan(nadj):
                # compute the additions
                cssqfp3 = ma.cumsum(np.square(fp3),axis=0)
                cssqfp3.mask = False
                sum_of_thesquared3e = cssqfp3[index3[1]-1] - cssqfp3[index3[0]]
                sum_of_thesquared3 = sum_of_thesquared3e + 2 * sum3e * offset + number_of_elements3 * np.square(offset) 
                # add to the intermediary variables
                sum_of_thesquared2[rows23] = sum_of_thesquared2[rows23] + sum_of_thesquared3
                sum_of_weightssquared2[rows23] = sum_of_weightssquared2[rows23] + number_of_elements3

    # compute average and standard deviation

        average2 = sum2 / sum_of_weights2
        if not np.isnan(nadj):
            standard_deviation2 = np.sqrt((sum_of_thesquared2-sum_of_weights2*np.square(average2)) 
                                            * sum_of_weights2 
                                            / (np.square(sum_of_weights2) + nadj * sum_of_weightssquared2))

    # prepare to integrate with the cases with single entries
        average1 = ma.empty((ma.shape(xindex)[0], ma.shape(fp1)[1]))
        average1.mask=True # mask them all as default
        number_of_elements1 = ma.empty_like(average1)
        sum_of_weights1 = ma.empty_like(average1)
        if not np.isnan(nadj):
            standard_deviation1 = ma.empty_like(average1)

        average1[rows2] = average2
        number_of_elements1[rows2] = number_of_elements2
        sum_of_weights1[rows2] = sum_of_weights2
        if not np.isnan(nadj):
            standard_deviation1[rows2] = standard_deviation2

    # treat cases with single entries    
        rows1 = (index1[1]-index1[0] == 0).nonzero()[0]
        average1[rows1] = fp1[index1[0,rows1]]
        number_of_elements1[rows1] = 1-fp1.mask[index1[0,rows1]]
        sum_of_weights1[rows1] = 1-fp1.mask[index1[0,rows1]] * weight1[0,rows1,np.newaxis]
        if not np.isnan(nadj):
            standard_deviation1[rows1] = np.nan

    # This is the end the processing for the cases where xp1 is not empty

# initialize output variables, even if xp1 is empty

    average = ma.empty((ma.shape(x)[0], ma.shape(fp1)[1]))
    average.mask=True # mask them all as default
    sum_of_weights = np.zeros_like(average)
    number_of_elements = np.zeros_like(average)
    if not np.isnan(nadj):
        standard_deviation = np.zeros_like(average)

# fill output variables
    if np.any(xp1):
        average[~xinvalid] = average1[xindexinverse]
        sum_of_weights[~xinvalid] = sum_of_weights1[xindexinverse]
        number_of_elements[~xinvalid] = number_of_elements1[xindexinverse]
        if not np.isnan(nadj):
            standard_deviation[~xinvalid] = standard_deviation1[xindexinverse] 

# return output variables, even if xp1 is empty

    if np.isnan(nadj):
        return average, sum_of_weights, number_of_elements
    else:
        return average, sum_of_weights, number_of_elements, standard_deviation
    
def index(dataset, **subsets):
    """Prepare boolean index arrays for assignment and referencing.
    
    The output arrays are given for the variables specified by the keyward argument variables and for their underlying dimensions.
    If variables are not specified, all variables in the dataset are selected.
    The input array dataset must be either a dataset or group in the NetCDF4 format.
    The output arrays for variables and dimensions are almost always redundant. That is, the output arrays for dimensions can be 
    combined to make the other output, variables. An exception to this principle can arise when any of the input subsets is 
    given in a multi-dimensional array that shares two or more dimensions with at least one of the variables.
    """
    
    # forestall confusion arising from the unexpected uses of a keyword
    if 'variables' in dataset.variables.keys():
        raise ValueError('dataset has a variable called variables. Remove it.')
    if 'variables' in dataset.dimensions.keys():
        raise ValueError('dataset has a dimension called variables. Remove it.')
    
    # restrict the access to a group within the dataset, unless all keys of subsets belong to a single group
#     for key, val in subsets.items():
#         if '/' in key:
#             raise ValueError('Access the single dataset or group given as the input argument dataset.')
    
#     group = []
#     dimensions = []
#     for key, val in subsets.items():
#         if key=='variables':
#             group.extend(['/' if v in dataset.variables.keys() or v in dataset.dimensions.keys() 
#                           else dataset[v].group().name 
#                           for v in val])
#         else:
#             try: # assume that a variable is given
#                 group.extend(['/' if key in dataset.variables.keys() or key in dataset.dimensions.keys() 
#                               else dataset[key].group().name])
#             except IndexError: # a dimension is given
#                 if key.rfind('/')==-1 and key not in dataset.dimensions.keys():
#                     raise IndexError(key + ' not among the dimensions.')
#                 else:
#                     dimensions.append((key, dataset[key[:key.rfind('/')]].dimensions[key[key.rfind('/')+1:]].name))
#                     group.append(key[:key.rfind('/')].strip('/'))              
#     if len(set(group))!=1:
#         raise IndexError('Access a single dataset or group.')
#     elif group[0]!='/':
#         dataset = dataset[group[0]]        
#     # let the keys refer to the dimension, instead of the combination of group and dimension
#     for dim0, dim in dimensions:
#         subsets[dim] = subsets.pop(dim0)
            
    # select the variables for which an indexing array is to be generated
    if 'variables' not in subsets.keys():
        subsets['variables'] = dataset.variables.keys()
       
    # Get their dimensions
    # Developer's notes: 
    # The business with '/' accommodates references to a group under dataset, the NetCDF4 root group.
    # This business is complicated by the fact that a variable can be accessed as dataset['/a_group/a_variable'] 
    # whereas a dimention cannot be accessed as dataset.dimensions['/a_group/a_dimension'].
    # Another consequence of the possibility of a group variable is that a variable is not necessarily in dataset.variables.keys(). 
    dimensionsofinterest = [(dataset[v].group().name if '/' in v else '/', dataset[v].dimensions) for v in subsets['variables']]
    dimensioncomponentsofinterest = [(group, (dimension,)) for group, dimensions in set(dimensionsofinterest) for dimension in dimensions]
    dimensionsofinterest = [dimension for dimension in set(dimensionsofinterest + [dimension for dimension in dimensioncomponentsofinterest])]
#     dimensionsofinterest = [dataset[v].dimensions for v in subsets['variables']]
#     dimensioncomponentsofinterest = [(dimension,) for dimensions in set(dimensionsofinterest) for dimension in dimensions]
#     dimensionsofinterest = [dimension for dimension in set(dimensionsofinterest + [dimension for dimension in dimensioncomponentsofinterest])]
    # Initiate the indexing arrays
    # All elements are marked True at this point. Some of them are converted to False later (look for "ias[indexofinterest] &")
    ias = np.array([np.ones([dataset.dimensions[dimensionofinterest].size if group=='/' else dataset[group].dimensions[dimensionofinterest].size 
            for dimensionofinterest in dois], dtype=np.bool)
           for group, dois in dimensionsofinterest])
#     ias = np.array([np.ones([dataset.dimensions[dimensionofinterest].size for dimensionofinterest in dois], dtype=np.bool) for dois in dimensionsofinterest])
    
    # account for each user input and mark the indexing arrays accordingly 
    for key, val in subsets.items():
        # determine if the given subset key refers to a variable or dimension
        # The possibility of a group variable means that a variable is not necessarily in dataset.variables.keys(). Use try.
        try: # assume it's a variable
            group = dataset[key].group().name if '/' in key else '/'
            dimensions = dataset.variables[key].dimensions
#             dimensions = list(dataset.variables[key].dimensions)
            variable = dataset[key][:]
        except:
            # assume that it's a dimension and that it's a dimension of interest.
            key = key.strip('/') # keep the '/' between groups only 
            group = key[:key.rfind('/')] if '/' in key else '/'
            dimensions = (key[key.rfind('/')+1:],)
#             dimensions = [key] 
            variable = []
#             if dimensions[0] not in set(dimensionsofinterest): 
#                 # ignore this set of user input
#                 dimensions = ()
        # check if the given subset is relevant to the variables of interest (that is, check if the user gave variables and subsets in an internally consistent manner.)
        indicesofinterest = [i for i, (grp, dois) in enumerate(dimensionsofinterest) if dimensions and all([dimension in dois for dimension in dimensions]) and grp==group]
#         indicesofinterest = [i for i, dois in enumerate(dimensionsofinterest) if dimensions and all([dimension in dois for dimension in dimensions])]
        if indicesofinterest:
            # represent the given subset in an indexing array
            ia2 = np.zeros([dataset.dimensions[dimension].size if group is '/' else dataset[group].dimensions[dimension].size
                            for dimension in dimensions], dtype=np.bool)
#             ia2 = np.zeros([dataset.dimensions[dimension].size for dimension in dimensions], dtype=np.bool)
            if np.any(variable) and np.array(val).ndim==2 and np.shape(np.array(val))[1]==2:
                if ia2.ndim==2 and np.shape(ia2)[1]==2:
                    warn('Be careful in selecting a subset in terms of the two-column variable ' + key + '.')
                # bounds are given; reduce them to a boolean array                
                for bounds in val:
                    ia2[np.squeeze((variable>=bounds[0]) & (variable<bounds[1]))] = True
            else:
                ia2[val] = True
            for indexofinterest in indicesofinterest:
                obj3=[]
                ooa=[]
                for dimensionofinterest in dimensionsofinterest[indexofinterest][1]:
                    # determine in what order of dois dimensions are found. (dois can be greater than, or same size of, dimensions, not smaller.)
                    if dimensionofinterest in dimensions:
                        ooa.append(dimensions.index(dimensionofinterest))
                        obj3.append(slice(None))  
                    else:
                        obj3.append(np.newaxis)
                ia3 = np.transpose(ia2, ooa)
                ias[indexofinterest] &= ia3[obj3] # Yohei, 2017-03-01; was: ias[indexofinterest] = ias[indexofinterest] & ia3[obj3]
                    
    # assign index arrays to the variables of interest    
    indices = [dimensionsofinterest.index((dataset[key].group().name if '/' in key else '/', dataset[key].dimensions)) for key in subsets['variables']]
#     indices = [dimensionsofinterest.index(dataset[var].dimensions) for var in subsets['variables']]
    variables = dict(zip(subsets['variables'], ias[indices]))
    # give the new size of the dimensions
    dimensions = dict([(d[0], ias[i]) for i, (_,d) in enumerate(dimensionsofinterest) if len(d)==1])
#     dimensions = dict([(d[0], ias[i]) for i, d in enumerate(dimensionsofinterest) if len(d)==1])
    
    return variables, dimensions
