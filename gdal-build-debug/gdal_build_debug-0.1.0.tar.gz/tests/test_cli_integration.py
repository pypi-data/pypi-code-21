import subprocess
import os
import pytest
import re

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)

cli_location = os.path.join(__location__, '..', 'gdal_build_debug', 'cli.py')
os.environ['PATH_TO_GDAL_CONFIG_LOG'] = os.path.join(
    __location__, 'fixtures', 'configure.log'
    )


def call(arg, *args):
    'calls args'
    return subprocess.run(
        [i for i in arg.split()] + [i for i in args],
        check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )


def call_cli(cmd):
    return call('python {} {}'.format(cli_location, cmd))


def call_cli_unchecked(cmd):
    return subprocess.run(
        'python {} {}'.format(cli_location, cmd).split(),
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )


def assert_success(to_check, count=1):
    assert len(re.findall('✓', to_check)) == count


def assert_failure(to_check, count=1):
    assert len(re.findall('×', to_check)) == count


@pytest.mark.parametrize('cmd', ('', '--help', 'config --help', 'cli --help'))
def test_init(cmd):
    'test each command / subcommand intializes'
    result = call_cli(cmd)
    assert result.stdout.decode()


@pytest.mark.parametrize('cmd', (
    'config --with png --with grib',
    'config --without pdf --without geos'
))
def test_config_log_check_passes_correctly(cmd):
    result = call_cli(cmd)
    assert_success(result.stdout.decode(), 2)


@pytest.mark.parametrize('cmd', (
    'config --without png',
    'config --with png --without grib',
    'config --without pdf --with geos'
))
def test_config_log_check_fails_correctly(cmd):
    try:
        call_cli(cmd)
        raise AssertionError('Should raise exit 1 on error')
    except subprocess.CalledProcessError:
        result = call_cli_unchecked(cmd)
        assert_failure(result.stdout.decode(), 1)
