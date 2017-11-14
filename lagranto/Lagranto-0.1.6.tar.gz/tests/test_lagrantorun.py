from datetime import datetime, timedelta

import pytest
from lagranto import LagrantoRun
from lagranto.lagranto import link_files
from path import Path


@pytest.fixture()
def sdates():
    sdate = datetime(2000, 10, 10, 0)
    edate = datetime(2000, 10, 11, 0)
    hours = int((edate - sdate).total_seconds()/3600)
    sdates = [sdate + timedelta(hours=h) for h in range(hours)]
    return sdates


@pytest.fixture()
def workingdir(sdates):
    workingdir = Path('workingdir')
    workingdir.makedirs_p()
    cstfile = workingdir / 'lffd{:%Y%m%d%H}c.nc'.format(sdates[0])
    cstfile.touch()
    for d in sdates:
        filename = workingdir / 'lffd{:%Y%m%d%H}.nc'.format(d)
        filename.touch()
    yield workingdir
    workingdir.rmtree_p()


@pytest.fixture()
def outdir():
    outdir = Path('outdir')
    outdir.makedirs_p()
    yield outdir
    outdir.rmtree_p()


@pytest.fixture
def lrun(sdates, workingdir, outdir):
    dates = [(d, d + timedelta(hours=3)) for d in sdates]
    lrun = LagrantoRun(dates, workingdir=workingdir, outputdir=outdir)
    return lrun


def test_linkfiles(workingdir):
    testdir = Path('testdir')
    testdir.makedirs_p()
    link_files(workingdir, testdir)
    files = testdir.files()
    assert Path('testdir/LMCONSTANTS') in files
    for f in files:
        assert f.isfile()
    testdir.rmtree_p()


def test_linkfiles_startdate(workingdir):
    testdir = Path('testdir')
    testdir.makedirs_p()
    link_files(workingdir, testdir, startdate=datetime(2000, 10, 10, 12))
    files = testdir.files()
    assert Path('testdir/P20001010_00') not in files
    assert Path('testdir/P20001010_11') not in files
    assert Path('testdir/P20001010_12') in files
    assert Path('testdir/S20001010_12') in files
    assert Path('testdir/P20001010_23') in files
    for f in files:
        assert f.isfile()
    testdir.rmtree_p()


def test_linkfiles_enddate(workingdir):
    testdir = Path('testdir')
    testdir.makedirs_p()
    link_files(workingdir, testdir, enddate=datetime(2000, 10, 10, 12))
    files = testdir.files()
    assert Path('testdir/P20001010_00') in files
    assert Path('testdir/P20001010_11') in files
    assert Path('testdir/P20001010_12') not in files
    assert Path('testdir/P20001010_23') not in files
    for f in files:
        assert f.isfile()
    testdir.rmtree_p()


@pytest.fixture()
def caltra_header():
    return """
    caltra.cosmo() {{
        echo "caltra.cosmo $*"
        }}
    cd {workingdir}
    touch lsl_2000101000.4
    """


def test_caltra(lrun, caltra_header):
    lrun.cmd_header = caltra_header
    out = lrun.caltra(*lrun.dates[0])
    cmd = 'caltra.cosmo 20001010_00 20001010_03 startf.4' \
          ' lsl_2000101000.4 -j\n'
    assert out == cmd
    assert lrun.outputdir / 'lsl_2000101000.4' in lrun.outputdir.files()


@pytest.fixture()
def create_header():
    cmd_header = """
    startf.cosmo() {{
        echo "startf.cosmo $*"
        }}
    lsl2list.cosmo() {{
        echo "lsl2list.cosmo $*"
        }}
    cd {workingdir}
    touch startf.4
    touch startf.startf
    """
    return cmd_header


def test_createstartf(lrun, create_header):
    lrun.cmd_header = create_header
    out = lrun.create_startf(lrun.dates[0][0], 'test')
    cmd = 'startf.cosmo 20001010_00 startf.4 test\n'
    assert out == cmd
    assert lrun.outputdir / 'startf.4' in lrun.outputdir.files()


def test_createstartf_tolist(lrun, create_header):
    lrun.cmd_header = create_header
    out = lrun.create_startf(lrun.dates[0][0], 'test', tolist=True)
    cmd = 'startf.cosmo 20001010_00 startf.4 test\n' \
          'lsl2list.cosmo startf.4 startf.startf\n'
    assert out == cmd
    assert lrun.outputdir / 'startf.startf' in lrun.outputdir.files()


def test_createstartf_filename(lrun, create_header):
    lrun.cmd_header = create_header + '\n touch startf_2000101000.4'
    out = lrun.create_startf(lrun.dates[0][0], 'test',
                             filename='startf_{date:%Y%m%d%H}.4')
    cmd = 'startf.cosmo 20001010_00 startf_2000101000.4 test\n'
    assert out == cmd
    assert lrun.outputdir / 'startf_2000101000.4' in lrun.outputdir.files()


@pytest.fixture()
def trace_header():
    return """
    trace.cosmo() {{
        echo "trace.cosmo $*"
        }}
    cd {workingdir}
    touch lsl_2000101000.4
    """


def test_trace(lrun, trace_header):
    lrun.cmd_header = trace_header
    out = lrun.trace(lrun.dates[0][0])
    cmd = 'trace.cosmo lsl_2000101000.4 lsl_2000101000.4\n'
    assert out == cmd
    assert lrun.outputdir / 'lsl_2000101000.4' in lrun.outputdir.files()


def test_trace_output(lrun, trace_header):
    lrun.cmd_header = trace_header + '\n touch test.4'
    out = lrun.trace(lrun.dates[0][0], outfile='test.4')
    cmd = 'trace.cosmo lsl_2000101000.4 test.4\n'
    assert out == cmd
    assert lrun.outputdir / 'test.4' in lrun.outputdir.files()


def test_single_run(lrun, trace_header, caltra_header):
    lrun.cmd_header = caltra_header + trace_header
    out = lrun.single_run(*lrun.dates[0])
    cmd = 'caltra.cosmo 20001010_00 20001010_03 startf.4' \
          ' lsl_2000101000.4 -j\n' \
          'trace.cosmo lsl_2000101000.4 lsl_2000101000.4\n'
    assert out == cmd
    assert lrun.outputdir / 'lsl_2000101000.4' in lrun.outputdir.files()


def test_single_run_all(lrun, trace_header, caltra_header, create_header):
    lrun.cmd_header = create_header + caltra_header + trace_header
    startf_kw = {'specifier': 'test'}
    out = lrun.single_run(*lrun.dates[0], type='all', startf_kw=startf_kw)
    cmd = 'startf.cosmo 20001010_00 startf.4 test\n' \
          'caltra.cosmo 20001010_00 20001010_03 startf.4' \
          ' lsl_2000101000.4 -j\n' \
          'trace.cosmo lsl_2000101000.4 lsl_2000101000.4\n'
    assert out == cmd
    assert lrun.outputdir / 'startf.4' in lrun.outputdir.files()
    assert lrun.outputdir / 'lsl_2000101000.4' in lrun.outputdir.files()


def test_different_create(lrun, caltra_header):
    create_header = """
    startf.cosmo() {{
        echo "startf.cosmo $*"
    }}
    cd {workingdir}
    """
    for d in lrun.dates:
        caltra_header += "\ntouch lsl_{:%Y%m%d%H}.4\n".format(d[0])
        create_header += "\ntouch startf_{:%Y%m%d%H}.4\n".format(d[0])
    lrun.cmd_header = create_header + caltra_header

    out = lrun.run(startf_kw={'filename': 'startf_{date:%Y%m%d%H}.4',
                              'specifier': 'test'}, type='create')
    cmd = 'startf.cosmo 20001010_10 startf_2000101010.4 test\n' \
          'caltra.cosmo 20001010_10 20001010_13 startf_2000101010.4' \
          ' lsl_2000101010.4 -j\n'
    assert out[10] == cmd
    assert lrun.outputdir / 'startf_2000101011.4' in lrun.outputdir.files()
    assert lrun.outputdir / 'lsl_2000101020.4' in lrun.outputdir.files()