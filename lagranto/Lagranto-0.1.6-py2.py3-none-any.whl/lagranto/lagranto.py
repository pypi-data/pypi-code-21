#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, timedelta
from functools import partial
from functools import wraps
from multiprocessing.pool import Pool

import numpy as np
from path import Path

try:
    from shutil import SameFileError
except ImportError:
    from shutil import Error as SameFileError
from tempfile import mkdtemp

from .tools import LagrantoException, run_cmd
from .formats import from_netcdf, to_ascii, from_ascii, to_netcdf

_all__ = ['Tra', 'LagrantoRun']


class Tra(object):
    """Class to work with LAGRANTO output.

    Read trajectories from a LAGRANTO file and return a structured numpy array

    Parameters
    ----------
        filename : string
            File containing lagranto trajectories
        usedatetime: bool
            Read times as datetime objects, default True
        array: structured array
            If defined creates a new Tra object filled with the array

    Returns
    -------
        structured array (Tra): trajs(ntra,ntime) with variables as tuple.

    Examples
    --------

    >>>    filename = 'mylslfile.nc'
    >>>    trajs = Tra()
    >>>    trajs.load_netcdf(filename)
    >>>    trajs['lon'][0,:]  # return the longitudes for the first trajectory.

    >>> trajs = Tra(filename)
    >>> selected_trajs = Tra(array=trajs[[10, 20, 30], :])

    Author : Nicolas Piaget, ETH Zurich , 2014
             Sebastiaan Crezee, ETH Zurich , 2014

    """

    _startdate = None

    def __init__(self, filename='', usedatetime=True, array=None, **kwargs):
        """Initialized a Tra object.

        If filename is given, try to load it directly;
        Arguments to the load function can be passed as key=value argument.
        """
        typefile = kwargs.pop('typefile', None)
        if typefile is not None:
            msg = 'typefile is not used anymore;' \
                  'it will be remove in futur version'
            raise DeprecationWarning(msg)
        if not filename:
            if array is None:
                self._array = None
            else:
                self._array = array
            return

        try:
            self.load_netcdf(filename, usedatetime=usedatetime, **kwargs)
        except (OSError, IOError, RuntimeError):
            try:
                self.load_ascii(filename, usedatetime=usedatetime, **kwargs)
            except Exception:
                raise IOError("Unkown fileformat. Known formats \
                               are ascii or netcdf")

    def __len__(self):
        return len(self._array)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._array, attr)

    def __getitem__(self, key):
        return self._array[key]

    def __setitem__(self, key, item):
        if type(key) is slice:
            self._array = item
        elif key in self.dtype.names:
            self._array[key] = item
        else:
            dtypes = self._array.dtype.descr
            dtypes.append((key, item.dtype.descr[0][1]))
            dtypes = [(str(d[0]), d[1]) for d in dtypes]
            newarr = np.zeros(self._array.shape, dtype=dtypes)
            for var in self.variables:
                newarr[var] = self._array[var]
            newarr[key] = item
            self._array = newarr

    def __repr__(self):
        try:
            string = " \
            {} trajectories with {} time steps. \n \
            Available fields: {}\n \
            total duration: {} minutes".format(
                self.ntra, self.ntime,
                "/".join(self.variables),
                self.duration
            )
        except AttributeError:
            # Assume it's an empty Tra()
            string = "\
            Empty trajectories container.\n\
            Hint: use load_ascii() or load_netcdf()\n\
            to load data"
        return string

    @property
    def ntra(self):
        if self.ndim < 2:
            print(" \
                Be careful with the dimensions, \
                you may want to change the shape: \n \
                either shape + (1,) or (1,)+shape \
                ")
            return None
        return self.shape[0]

    @property
    def ntime(self):
        if self.ndim < 2:
            print(" \
                Be careful with the dimensions,\
                you may want to change the shape: \n \
                either shape + (1,) or (1,)+shape \
                ")
            return None
        return self.shape[1]

    @property
    def variables(self):
        return list(self.dtype.names)

    @property
    def duration(self):
        """Time duration in minutes."""
        end = self['time'][0, -1]
        start = self['time'][0, 0]
        delta = end - start
        if type(delta) == np.dtype('timedelta64'):
            return delta.astype(timedelta).total_seconds() / 60.
        else:
            return delta * 60.

    @property
    def initial(self):
        """Give the initial time of the trajectories."""
        starttime = self['time'][0, 0]
        return starttime.astype(datetime)

    @property
    def startdate(self):
        if self._startdate is None:
            time0 = self['time'][0, 0]
            if type(time0) == np.datetime64:
                self._startdate = time0.astype(datetime)
            else:
                self._startdate = datetime(1900, 1, 1, 0)
        return self._startdate

    def set_array(self, array):
        """To change the trajectories array."""
        self._array = array

    def concatenate(self, trajs, time=False, inplace=False):
        """To concatenate trajectories together.

        Concatenate trajectories together and return a new object.
        The trajectories should contain the same variables.
        if time=False, the number of timestep in each trajs should be the same
        if time=True, the number of trajectories in each Tra should be the same

        Parameters
        ----------

            trajs: Tra or list of Tra
                Trajectories to concatenate with the current one
            time: bool, default False
                if True concatenate along the time dimension
            inplace: bool, default False
                if True append the trajs to current Tra object and return None

        Returns
        -------
        Tra
            Return a new Tra (trajectories) object

        Examples
        --------

        Create a new Tra object which include trajs and all newtrajs

        >>> files = ['lsl_20001010_00.4', 'lsl_2001010_01.4']
        >>> filename = files[0]
        >>> trajs = Tra(filename)
        >>> newtrajs = [Tra(f) for f in files]
        >>> alltrajs = trajs.concatenate(newtrajs)

        Append newtrajs to trajs

        >>> trajs = Tra(filename)
        >>> newtrajs = [Tra(f) for f in files]
        >>> trajs.concatenate(newtrajs, inplace=True)

        """
        if type(trajs) not in [tuple, list]:
            trajs = (trajs,)
        if time:
            trajstuple = (self._array.T,)
            trajstuple += tuple(tra._array.T for tra in trajs)
            test = np.concatenate(trajstuple).T
        else:
            trajstuple = (self._array,)
            trajstuple += tuple(tra._array for tra in trajs)
            test = np.concatenate(trajstuple)

        if inplace:
            self._array = test
        else:
            newtrajs = Tra()
            newtrajs.set_array(test)
            return newtrajs

    def append(self, trajs):
        """append trajectories

        Parameters
        ---------
        trajs: single Tra or list of Tra
                Trajectories to concatenate with the current one

        Examples
        --------

        >>> files = ['lsl_20001010_00.4', 'lsl_2001010_01.4']
        >>> filename = files[0]
        >>> trajs = Tra(filename)
        >>> newtrajs = [Tra(f) for f in files]
        >>> trajs.append(newtrajs)
        """
        self.concatenate(trajs, inplace=True)

    def write(self, filename, fileformat='netcdf'):
        globals()['_write_{}'.format(fileformat)](self, filename)

    def load_netcdf(self, filename, usedatetime=True, msv=-999, unit='hours',
                    exclude=None, date=None):
        self._array, self._startdate = from_netcdf(filename,
                                                   usedatetime=usedatetime,
                                                   msv=msv,
                                                   unit=unit,
                                                   exclude=exclude,
                                                   date=date)
    load_netcdf.__doc__ = from_netcdf.__doc__

    def write_netcdf(self, filename, exclude=None, unit='hours'):
        to_netcdf(self, filename, exclude=exclude, unit=unit)
    write_netcdf.__doc__ = to_netcdf.__doc__

    def write_ascii(self, filename, gz=False, digit=3, mode='w'):
        to_ascii(self, filename, gz=gz, digit=digit, mode=mode)
    write_ascii.__doc__ = to_ascii.__doc__

    def load_ascii(self, filename, usedatetime=True, msv=-999.999, gz=False):
        self._array, self._startdate = from_ascii(filename,
                                                  usedatetime=usedatetime,
                                                  msv=msv,
                                                  gz=gz)
    load_ascii.__doc__ = from_ascii.__doc__


def intmpdir(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        workingdir = args[0]
        no_tmp_dir = kwds.get('no_tmp_dir', False)
        if Path(workingdir).parent == '/tmp' or no_tmp_dir:
            return f(*args, **kwds)
        else:
            tmpdir = Path(mkdtemp())
            lwkds = {key: value for key, value in kwds.items()
                     if key in ['outputdir', 'version', 'sdate']}
            link_files(workingdir, tmpdir, **lwkds)
            nargs = (tmpdir,) + args[1:]
            out = f(*nargs, **kwds)
            tmpdir.rmdir_p()
            return out
    return wrapper


@intmpdir
def create_startf(workingdir, date, filename, specifier, version='cosmo',
                  outputdir='', sdate=None, tolist=False, cmd_header=None,
                  options=None):
    """ Create a startfile for LAGRANTO."""
    outputdir = Path(outputdir)
    workingdir = Path(workingdir)
    create = "startf.{version} "
    create += "{date:%Y%m%d_%H} {filename} {specifier}"
    if options is not None:
        if type(options) is list:
            for option in options:
                create += ' ' + option
        else:
            raise LagrantoException('options as to be a list of string')
    # if tolist:
    #     filename = Path(filename).splitext()[0] + '.4'
    create = create.format(version=version, date=date,
                           filename=filename, specifier=specifier)
    out = run_cmd(create, workingdir, cmd_header=cmd_header)
    if tolist:
        lslname = filename
        filename = Path(lslname).splitext()[0] + '.startf'
        lsl2list = 'lsl2list.{} {} {}'.format(version, lslname, filename)
        out += run_cmd(lsl2list, workingdir, cmd_header=cmd_header)
    try:
        Path.copy(workingdir / filename, outputdir / filename)
    except SameFileError:
        pass
    if tolist:
        return out, filename
    else:
        return out


@intmpdir
def select(workingdir, inpfile, outfile, crit,
           outputdir='', sdate=None, version='cosmo',
           cmd_header=None, **kwargs):
    """Select trajectories."""
    netcdf_format = kwargs.pop('netcdf_format', 'CF')
    select_cmd = 'select.{version} {inpfile} {outfile} "{crit}"'
    select_cmd = select_cmd.format(version=version, inpfile=inpfile,
                                   outfile=outfile, crit=crit)
    out = run_cmd(select_cmd, workingdir,
                  netcdf_format=netcdf_format, cmd_header=cmd_header)
    outputdir = Path(outputdir)
    try:
        Path.copy(workingdir / outfile, outputdir / outfile)
    except SameFileError:
        pass
    return out


@intmpdir
def trace(workingdir, filename, outputdir='', outfile='', tracevars='',
          tracevars_content='', field='', sdate=None, version='cosmo',
          cmd_header=None, **kwargs):
    """Trace variables along a trajectory."""
    netcdf_format = kwargs.pop('netcdf_format', 'CF')
    workingdir = Path(workingdir)
    outputdir = Path(outputdir)
    if not outfile:
        outfile = filename
    trace_cmd = 'trace.{version} {filename} {outfile}'
    tracevars_file = 'tracevars'
    if tracevars:
        tracevars_file = tracevars
        trace_cmd += ' -v ' + tracevars
    if tracevars_content:
        with (Path(workingdir) / tracevars_file).open('w') as f:
            f.write(tracevars_content)
    if field:
        trace_cmd += ' -f ' + field
    trace_cmd = trace_cmd.format(filename=filename, outfile=outfile,
                                 version=version)
    out = run_cmd(trace_cmd, workingdir,
                  netcdf_format=netcdf_format, cmd_header=cmd_header)
    try:
        Path.copy(workingdir / outfile, outputdir / outfile)
    except SameFileError:
        pass
    return out


@intmpdir
def caltra(workingdir, startdate, enddate, startfile, filename,
           jump=True, outputdir='', sdate=None, version='cosmo',
           cmd_header=None, withtrace=False, tracevars_content='',
           tracevars='', **kwargs):
    """Calculate trajectories for air parcels.

    starting at positions specified in startfile.
    """
    outputdir = Path(outputdir)
    netcdf_format = kwargs.pop('netcdf_format', 'CF')
    no_tmp_dir = kwargs.pop('no_tmp_dir', False)
    prefix = kwargs.pop('prefix', '')
    if no_tmp_dir:
        filename = outputdir / filename
    if not withtrace:    
        caltra_cmd = 'caltra.{version}'
        caltra_cmd += ' {startdate:%Y%m%d_%H} {enddate:%Y%m%d_%H}'
        caltra_cmd += ' {startfile} {filename}'
        if jump:
            caltra_cmd += ' -j'
        for key, value in kwargs.items():
            caltra_cmd += ' -{key} {value}'.format(key=key, value=value)
        caltra_cmd = caltra_cmd.format(startdate=startdate, enddate=enddate,
                                       startfile=startfile, filename=filename,
                                       version=version)
    else:
        tracevars_file = tracevars if tracevars else 'tracevars'
        if tracevars_content:
            with (Path(workingdir) / tracevars_file).open('w') as f:
                f.write(tracevars_content)
        delta = (enddate - startdate).total_seconds() / (60 * 60)
        caltra_cmd = 'caltra {startfile} {delta:1.0f} {filename} '
        caltra_cmd += '-ref {startdate:%Y%m%d_%H%M}'
        for key, value in kwargs.items():
            caltra_cmd += ' -{key} {value}'.format(key=key, value=value)
        caltra_cmd = caltra_cmd.format(startdate=startdate, delta=delta,
                                       startfile=startfile, filename=filename)
    out = run_cmd(caltra_cmd, workingdir, netcdf_format=netcdf_format,
                  cmd_header=cmd_header, prefix=prefix)
    if not no_tmp_dir:
        try:
            Path.copy(workingdir / filename, outputdir / filename)
        except SameFileError:
            pass
    return out


@intmpdir
def density(workingdir, inpfile, outfile,
            outputdir='', sdate=None, version='cosmo',
            cmd_header=None, **kwargs):
    """Calculate trajectories density."""
    outputdir = Path(outputdir)
    netcdf_format = kwargs.pop('netcdf_format', 'CF')
    density_cmd = 'density.{version} {inpfile} {outfile}'
    for key, value in kwargs.items():
        density_cmd += ' -{key} {value}'.format(key=key, value=value)
    density_cmd = density_cmd.format(inpfile=inpfile, outfile=outfile,
                                     version=version)
    out = run_cmd(density_cmd, workingdir,
                  netcdf_format=netcdf_format, cmd_header=cmd_header)
    try:
        Path.copy(workingdir / outfile, outputdir / outfile)
    except SameFileError:
        pass
    return out


def link_files(folder, tmpdir, outputdir='', version='cosmo',
               sdate=None, sfiles=True, startdate=None, enddate=None):
    """Link data from `folder`, `outputdir`, to `tmpdir`.

    Transform lff[d,f]*.nc files from `folder` in P and S files.

    Parameters
    ----------
    folder: string,
        Path to the origin folder
    tmpdir: string,
        Path to the destination folder
    outputdir: string,
        Path to the folder where results are saved
    version: string,
        Only cosmo is available for now
    sdate: datetime object,
        Starting date of the cosmo run;
        Useful is the cosmo file are named in forecast mode
    sfiles: boolean,
        If True create link with prefix S as well, pointing to the same files
        as the P files.
    startdate: datetime object,
        First date for which to link files. (inclusive)
    enddate: datetime object,
        Last date for which ti link files (exclusive)
    """
    # the necessary files
    folder = Path(folder).abspath()
    tmpdir = Path(tmpdir)
    files = set(folder.files())
    if version == 'cosmo':
        constant_file = folder.files('l*c.nc')[0]
        if constant_file.isfile():
            constant_file.symlink(tmpdir / 'LMCONSTANTS')
        cosmofiles = set(folder.files('lff[df]*[0-9].nc'))
        for fname in cosmofiles:
                try:
                    date = datetime.strptime(fname.name, 'lffd%Y%m%d%H.nc')
                except ValueError:
                    sfname = fname.name[4:-3]
                    dd, hh, mm, ss = [int(sfname[i:i + 2])
                                      for i in range(0, len(sfname), 2)]
                    date = sdate + timedelta(days=dd, hours=hh,
                                             minutes=hh, seconds=ss)
                if (startdate is not None) and (date < startdate):
                    continue
                if (enddate is not None) and (date >= enddate):
                    continue
                pfile = 'P{:%Y%m%d_%H}'.format(date)
                fname.symlink(tmpdir / pfile)
                if sfiles:
                    sfile = 'S{:%Y%m%d_%H}'.format(date)
                    fname.symlink(tmpdir / sfile)
        files = files.difference(cosmofiles)
    for fname in files:
        try:
            fname.symlink(tmpdir / fname.name)
        except FileExistsError:
            pass
    if outputdir:
        outputdir = Path(outputdir).abspath()
        for fname in outputdir.files():
            try:
                fname.symlink(tmpdir / fname.name)
            except FileExistsError:
                pass


class LagrantoRun:
    """Perform Lagranto calculation.

    Parameters
    ----------
    dates: list
        list of (startdate, enddate) tuple
    workingdir: string, optional
        path to the model output directory, default to current
    outputdir: string, optional
        path to the trajectory utput directory, defautl to current
    startf: string, optional
        name of the startf to use (or to create), default to startf.4
        The format parameter date can be used, for ex: startf_{date:%Y%m%d%H}.4
    lslname: string, optional
        name of the lsl file, define its type, default to lsl_{:%Y%m%d%H}.4
    tracevars: string, optional
        name of a tracevars file as used by trace, default to none
    field: string, optional
        name of a single field to trace, default to none
    version: string, optional
        name of the model version to use, currently only cosmo (default)
    linkfiles: function, optional
        function used to overwrite link_files in run.
        Should be used if COSMO output is not standard netcdf
    nprocesses: int, optional
        Number of processes used when running in parallel, default to 10
    sdate: datetime object,
        Starting date of the simulation;
        useful if files are named in forecast mode
    fresh: bool, optional
        Fresh start. Remove output directory first.
    cmd_header: string, optional
        Change the header using for running the command;
        see ``run_cmd`` help for more details.
    """

    def __init__(self, dates, workingdir='.', outputdir='.',
                 startf='startf.4', lslname='lsl_{:%Y%m%d%H}.4',
                 tracevars='', field='', version='cosmo', linkfiles=None,
                 nprocesses=10, sdate=None, fresh=False, cmd_header=None):
        self.dates = dates
        self.workingdir = Path(workingdir).abspath()
        self.outputdir = Path(outputdir).abspath()
        if fresh:
            self.clear()
        self.outputdir.makedirs_p()
        self.startf = Path(startf)
        self.lslname = lslname
        self.tracevars = tracevars
        self.field = field
        self.version = version
        self.link_files = linkfiles if linkfiles else link_files
        self.nprocesses = nprocesses
        self.sdate = sdate
        self.cmd_header = cmd_header

    def create_startf(self, date, specifier, filename='', tolist=False,
                      **kwargs):
        """Create a file with the starting position of the trajectories.

        Parameters
        ----------
        date: datetime
            date for which the startf date is produced
        specifier: string
            detailed description of starting positions;
            (see LAGRANTO documentations for more details)
        filename: string
            filename where starting positions are saved;
            the default is defined by `LagrantoRun`
            Can make use of the format parameter date, for example:
            startf_{date:%Y%m%d%H}.4
        tolist: bool
            If the starting position should be saved as a list of points;
             Useful if the same file is used for different starting times
        kwargs: dict
            key, value options, possible values are listed bellow;

            - cmd_header:
              header to add to the shell command;
              (see `run_cmd` for more details)
            - options:
              list of options to pass to the startf function;
              (see the LAGRANTO documentation for more details)


        """
        if filename:
            startf = Path(filename.format(date=date))
            self.startf = startf
        else:
            startf = self.startf.format(date=date)
        out = create_startf(self.workingdir, date, startf, specifier,
                            outputdir=self.outputdir, sdate=self.sdate,
                            version=self.version, tolist=tolist,
                            cmd_header=self.cmd_header, **kwargs)
        if tolist:
            self.startf = out[1]
            return out[0]
        else:
            return out

    def caltra(self, startdate, enddate, filename='', **kwargs):
        """Compute trajectories for the given startdate"""
        if filename:
            self.lslname = filename
        self.caltra_out = self.lslname.format(startdate)
        return caltra(self.workingdir, startdate, enddate, self.startf,
                      self.caltra_out, outputdir=self.outputdir,
                      sdate=self.sdate, version=self.version,
                      cmd_header=self.cmd_header, **kwargs)

    def trace(self, date, filename='', outfile='', tracevars='',
              tracevars_content='', field='', **kwargs):
        r"""Trace variable along a trajectory.

        Trace meteorological fields along trajectories

        Parameters
        ----------
        date: datetime object
            starting date of the trajectories to trace
        filename: string, optional
            If not specified use `LagrantoRun.lslname`
        outfile: string, optional
            If not specified same as `filename`
        tracevars: string, optional
            Name of the file with the field to trace;
            If not specified use `LagrantoRun.tracevars`
        tracevars_content: string, optional
            Content of the tracevars file;

            .. code_block: python

            \"\"\"\n
            QV      1000. P 1\n
            PV      1.    T 1\n
            \"\"\"

        field: string,
            Specify a field to trace as follow: QV 1.
        kwargs
        """
        tracef = tracevars if tracevars else self.tracevars
        fieldv = field if field else self.field
        filename = filename if filename else self.lslname
        filename = filename.format(date)
        return trace(self.workingdir, filename, outfile=outfile,
                     outputdir=self.outputdir, tracevars=tracef,
                     tracevars_content=tracevars_content,
                     field=fieldv, sdate=self.sdate,
                     version=self.version, cmd_header=self.cmd_header, **kwargs)

    def density(self, inpfile=None, outfile=None, **kwargs):
        """Return the density of trajectories"""
        if inpfile is None:
            try:
                inpfile = self.caltra_out
            except AttributeError:
                raise ValueError('Provide an input file or run caltra')
        if outfile is None:
            self.density_out = 'density.4'
        else:
            self.density_out = outfile
        return density(self.workingdir, inpfile=inpfile,
                       outfile=self.density_out, outputdir=self.outputdir,
                       sdate=self.sdate, version=self.version,
                       cmd_header=self.cmd_header, **kwargs)

    def select(self, inpfile=None, outfile=None, **kwargs):
        """Perform selection of trajectories"""
        if inpfile is None:
            try:
                inpfile = self.caltra_out
            except AttributeError:
                raise ValueError('Provide an input file or run caltra')
        if outfile is None:
            self.select_out = 'selected.4'
        else:
            self.select_out = outfile
        return select(self.workingdir, inpfile=inpfile,
                      outfile=self.select_out, outputdir=self.outputdir,
                      sdate=self.sdate, version=self.version,
                      cmd_header=self.cmd_header, **kwargs)

    def run(self, caltra_kw=None, trace_kw=None, startf_kw=None, **kwargs):
        """Run caltra, trace, and/or create_startf.

        Run single_run for each dates tuple
        See single_run description for more details.

        Parameters
        ----------
        caltra_kw: dictionary
            Arguments to pass to the caltra function
        trace_kw: dictionary
            Arguments to pass to the trace function
        startf_kw: dictionary
            Arguments to pass to the create_startf function
        kwargs:
            Arguments to pass to the single_run function

        Returns
        ------
        A list of single_run result: list
        """
        results = []
        if caltra_kw is None:
            caltra_kw = dict()
        if trace_kw is None:
            trace_kw = dict()
        if startf_kw is None:
            startf_kw = dict()
        for sd, ed in self.dates:
            res = self.single_run(sd, ed, caltra_kw=caltra_kw,
                                  trace_kw=trace_kw,
                                  startf_kw=startf_kw, **kwargs)
            results.append(res)
        return results

    def run_parallel(self, caltra_kw=None, trace_kw=None, startf_kw=None,
                     nprocesses=None, **kwargs):
        """Run caltra, trace, and/or create_startf in parallel.

        Run single_run for each dates tuple using `multiprocessing.Pool`.
        See single_run description for more details.

        Warning:  If you use run_parallel with create_startf and
        if the starting file is not a list, be sure that every starting file
        has a different name, for example doing as follow:

        >>> LagrantoRun(startf='startf_{date:%Y%m%d_%H.4}', ...)


        Parameters
        ----------
        caltra_kw: dictionary
            Arguments to pass to the caltra function
        trace_kw: dictionary
            Arguments to pass to the trace function
        startf_kw: dictionary
            Arguments to pass to the create_startf function
        nprocesses: int,
            Number of processors to use
        kwargs:
            Arguments to pass to the single_run function

        Returns
        -------
        A list of single_run results: list
        """
        if caltra_kw is None:
            caltra_kw = dict()
        if trace_kw is None:
            trace_kw = dict()
        if startf_kw is None:
            startf_kw = dict()
        if nprocesses is not None:
            self.nprocesses = nprocesses

        single_run = partial(self.single_run, caltra_kw=caltra_kw,
                             trace_kw=trace_kw, startf_kw=startf_kw, **kwargs)
        with Pool(processes=self.nprocesses) as pool:
            results = pool.starmap(single_run, self.dates)
        return results

    def single_run(self, sd, ed, caltra_kw=None, trace_kw=None, startf_kw=None,
                   type='both', debug=False, **kwargs):
        """Run caltra, trace and/or create_startf for a given starting date

        Compute a trajectory set using caltra, trace and/or create_startf in a
        temporary directory. Need a working installation of LAGRANTO.

        If caltra, trace or create_startf return a error, single_run return
        a LagrantoException error with the path of the temporary directory.
        In this case, the temporary directory is not deleted.


        Parameters
        ----------
        sd: datetime
            Starting date of the trajectory
        ed: datetime
            Ending date of the trajectory
        caltra_kw: dictionary
            Arguments to pass to the caltra function
        trace_kw: dictionary
            Arguments to pass to the trace function
        startf_kw: dictionary
            Arguments to pass to the create_startf function
        type: string (default both)
            Define the type a run to perform:
            both: caltra + trace
            caltra: caltra
            trace: trace
            all: create_startf + caltra + trace
            create: create_startf + caltra
        debug: Boolean
            If True raise LagrantoException instead of return it as string
        kwargs: dictionnary
            Arguments to pass to the link_files function

        Returns
        -------
        output of caltra, trace and/or create_startf: str

        """
        if caltra_kw is None:
            caltra_kw = dict()
        if trace_kw is None:
            trace_kw = dict()
        if startf_kw is None:
            startf_kw = dict()

        workingdir = self.workingdir
        tmpdir = Path(mkdtemp())
        self.workingdir = tmpdir
        nkwargs = {'version': self.version,
                   'outputdir': self.outputdir,
                   'sdate': self.sdate}
        nkwargs.update(kwargs)
        self.link_files(workingdir, tmpdir, **nkwargs)
        out = ''
        try:
            if type == 'both':
                out += self.caltra(sd, ed, **caltra_kw)
                out += self.trace(sd, **trace_kw)
            elif type == 'caltra':
                out += self.caltra(sd, ed, **caltra_kw)
            elif type == 'trace':
                out += self.trace(sd, **trace_kw)
            elif (type == 'all') or (type == 'create'):
                if 'specifier' not in startf_kw.keys():
                    raise LagrantoException('specifier need to be specified'
                                            ' in startf_kw for type:"{}", '
                                            'see create_starf function'
                                            ''.format(type))
                out += self.create_startf(sd, **startf_kw)
                out += self.caltra(sd, ed, **caltra_kw)
                if type == 'all':
                    out += self.trace(sd, **trace_kw)
        except LagrantoException as err:
            err.args += (tmpdir,)
            if debug:
                raise
            else:
                return err
        self.workingdir = workingdir
        tmpdir.rmtree_p()
        return out

    def clear(self):
        self.outputdir.rmtree_p()
