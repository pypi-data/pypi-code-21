"""
Input and output functions for lagranto
"""
# coding: utf8
import gzip
from datetime import datetime, timedelta

import netCDF4
import numpy as np
from functools import partial

__all__ = ['from_netcdf', 'to_ascii', 'from_ascii']


def from_netcdf(filename, usedatetime=True, msv=-999, unit='hours',
                exclude=None, date=None):
    """ Load trajectories from a netcdf


        Parameters
        ----------

        filename : string,
            path to a netcdf file containing trajectories
        usedatetime : bool, default True
                If True then return time as datetime object
        msv : float, default -999
                Define the missing value
        unit : string, default hours
                Define the units of the times (hours, seconds or hhmm)
        exclude: list of string, default empty
                Define a list of variables to exclude from reading
        date: datetime or list
                Can be used to select particular dates, for example
                to read in a single timestep
    """
    if exclude is None:
        exclude = []
    try:
        with netCDF4.Dataset(filename) as ncfile:

            exclude.append('BASEDATE')
            variables = [var for var in ncfile.variables if var not in exclude]

            formats = [ncfile.variables[var].dtype for var in variables]

            if usedatetime:
                formats[variables.index('time')] = 'datetime64[s]'

            ntra, ntime = _get_netcdf_traj_dim(ncfile)

            if usedatetime:
                dates = _netcdf_time_to_datetime(ncfile, unit=unit)
            else:
                dates = ncfile['time'][:]

            index = slice(None)
            if date is not None:
                if type(date) not in [list, tuple]:
                    date = [date]
                ntime = len(date)
                d_index = np.hstack([np.where(dates == d)[0] for d in date])
                if d_index.size == 0:
                    sdate = [str(d) for d in date]
                    sdates = [str(d) for d in dates]
                    msg = '{} not found in time'.format(','.join(sdate))
                    raise RuntimeError(msg)
                index = [np.sort(d_index), slice(None)]
                dates = dates[d_index]

            array = np.zeros((ntra, ntime), dtype={'names': variables,
                                                   'formats': formats})

            array['time'] = repeat_time(dates, ntra)

            for var in variables:
                if var == 'time':
                    continue
                vardata = ncfile.variables[var][index].T
                vardata[vardata <= msv] = np.nan

                # Check need for netcdf trajectories produced by LAGRANTO
                # which make use of a old fortran library to write netcdf.
                # This library add two dummies dimensions.
                if vardata.ndim > 2:
                    array[var] = vardata.squeeze()
                else:
                    array[var] = vardata

            if 'latitude' in variables:
                variables[variables.index('latitude')] = u'lat'
                variables[variables.index('longitude')] = u'lon'
                try:
                    array.dtype.names = variables
                except ValueError:
                    array.dtype.names = [v.encode('utf8') for v in variables]

            starttime = get_netcdf_startdate(ncfile)
            t0 = ncfile.variables['time'][0]
            if t0 != 0:
                starttime += timedelta(**{unit: int(t0)})
    except RuntimeError as e:
        e.args += (str(filename), )
        raise
    return array, starttime


def get_netcdf_startdate(ncfile):
    """return the startdate of trajectories"""
    try:
        # if netcdf produced by lagranto
        date = [int(i) for i in ncfile.variables['BASEDATE'][0, 0, 0, :]]
        starttime = datetime(date[0], date[1], date[2], date[3], date[4])
    except KeyError:
        # if netcdf produced by the online trajectory module from COSMO
        starttime = datetime(ncfile.ref_year, ncfile.ref_month,
                             ncfile.ref_day, ncfile.ref_hour,
                             ncfile.ref_min)
    return starttime


def _netcdf_time_to_datetime(ncfile, unit='hours'):
    """ return times as datetime

        Paramters:
            ncfile : netCDF4.Dataset instance
            ntra : int
                nbre of trajectories
            unit : string, default hours
                unit of times hours or seconds
    """
    otimes = ncfile.variables['time'][:]
    starttime = get_netcdf_startdate(ncfile)

    if unit == 'hhmm':
        # lagranto writes the times as hh.mm instead as fractional times
        times = hhmm2frac(otimes)
        unit = 'hours'
    else:
        times = otimes

    units = '{} since {:%Y-%m-%d %H:%M:%S}'.format(unit, starttime)

    dates = netCDF4.num2date(times, units=units)

    return dates


def repeat_time(dates, ntra):
    dates.shape = (1, ) + dates.shape
    return dates.repeat(ntra, axis=0)


def _get_netcdf_traj_dim(ncfile):
    """ return nbre of trajectories (ntra) and nbre of timestep (ntime)"""

    dim_set = {'dimx_lon', 'id', 'ntra'}
    dim_nc = set(ncfile.dimensions.keys())

    try:
        ntra_dim = dim_set.intersection(dim_nc).pop()
        ntra = len(ncfile.dimensions[ntra_dim])
    except KeyError:
        raise Exception('Cannot read the number of trajectories, ' +
                        'not one of (' + ' '.join(dim_set) + ')')

    try:
        ntime = len(ncfile.dimensions['time'])
    except KeyError:
        ntime = len(ncfile.dimensions['ntim'])

    return ntra, ntime


def datetime_to_hours_since_start(date, start, units='hhmm'):
    """return date -start in hours"""
    hours = (date - start).total_seconds()/3600
    if units == 'hhmm':
        hours = int(hours) + 0.6 * (hours - int(hours))
    return hours


v_datetime_to_h_since_start = np.vectorize(datetime_to_hours_since_start)


def hhmm_to_hours(time):
    """Change from hh.mm to fractional hour"""
    if type(time) == bytes:
        hhmm = [float(t) for t in time.decode().split('.')]
        time = np.copysign(1, hhmm[0]) * (abs(hhmm[0]) + hhmm[1] / 60)
    else:
        h = int(time)
        m = round(100 * (time - h)) / 60
        time = h + m
    return time


hhmm2frac = np.vectorize(hhmm_to_hours)


def time_since_start_to_datetime(start, time, unit='hhmm'):
    """return start + time as datetime"""
    if unit == 'hhmm':
        time = hhmm_to_hours(time)
        unit = 'hours'
    return start + timedelta(**{unit: float(time)})


def add_times_to_netcdf(ncfile, times, startdate, unit='hours'):
    """Write times information on a netcdf file"""
    shift = startdate.second
    startdate -= timedelta(seconds=shift)
    ncfile.ref_year, ncfile.ref_month, ncfile.ref_day, ncfile.ref_hour,\
        ncfile.ref_min = startdate.timetuple()[0:5]
    ntimes = ncfile.createVariable('time', 'f4', ('ntim', ))
    units = ''
    if unit == 'seconds':
        units = 'seconds since {:%Y-%m-%d %H:%M:%S}'.format(startdate)
    elif unit == 'hours':
        units = 'hours since {:%Y-%m-%d %H:%M:%S}'.format(startdate)
    elif unit == 'hhmm':
        hhmms = v_datetime_to_h_since_start(times.astype(datetime), startdate)
        ntimes[:] = hhmms[0, :]
        return

    if type(times[0, 0]) == np.datetime64:
        t = times[0, :].astype(datetime)
        ntimes[:] = netCDF4.date2num(t, units)
    else:
        ntimes[:] = times[0, :] + shift / 3600


def to_netcdf(trajs, filename, exclude=None, unit='hours'):
    """
    Write the trajectories in a netCDF file

    Parameters
    ----------
    trajs : Tra
        A Tra instance
    filename : string
        The name of the output file
    exclude : list, optional
        A list of variables to exclude
    unit : string, optional
        The unit of the dates, can be hours, seconds or hhmm
    """
    if exclude is None:
        exclude = []
    with netCDF4.Dataset(filename, 'w', format='NETCDF3_CLASSIC') as ncfile:
        ncfile.createDimension('ntra', trajs.ntra)
        ncfile.createDimension('ntim', trajs.ntime)
        ncfile.duration = int(trajs.duration)
        ncfile.pollon = 0.
        ncfile.pollat = 90.
        add_times_to_netcdf(ncfile, trajs['time'], trajs.startdate, unit=unit)
        exclude.append('time')
        for var in trajs.variables:
            if var in exclude:
                continue
            try:
                vararray = ncfile.createVariable(var, trajs[var].dtype,
                                                 ('ntim', 'ntra'))
            except RuntimeError as err:
                err.args += (var, trajs[var].dtype)
                raise
            vararray[:] = trajs[var].T


def to_ascii(trajs, filename, mode='w', gz=False, digit=3):
    """ Write the trajectories in an ASCII format

        Parameters:

        filename : string
            filename where the trajectories are written
        mode : string, default w
            define the mode for opening the file.
            By default in write mode ('w'),
            append (a) is another option

    Parameters
    ----------
    filename: string
        filename where the trajectories are written
    mode: string, default w
        define the mode for opening the file.
        By default in write mode ('w'),
        append ('a') is another option.
    gz: boolean, default False
        If true write the file as a gzip file
    digit: int, default 3
        Number of digit after the comma to use for lon, lat;
        Only 3 or 2 digits allowed

    """
    if trajs['time'].dtype != np.float:
        trajs['timeh'] = v_datetime_to_h_since_start(
            trajs['time'].astype(datetime), trajs.initial)

    for var in trajs.variables[1:]:
        trajs[var][np.isnan(trajs[var])] = -1000

    # skip 'time' and move 'timeh' to front
    if trajs['time'].dtype != np.float:
        variables = ['timeh']+trajs.variables[1:-1]
    else:
        variables = trajs.variables

    ntraj = trajs.shape[0]
    ntim = trajs.shape[1]
    nvar = len(variables)

    trajs_resh = np.reshape(np.array([np.reshape(trajs[var], ntraj*ntim)
                                      for var in variables]).T,
                            ntraj*ntim*nvar)
    # String template for header, variables header and variables
    header = 'Reference date {:%Y%m%d_%H%M} / Time range{:>8.0f} min\n \n'
    varheader = '{:>7}{:>10}{:>9}{:>6}'

    if digit == 2:
        fixvar = '{:>7.2f}{:>9.2f}{:>8.2f}{:>6.0f}'
        lineheader = '{:->7}{:->10}{:->9}{:->6}'
    elif digit == 3:
        fixvar = '{:>7.2f}{:>10.3f}{:>9.3f}{:>6.0f}'
        lineheader = '{:->7}{:->10}{:->9}{:->6}'
    else:
        raise
    row_format = (' \n' + ((fixvar + '{:>10.3f}' * (nvar - 4)+'\n') * ntim))
    row_format *= ntraj

    if gz:
        with gzip.open(filename, mode + 't') as f:
            # write the header
            f.write(header.format(trajs.startdate, trajs.duration))

            # write the variables header
            if trajs['time'].dtype != np.float:
                f.write((varheader + '{:>10}' * (nvar - 4)
                         ).format(*trajs.variables[:-1]) + '\n')
            else:
                f.write((varheader + '{:>10}' * (nvar - 4)
                         ).format(*trajs.variables) + '\n')

            # write the line
            f.write(
                (lineheader + '{:->10}' * (nvar - 4)
                 ).format(*[''] * nvar) + '\n')

            # write the variables values
            f.write(row_format.format(*trajs_resh))
    else:
        with open(filename, mode) as f:
            # write the header
            f.write(header.format(trajs.startdate, trajs.duration))

            # write the variables header
            if trajs['time'].dtype != np.float:
                f.write((varheader + '{:>10}' * (nvar - 4)
                         ).format(*trajs.variables[:-1]) + '\n')
            else:
                f.write((varheader + '{:>10}' * (nvar - 4)
                         ).format(*trajs.variables) + '\n')

            # write the line
            f.write(
                (lineheader + '{:->10}' * (nvar - 4)
                 ).format(*[''] * nvar) + '\n')

            # write the variables values
            f.write(row_format.format(*trajs_resh))

    # remove the artificial timeh
    if trajs['time'].dtype != np.float:
        trajs.set_array(trajs[[name for name in trajs.variables[:-1]]])


def header_to_date(header):
    """ return the initial date based on the header of an ascii file"""
    try:
        starttime = datetime.strptime(header[2], '%Y%m%d_%H%M')
    except ValueError:
        try:
            starttime = datetime.strptime(
                header[2] + '_' + header[3], '%Y%m%d_%H'
            )
        except ValueError:
            print("Warning: could not retrieve starttime from header,\
                  setting to default value ")
            starttime = datetime(1970, 1, 1)

    return starttime


def get_ascii_timestep_period(times, usedatetime=True):
    """return the timestep and the period for an ascii """
    if usedatetime:
        timestep = times[1] - times[0]
        period = times[-1] - times[0]
    else:
        timestep = hhmm_to_hours(times[1]) - hhmm_to_hours(times[0])
        period = hhmm_to_hours(times[-1]) - hhmm_to_hours(times[0])
    return timestep, period


def get_ascii_header_variables(filename, gz=False):
    """return the header and variables of an ascii file"""
    if gz:
        with gzip.open(filename, 'rt') as f:
            header = f.readline().split()
            f.readline()
            variables = f.readline().split()
    else:
        with open(filename) as f:
            header = f.readline().split()
            f.readline()
            variables = f.readline().split()
    return header, variables


def from_ascii(filename, usedatetime=True, msv=-999.999, gz=False):
    """ Load trajectories from an ascii file

        Parameters:

        usedatetime: bool, default True
               If true return the dates as datetime object
        msv: float, default -999.999
               Change <msv> value into np.nan
        gzip: bool, default False
              If true read from gzip file
    """
    header, variables = get_ascii_header_variables(filename, gz=gz)

    startdate = header_to_date(header)

    dtypes = ['f8']*(len(variables))
    converters = None
    if usedatetime:
        dtypes[variables.index('time')] = 'datetime64[s]'
        t_to_d = partial(time_since_start_to_datetime, startdate)
        converters = {0: t_to_d}

    array = np.genfromtxt(filename, skip_header=5, names=variables,
                          missing_values=msv, dtype=dtypes,
                          converters=converters, usemask=True)
    for var in variables:
        if (var == 'time') and usedatetime:
            continue
        array[var] = array[var].filled(fill_value=np.nan)
    timestep, period = get_ascii_timestep_period(array['time'], usedatetime)

    # period/timestep gives strange offset (related to precision??)
    # so use scipy.around
    ntime = int(1 + np.around(period / timestep))
    ntra = int(array.size / ntime)

    array = array.reshape((ntra, ntime))
    return array, startdate
