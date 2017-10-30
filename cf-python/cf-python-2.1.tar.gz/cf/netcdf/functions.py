from os.path import isfile

from netCDF4 import Dataset as netCDF4_Dataset

from ..constants import _file_to_fh
from ..functions import open_files_threshold_exceeded, close_one_file

#if 'netCDF' not in _file_to_fh:
#    _file_to_fh['netCDF'] = {}

_file_to_Dataset = _file_to_fh.setdefault('netCDF', {})

def _open_netcdf_file(filename, mode, fmt='NETCDF4'):
    '''

Open a netCDF file and read it into a netCDF4.Dataset object.

If the file is already open then the existing netCDF4.Dataset object
will be returned.

:Parameters:

    filename : str
        The netCDF file to be opened.

:Returns:

    out : netCDF4.Dataset
         A netCDF4.Dataset instance for the netCDF file.

:Examples:

>>> nc1 = _open_netcdf_file('file.nc')
>>> nc1
<netCDF4.Dataset at 0x1a7dad0>
>>> nc2 = _open_netcdf_file('file.nc')
>>> nc2 is nc1
True

'''
    if filename in _file_to_Dataset and mode == 'r':
        # File is already open
        return _file_to_Dataset[filename]
    elif open_files_threshold_exceeded():
        # Close a random data file to make way for this one
        close_one_file()

    if mode in ('a', 'r+'):
        if not isfile(filename):
            nc = netCDF4_Dataset(filename, 'w', format=fmt) 
            nc.close()
        elif filename in _file_to_Dataset:
            _close_netcdf_file(filename)

    try:        
        nc = netCDF4_Dataset(filename, mode, format=fmt)
    except RuntimeError as runtime_error:
        raise RuntimeError("{0}: {1}".format(runtime_error, filename))

    if mode == 'r':
        # Update the _file_to_Dataset dictionary
        _file_to_Dataset[filename] = nc

    return nc
#--- End: def

def _close_netcdf_file(filename):
    '''

Close a netCDF file

does nothing if the file is already closed.

:Parameters:

    filename : str
        The netCDF file to be closed.

:Returns:

    None

:Examples:

'''
    nc = _file_to_Dataset.pop(filename, None)
    if nc is not None:
        nc.close()
#--- End: def
