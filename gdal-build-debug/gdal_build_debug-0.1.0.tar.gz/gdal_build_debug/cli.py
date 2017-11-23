#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Console script for gdal_build_debug."""

import os
# import subprocess
import click
import json
import logging
from gdal_build_debug.config_test_fns import main as test_config_log
from gdal_build_debug.cli_test_fns import main as test_formats
from gdal_build_debug.cli_test_fns import test_version_is

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
debug = logger.debug


__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def load(json_file):
    "load pickled sets of normalized format codes"
    with open(os.path.join(__location__, 'json', json_file), 'r') as _json:
        return json.load(_json)


@click.group('test-gdal-build')
@click.option('--root', help='root path for relative paths', default='')
@click.option(
    '--debug', is_flag=True, help='whether to include debug logs in output'
    )
@click.pass_context
def main(ctx, root, debug):
    'A command-line utility for testing your GDAL configuration and build.'
    if not ctx.obj:
        ctx.obj = {}
    ctx.obj['root'] = root
    ctx.obj['level'] = logging.DEBUG if debug else logging.ERROR


@main.command(
    'config',
    short_help='test package inclusion in the output of gdal/configure \
    [options] --cache-file'
    )
@click.option(
    '--path-to-config-log', 'config_log_path', default='./configure.log',
    envvar='PATH_TO_GDAL_CONFIG_LOG', type=click.Path(),
    help='a relative or absolute path to the logged output of gdal/configure'
)
@click.option(
    '--with', 'include', type=str, envvar='TEST_GDAL_CONFIGURED_WITH',
    multiple=True,
    help='Searches the output of gdal/configure to ensure packages are \
     present.', metavar='<package...>'
     )
@click.option(
    '--without', 'exclude', type=str, envvar='TEST_GDAL_CONFIGURED_WITHOUT',
    multiple=True, help='Searches the output of gdal/configure to ensure \
    packages are absent', metavar='<package...>'
    )
@click.option(
    '--search', 'searches', type=str, envvar='TEST_GDAL_CONFIG_SEARCHES',
    multiple=True, metavar='<regex...>',
    help='''
    case-insensitive python regex searches of the form:
      "match_line:::(success)|(failure)|(pass)"
    match_line: a name that if matched will run the test

    ::: an optional separator to treat 1 as a --with option

    success The match group that indicates the test succeeded ( \
    optionally named with success)

    failure: The match group that indicates the test failes ( \
    optionally named fail or failure)

    pass: the match group that indicates the test was not passing but \
    not fatal (optionally named pass)

    Gotchas: must be quoted. Success overrides failure overrides pass; named \
    groups override group order.
    '''
    )
@click.pass_context
def config(ctx, config_log_path, include, exclude, searches):
    '''
    Tests the the output of gdal/configure for inclusion/exclusion of  \
    dependencies, and supports custom regex-based testing

    EXAMPLES:\n
      # The command must have a reference to the output of gdal/configure:\t
      # any of \n
      test-gdal-build --root="path/to/gdal/directory" config [...]\t\t
      PATH_TO_GDAL_CONFIG_LOG="..." test-gdal-build config [...]\t\t
      test-gdal-build test --path-to-config-log="..." [...]\n
      # search the configure output for included/excluded packages\n
      test-gdal-build --with foo --with bar --without baz\n
      # or\n
      TEST_GDAL_CONFIGURED_WITH="foo bar"\t\t\t\t
      TEST_GDAL_CONFIGURED_WITHOUT="baz"\t\t\t\t
      test-gdal-build config\n
      # use custom regex to search the configuration log \t\t\t
      # (ironically not gdal/config.log)\n
      # run case-insensitive tests on lines including the search prefix\t\t
      test-gdal-build config --search postgis:::(yes)|(no)|(internal)\t\t\t
      test-gdal-build config --search postgis:::(?P<fail>no)|(?P<success>yes)\t
      # or test every line\t\t\t\t\t\t\t
      test-gdal-build config --search "postgis\.\.\.\s(yes)|(no)|(internal)"
    '''
    if ctx.obj['root']:
        config_log_path = os.path.join(ctx.obj['root'], config_log_path)
    debug(''.join(map(str, [include, exclude])))
    with open(config_log_path) as config_log_file:
        config_log = config_log_file.read()
        tests_passed = test_config_log(
            config_log,
            include,
            exclude,
            searches,
            level=ctx.obj['level']
        )
        if not tests_passed:
            os._exit(1)


@main.command(short_help='tests for the gdal command line interface')
@click.option(
    '--with', 'include', multiple=True, type=str,
    default=[], envvar='TEST_GDAL_CLI_INCLUDES', metavar='<format...>',
    help='checks a format is not present in gdal or ogr'
    )
@click.option(
    '--without', 'exclude', multiple=True, type=str,
    default=[], envvar='TEST_GDAL_CLI_EXCLUDES', metavar='<format...>',
    help='checks a format is not present in gdal or ogr'
    )
@click.option(
    '--version-is', 'version_is', type=str,
    help="Tests whether the cli version is correct via regex"
    )
@click.pass_context
def cli(ctx, include, exclude, version_is):
    """
    Tests the inclusion/exclusion of formats from the gdal command-line \
    interface and installed version of gdal.

    EXAMPLES:\n
      # test the inclusion / exclusion of multiple gdal & ogr formats\n
      test-gdal-build cli --with spatialite --with pdf\t\t\t
      test-gdal-build cli --without geojson --without georss\n
      # For large or iterative tests, store the in/exclusions in environment\t
      # variables\n
      TEST_GDAL_CLI_EXCLUDES="geojson georss"\t\t\t\t\t
      TEST_GDAL_CLI_INCLUDES="spatialite pdf"\t\t\t\t\t
      test-gdal-build cli
    """
    # note click strips unescaped whitespace, including newlines. Escaping a
    # newline \n seems to block stripping the of the invisible newline.
    # Using \ts to pad out the 80-char limit seems to work best.
    tests_passed = True
    if include or exclude:
        for fmt in set(include).union(exclude).difference(ogr.union(gdal)):
            msg = fmt + ' is not a recognized gdal/ogr format'
            click.echo(click.style(msg, fg='yellow'))
        tests_passed &= test_formats(
            ogr_include=ogr.intersection(include),
            ogr_exclude=ogr.intersection(exclude),
            gdal_exclude=gdal.intersection(exclude),
            gdal_include=gdal.intersection(include),
            level=ctx.obj['level']
        )
    if version_is:
        tests_passed &= test_version_is(version_is)
    if not tests_passed:
        os._exit(1)


ogr = set(load('ogr_formats_set.json'))
gdal = set(load('gdal_formats_set.json'))
formats = gdal.union(ogr)
dependencies = set(load('dependencies_set.json'))


def __main__():
    # global ogr, gdal, formats, dependencies
    main(obj={})


if __name__ == "__main__":
    __main__()
