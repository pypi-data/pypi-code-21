from datetime import datetime
from filecmp import cmp

import numpy as np
from path import Path

from lagranto import Tra

testdatadir = Path.dirname(Path(__file__)).joinpath('test_data')
netcdffile = testdatadir / 'lsl_lagranto2_0.nc'
asciifile = testdatadir / 'lsl_lagranto2_0.txt'
longasciifile = testdatadir / 'lsl_long_ASCII.txt'
asciifile_minutes = testdatadir / 'lsl_lagranto2_0_minutes.txt'
netcdffile_minutes = testdatadir / 'lsl_lagranto2_0_minutes.nc'
gzipfile = testdatadir / 'lsl_lagranto2_0.txt.gz'
onlinefile = testdatadir / 'lsl_lagranto_online.nc'
backfile = testdatadir / 'lsl_lagranto_backward_forward.txt.gz'
startdate = datetime(2000, 10, 14, 6)


def test_read_netcdf():
    trajs = Tra(netcdffile)
    assert type(trajs) == Tra


def test_read_ascii():
    trajs = Tra(asciifile)
    assert type(trajs) == Tra


def test_load_netcdf():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    assert type(trajs) == Tra
    assert trajs.initial == startdate
    assert trajs['time'][0, 0].astype(datetime) == startdate


def test_load_online_netcdf():
    trajs = Tra()
    trajs.load_netcdf(onlinefile, unit='seconds')
    assert trajs.initial == datetime(2007, 8, 8, 10, 5, 20)
    assert trajs['time'][0, 1] == datetime(2007, 8, 8, 10, 5, 40)


def test_load_netcdf_exclude():
    trajs = Tra()
    trajs.load_netcdf(netcdffile, exclude=['QV'])
    assert trajs.variables == ['time', 'lon', 'lat', 'z']


def test_load_ascii():
    trajs = Tra()
    trajs.load_ascii(asciifile)
    assert type(trajs) == Tra
    assert trajs.initial == startdate
    assert trajs['time'][0, 0].astype(datetime) == startdate


def test_load_long_ascii():
    trajs = Tra()
    trajs.load_ascii(longasciifile, msv=-999.99)
    assert type(trajs) == Tra
    assert trajs.initial == datetime(2016, 11, 17, 9)
    assert trajs.duration == -10080
    assert np.all(np.isnan(trajs['FVEL'][0, :9]))


def test_load_gzip():
    trajs = Tra()
    trajs.load_ascii(gzipfile, gz=True)
    assert type(trajs) == Tra
    assert trajs.initial == startdate


def test_array():
    trajs = Tra()
    trajs.load_ascii(gzipfile, gz=True)
    ntrajs = Tra(array=trajs[:])
    np.testing.assert_array_equal(ntrajs['QV'], trajs['QV'])


def test_write_ascii():
    outfile = testdatadir / 'lsl_lagranto2.0_test.txt'
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    trajs.write_ascii(outfile)
    assert cmp(outfile, asciifile)
    outfile.remove()


def test_write_netcdf():
    outfile = testdatadir / 'lsl_lagranto2_0_test.nc'
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    trajs.write_netcdf(outfile)
    ntrajs = Tra()
    ntrajs.load_netcdf(outfile)
    assert type(ntrajs) == Tra
    assert ntrajs.initial == startdate
    np.testing.assert_almost_equal(ntrajs['QV'], trajs['QV'])
    outfile.remove()


def test_write_ascii_digit():
    outfile = testdatadir / 'lsl_long_ASCII_test.txt'
    trajs = Tra()
    trajs.load_ascii(longasciifile)
    trajs.write_ascii(outfile, digit=2)
    assert cmp(outfile, longasciifile)
    outfile.remove()


def test_write_netcdf_exclude():
    outfile = testdatadir / 'lsl_lagranto2_0_test_exclude.nc'
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    trajs.write_netcdf(outfile, exclude=['QV'])
    ntrajs = Tra()
    ntrajs.load_netcdf(outfile)
    oldvar = trajs.variables
    oldvar.remove('QV')
    assert ntrajs.variables == oldvar
    outfile.remove()


def test_write_online_netcdf():
    outfile = testdatadir / 'lsl_lagranto_online_test.nc'
    trajs = Tra()
    trajs.load_netcdf(onlinefile, unit='seconds')
    trajs.write_netcdf(outfile, unit='seconds')
    ntrajs = Tra()
    ntrajs.load_netcdf(outfile, unit='seconds')
    assert np.all(ntrajs['time'][0, :] == trajs['time'][0, :])
    assert trajs.duration == 1.0
    outfile.remove()


def test_read_ascii_minute_datetime():
    trajs = Tra()
    trajs.load_ascii(asciifile_minutes)
    assert trajs.initial == datetime(2012, 10, 19, 9, 59)
    assert trajs['time'][0, -1] == datetime(2012, 10, 19, 13, 31)


def test_read_ascii_minute_nodatetime():
    trajs = Tra()
    trajs.load_ascii(asciifile_minutes, usedatetime=False)
    assert trajs.startdate == datetime(2012, 10, 19, 9, 59)
    assert trajs['time'][0, -1] == 3.32


def test_write_ascii_minute():
    trajs = Tra()
    trajs.load_ascii(asciifile_minutes)
    outfile = testdatadir / asciifile_minutes.namebase + '_test.txt'
    trajs.write_ascii(outfile)
    assert cmp(outfile, asciifile_minutes)
    outfile.remove()


def test_read_netcdf_hhmm():
    trajs = Tra()
    trajs.load_netcdf(netcdffile_minutes, unit='hhmm')
    assert trajs.initial == datetime(2012, 10, 19, 9, 59)
    assert trajs['time'][0, -1] == datetime(2012, 10, 19, 13, 31)


def test_write_netcdf_hhmm():
    trajs = Tra()
    trajs.load_ascii(asciifile_minutes)
    outfile = testdatadir / asciifile_minutes.namebase + '_test.nc'
    trajs.write_netcdf(outfile, unit='hhmm')
    ntrajs = Tra()
    ntrajs.load_netcdf(outfile, unit='hhmm')
    assert np.all(ntrajs['time'][0, :] == trajs['time'][0, :])
    outfile.remove()


def test_select_date_usedatetime():
    date = datetime(2000, 10, 14, 3)
    trajs = Tra()
    trajs.load_netcdf(netcdffile, date=date)
    assert trajs.ntime == 1
    assert trajs['time'][0, 0].astype(datetime) == date


def test_select_dates_usedatetime():
    dates = [datetime(2000, 10, 14, 3), datetime(2000, 10, 14, 4)]
    trajs = Tra()
    trajs.load_netcdf(netcdffile, date=dates)
    assert trajs.ntime == 2
    np.testing.assert_array_equal(trajs['time'][0, :].astype(datetime), dates)


def test_select_dates():
    dates = [-3, -5, -9]
    trajs = Tra()
    trajs.load_netcdf(netcdffile, date=dates, usedatetime=False)
    assert trajs.ntime == 3
    np.testing.assert_array_equal(trajs['time'][0, :], dates)


def test_select_date():
    date = -3
    trajs = Tra()
    trajs.load_netcdf(netcdffile, date=date, usedatetime=False)
    assert trajs.ntime == 1
    assert trajs['time'][0, 0].astype(datetime) == date


def test_backward_notdatetime():
    trajs = Tra()
    trajs.load_ascii(backfile, usedatetime=False, gz=True)
    assert trajs.startdate == datetime(2012, 10, 15)
    assert trajs['time'][0, 0] == -36.0


def test_backward_toascii():
    trajs = Tra()
    trajs.load_ascii(backfile, usedatetime=False, gz=True)
    outfile = testdatadir / backfile.namebase + '_test.txt.gz'
    trajs.write_ascii(outfile, gz=True)
    ntrajs = Tra()
    ntrajs.load_ascii(outfile, usedatetime=False, gz=True)
    assert np.all(ntrajs['time'][0, :] == trajs['time'][0, :])
    outfile.remove()


def test_concatenate():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    newtrajs = [Tra(array=trajs[t-100:t]) for t in range(100, 1000, 100)]
    tra = newtrajs[0]
    tra = tra.concatenate(newtrajs[1:])
    np.testing.assert_array_equal(tra['QV'], trajs['QV'])


def test_concatenate_inplace():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    newtrajs = [Tra(array=trajs[t-100:t]) for t in range(100, 1000, 100)]
    tra = newtrajs[0]
    tra.concatenate(newtrajs[1:], inplace=True)
    np.testing.assert_array_equal(tra['QV'], trajs['QV'])


def test_concatenate_time():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    newtrajs = [Tra(array=trajs[:, t - 3:t]) for t in range(3, 33, 3)]
    tra = newtrajs[0]
    tra.concatenate(newtrajs[1:], inplace=True, time=True)
    np.testing.assert_array_equal(tra['QV'], trajs['QV'][:, :-1])


def test_append_single():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    tra = Tra()
    tra.set_array(trajs[:-1, :])
    tra.append(Tra(array=trajs[-1:, :]))
    np.testing.assert_array_equal(tra['QV'], trajs['QV'])


def test_append():
    trajs = Tra()
    trajs.load_netcdf(netcdffile)
    newtrajs = [Tra(array=trajs[t-100:t]) for t in range(100, 1000, 100)]
    tra = newtrajs[0]
    tra.append(newtrajs[1:])
    np.testing.assert_array_equal(tra['QV'], trajs['QV'])
