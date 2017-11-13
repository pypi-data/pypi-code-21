"""
Tools to prepare data for an fvcom run.

A very gradual port of the most used functions from the matlab toolbox https://github.com/pwcazenave/fvcom-toolbox/tree/master/fvcom_prepro/
"""

import numpy as np
import os
import netCDF4 as nc
import multiprocessing as mp
import datetime as dt
from scipy.interpolate import griddata
from functools import partial

from PyFVCOM.grid import read_fvcom_mesh
from PyFVCOM.coordinate import UTM_to_LL


def interp_sst_assimilation(sst_dir, run_year, output_file, fvcom_grd_file_or_latlon_list, utm_zone=None, serial=False, pool_size=None):
    """
    Interpolate SST data from remote sensing data onto the supplied model
    grid.

    Parameters
    ----------

    sst_dir : str
        Path to directory containing the SST data
    run_year : int
        Tear for which to generate SST data
    output_file : str
         Path for output netCDF file
    fvcom_grd_file_or_latlon_list - str, or Nx2 list/array
         Either the path of the fvcom.grd file or a python Nx2 list/array of node lat/lons to interpolate onto
    utm_zone : str, required only when using .grd file
        The utm zone to convert the UTM coordinates in the grid file to lat/lon
    serial : bool, optional
        Run in serial rather than parallel
    pool_size - Optional, specifiy number of processes for parallel run. By default it uses all available (mp.cpu_count())


    Returns 
    -------

    FVCOM data assimilation SST netCDF file (path specified by output_file)
    date_list : list
        List of python datetimes for sst data

    sst_interp_list : list
        List of interpolated temperatures. One list entry for each data, each entry is an array len(nodes)


    Example
    -------
    sst_dir = '/gpfs1/users/modellers/mbe/Data/SST_data/2006/'
    grd_filestr = '/gpfs1/users/modellers/mbe/Models/FVCOM/tamar/input/tamar_v2/common/tamar_v2_grd.dat'
    date_list, sst_list = pf.preproc.interp_sst_assimilation(sst_dir, 2006, 'output_file.nc', grd_filestr, utm_zone='30U', serial=False, pool_size=20)


    To Do
    -----

    Unlike the matlab toolbox function it doesn't automatically include the last day of the previous year and first day of the next. Instead I have copied the relevant files into the year directory. This should probably be implemented to happen automatically assuming a directory structure based on year folders.

    Sort PEP8 line lengths

    Based on https://github.com/pwcazenave/fvcom-toolbox/tree/master/fvcom_prepro/interp_sst_assimilation.m, authors Ricardo Torres (Plymouth Marine Laboratory), Pierre Cazenave (Plymouth Marine Laboratory)
    
    """
    # SST files
    sst_files = os.listdir(sst_dir)

    # Add last day from previous year and first day of following year

    # Read SST data files and interpolate each to the FVCOM mesh
    sst_nc = nc.Dataset(sst_dir + sst_files[0], 'r')
    sst_meshgrid = np.meshgrid(sst_nc.variables['lon'][:], sst_nc.variables['lat'][:])

    if isinstance(fvcom_grd_file_or_latlon_list, str) and utm_zone:
        triangle, nodes, X, Y, Z = read_fvcom_mesh(fvcom_grd_file_or_latlon_list)
        fvcom_ll = np.asarray(UTM_to_LL(23, Y,X, '30U')).T

    else:
        try:
            assert fvcom_grd_file_or_latlon_list.shape[1] == 2
            fvcom_ll = np.asarray(fvcom_grd_file_or_latlon_list)

        except:
            print('Require either an fvcom .grd file and its associated utm_zone, or a Nx2 array of fvcom model lon lat points')
            return
    if serial:    
        interped_data = []
        for this_file in sst_files:
            interped_data.append(_inter_sst_worker(sst_dir, fvcom_ll, this_file))

    else:
        if pool_size == None:
            pool = mp.pool(mp.cpu_count())
        else:
            pool = mp.Pool(pool_size)
        part_func = partial(_inter_sst_worker, sst_dir, fvcom_ll)
        interped_data = pool.map(part_func, sst_files)
        pool.close()

    # sort data and prepare date lists
    interped_data = sorted(interped_data)
    date_list = []
    sst_interp_list = []
    for this_record in interped_data:
        date_list.append(this_record[0])
        sst_interp_list.append(this_record[1])
    
    ref_date = dt.datetime(1858, 11, 17, 0, 0)
    date_list_str = []
    date_list_float = []
    for this_date in date_list:
        date_list_float.append((this_date -ref_date).days + 0.5) # FVCOM expects midday values

    # Write to nc file
    sst_out_nc = nc.Dataset(output_file, 'w', format='NETCDF3_64BIT')

    sst_out_nc.year = run_year
    sst_out_nc.title = 'FVCOM SST 1km merged product File'
    sst_out_nc.institution = 'Plymouth Marine Laboratory'
    sst_out_nc.source = 'FVCOM grid (unstructured) surface forcing'
    sst_out_nc.history = 'File created using PyFVCOM'
    sst_out_nc.references = 'http://fvcom.smast.umassd.edu, http://codfish.smast.umassd.edu'
    sst_out_nc.Conventions = 'CF-1.0'
    sst_out_nc.CoordinateProjection = 'init=WGS84'

    # add dimensions
    sst_out_nc.createDimension('time', len(date_list))
    sst_out_nc.createDimension('node', len(fvcom_ll))
    sst_out_nc.createDimension('three', 3)
    date_str_len = 26
    sst_out_nc.createDimension('DateStrLen', date_str_len)
    
    # add space variables
    sst_lon = sst_out_nc.createVariable('lon', 'f4', ('node',))
    sst_lon.long_name = 'nodal longitude'
    sst_lon.units = 'degrees_east'
    sst_lon[:] = fvcom_ll[:,0]

    sst_lat = sst_out_nc.createVariable('lat', 'f4', ('node',))
    sst_lat.long_name = 'nodal latitude'
    sst_lat.units = 'degrees_north'
    sst_lat[:] = fvcom_ll[:,1]

    # add time variables
    sst_time = sst_out_nc.createVariable('time', 'f4', ('time',))
    sst_Times = sst_out_nc.createVariable('Times', 'c', ('time', 'DateStrLen'))

    sst_time.long_name = 'time'
    sst_time.units = 'days since 1858-11-17 00:00:00'
    sst_time.delta_t = '0000-00-00 01:00:00'
    sst_time.format = 'modified julian day (MJD)'
    sst_time.time_zone = 'UTC'

    sst_Times.long_name = 'Calendar Date'
    sst_Times.format = 'String: Calendar Time'
    sst_Times.time_zone = 'UTC'

    sst_time[:] = date_list_float

    date_str_var_type = 'S'+str(date_str_len)
    Times = np.empty([len(date_list)]).astype(date_str_var_type)

    for i in range(0, len(date_list)):
        Times[i] = date_list[i].strftime('%Y-%m-%d %H:%M:%S')

    Times_chars = nc.stringtochar(Times)
    sst_Times[:] = Times_chars

    # add sst
    sst = sst_out_nc.createVariable('sst', 'f4', ('node', 'time'))
    
    sst.long_name = 'sea surface Temperature'
    sst.units = 'Celsius Degree'
    sst.grid = 'fvcom_grid'
    sst.type = 'data'

    sst[:] = sst_interp_list

    # close netcdf
    sst_out_nc.close()

    return date_list, sst_interp_list 

# functionised version of sst interpolation for multiprocessing
def _inter_sst_worker(sst_dir, fvcom_ll, this_file):
    this_file_nc = nc.Dataset(sst_dir + this_file, 'r')
    
    sst_eo = this_file_nc.variables['analysed_sst'][:] - 273.15
    sst_eo = sst_eo.flatten()
    flat_mask = sst_eo.mask
    sst_eo = sst_eo[~flat_mask]
    sst_eo = np.ma.filled(sst_eo, np.NAN)

    sst_lon = this_file_nc.variables['lon'][:]
    sst_lat = this_file_nc.variables['lat'][:]

    sst_meshgrid = np.asarray(np.meshgrid(sst_lon, sst_lat))
    sst_grid_flat = np.asarray([sst_meshgrid[1,:,:].flatten(), sst_meshgrid[0,:,:].flatten()]).T
    sst_grid_flat = sst_grid_flat[~flat_mask]
    
    interp_sst = griddata(sst_grid_flat, sst_eo, fvcom_ll)

    time_eo = this_file_nc.variables['time'][:]
    time_eo_units = this_file_nc.variables['time'].units

    time_str = time_eo_units.split(' ')[2] + ' ' + time_eo_units.split(' ')[3]
    this_basetime = dt.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    time_out_dt = this_basetime + dt.timedelta(seconds = int(time_eo[0]))

    return (time_out_dt, interp_sst)

