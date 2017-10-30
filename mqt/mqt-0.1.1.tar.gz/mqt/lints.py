#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import subprocess
from os.path import join
from os.path import isfile
import pylint.lint

try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

from . import getaddons
from . import helpers
from .getaddons import get_modules_changed
from .git_run import GitRun
from .mqt import Mqt

mqt = Mqt()


class Lints(Mqt):
    """This class runs `pylint` with plugins and special configuration files.
    Use the following types of pylint configuration files:
    
        1. Global
        2. Pull request
        3. Version
        4. Beta
    
    1. Global
    
        Used to check enabled messages on this file in all modules of the project.
        The result affect your build status. **File name:** `pylint.cfg`
    
    2. Pull request
    
        Used to check enabled messages on this file just in modules changed in a
        pull request of the project. The result affects your build status. **File
        name:** `pylint_pr.cfg`
    
    3. Version Exclusions
    
        Used to disable the previously enabled messages of `global` or
        `pull request` configuration files based on `VERSION` variable environment.
        **File name:** `pylint_exclude_{VERSION}.cfg`
    
    4. Beta
    
        Used to add the previously enabled messages in `global` or `pull request`
        configuration files that you want to display, without affecting your build
        status. **File name:** `pylint_beta.cfg`
    """
    def __init__(self):
        pass


def get_sub_paths(paths):
    """Get list of subdirectories if `__init__.py` file not exists in root path
    then get subdirectories.
    
    Why? More info `Python <https://www.mail-archive.com/code-quality@python.org /msg00294.html>`_.

    :param paths: List of paths
    :return: Return list of paths with subdirectories.

    """
    subpaths = []
    for path in paths:
        if not isfile(join(path, '__init__.py')):
            subpaths.extend(
                [join(path, item)
                 for item in os.listdir(path)
                 if isfile(join(path, item, '__init__.py')) and
                 (not getaddons.is_module(join(path, item)) or
                  getaddons.is_installable_module(join(path, item)))])
        else:
            if not getaddons.is_module(path) or \
                    getaddons.is_installable_module(path):
                subpaths.append(path)
    return subpaths


def run_pylint(paths, cfg,
               beta_msgs=None,
               sys_paths=None,
               extra_params=None):
    """Execute pylint command from original python library
    
    :param paths: List of paths of python modules to check pylint
    :param cfg: String name of pylint configuration file
    :param sys_paths: List of paths to append to sys path
    :param extra_params: List of parameters extra to append
        in pylint command
    :return: Dict with python linter stats
    """
    if sys_paths is None:
        sys_paths = []
    if extra_params is None:
        extra_params = []
    if not cfg:
        cfg = join(mqt.path, 'cfg/pylint.cfg')
    sys.path.extend(sys_paths)
    cmd = ['--rcfile=' + cfg]
    cmd.extend(extra_params)
    sub_paths = get_sub_paths(paths)
    if not sub_paths:
        raise UserWarning("Python modules not found in paths"
                          " {paths} ".format(paths=paths))
    cmd.extend(sub_paths)
    pylint_res = pylint.lint.Run(cmd, exit=False)
    return pylint_res.linter.stats


def run(paths, config_file, msgs_no_count=None, sys_paths=None,
        extra_params=None):
    try:
        fname = config_file if config_file else False
        stats = run_pylint(
            list(paths),
            cfg=fname,
            sys_paths=sys_paths,
            extra_params=extra_params
        )
        count_fails = get_count_fails(stats, list(msgs_no_count))
    except UserWarning:
        count_fails = -1
    return count_fails


def get_extra_params(odoo_version):
    """Get extra pylint params by odoo version
    Transform a seudo-pylint-conf to params,
    it to overwrite base-pylint-conf values.
    Use a seudo-inherit of configuration file.
    To avoid have a 2 config files (stable and pr-conf) by each odoo-version
    Example:

        pylint_master.conf
        pylint_master_pr.conf
        pylint_90.conf
        pylint_90_pr.conf
        pylint_80.conf
        pylint_80_pr.conf
        pylint_70.conf
        pylint_70_pr.conf
        pylint_61.conf
        pylint_61_pr.conf
        ... and new future versions.

    If you need add a new conventions in all versions
    you will need change all pr files or stables files.


    With this method you can use:

        pylint_lastest.conf
        pylint_lastest_pr.conf
        pylint_disabling_70.conf <- Overwrite params of pylint_lastest*.conf
        pylint_disabling_61.conf <- Overwrite params of pylint_lastest*.conf

    If you need add a new conventions in all versions you will need change just
    pylint_lastest_pr.conf or pylint_lastest.conf, similar to inherit.

    :param odoo_version: String with name of version of odoo
    :return: List of extra pylint params
    """
    odoo_version = odoo_version.replace('.', '')
    version_cfg = join(
        mqt.path,
        'cfg/pylint_exclude_{odoo_version}.cfg'.format(
            odoo_version=odoo_version))
    params = []
    if isfile(version_cfg):
        config = ConfigParser.ConfigParser()
        config.readfp(open(version_cfg))
        for section in config.sections():
            for option, value in config.items(section):
                params.extend(['--' + option, value])
    return params


git_work_dir = mqt.BUILD_DIR if not isinstance(mqt.BUILD_DIR, list) else False
is_pull_request = mqt.PULL_REQUEST
branch_base = mqt.BRANCH

extra_params_cmd = [
    '--sys-paths', join(
        mqt.path,
        'pylint_deprecated_modules'),
    '--extra-params', '--load-plugins=pylint_odoo',
]


def get_beta_msgs():
    """Get beta msgs from beta.cfg file

    :return: List of strings with beta message names"""
    beta_cfg = join(
        mqt.path,
        'cfg/pylint_beta.cfg')
    if not isfile(beta_cfg):
        return []
    config = ConfigParser.ConfigParser()
    config.readfp(open(beta_cfg))
    return [
        msg.strip()
        for msg in config.get('MESSAGES CONTROL', 'enabled2beta').split(',')
        if msg.strip()]


version = mqt.VERSION

if not version:
    if git_work_dir:
        repo_path = join(git_work_dir, '.git')
        branch_name = GitRun(repo_path).get_branch_name()
        version = branch_name.replace('_', '-').split('-')[:1] \
            if branch_name else False
        version = version[0] if version and len(version) else None

if version:
    extra_params = get_extra_params(version)
    for extra_param in extra_params:
        extra_params_cmd.extend([
            '--extra-params', extra_param
        ])
    is_version_number = re.match(r'\d+\.\d+', version)
    if is_version_number:
        extra_params_cmd.extend([
            '--extra-params', '--valid_odoo_versions=%s' % version])
else:
    print(helpers.yellow('Undefined environment variable `VERSION`.'
                         '\nSet `VERSION` for compatibility with guidelines by version.'))

beta_msgs = get_beta_msgs()
[extra_params_cmd.extend(['--msgs-no-count', beta_msg])
 for beta_msg in beta_msgs]

# Look for an environment variable
# whose value is the name of a proper configuration file for pylint
# (this file will then be expected to be found in the 'cfg/' folder).
# If such an environment variable is not found,
# it defaults to the standard configuration file.
pylint_rcfile = join(mqt.path, 'cfg',  mqt.PYLINT_CONFIG_FILE)
# import pdb; pdb.set_trace()
count_errors = run(mqt.BUILD_DIR, pylint_rcfile)
pylint_rcfile_pr = join(mqt.path, 'cfg', "pylint_pr.cfg")

if is_pull_request and branch_base and git_work_dir:
    if branch_base != 'HEAD':
        branch_base = 'origin/' + branch_base
    modules_changed = get_modules_changed(
        git_work_dir,
        branch_base)
    if modules_changed and count_errors >= 0:
        print(helpers.green(
            'Start lint check just in modules changed'))
        modules_changed_cmd = []
        for module_changed in modules_changed:
            modules_changed_cmd.extend([
                '--path',
                module_changed,
            ])
        pr_errors = run([
                                   "--config-file=" + pylint_rcfile_pr,
                               ] + modules_changed_cmd + extra_params_cmd,
                               standalone_mode=False)
        if pr_errors:
            print(helpers.yellow(
                "Found {pr_errors} errors".format(pr_errors=pr_errors) +
                " in modules changed."
            ))
            if pr_errors < 0:
                count_errors = pr_errors
            else:
                count_errors += pr_errors
else:
    # TODO: Add git hook case in other PR
    pass
expected_errors = int(
    os.environ.get('PYLINT_EXPECTED_ERRORS', 0))

exit_status = 0
if count_errors == -1:
    print(helpers.yellow('Python modules not found'))
elif count_errors != expected_errors:
    print(helpers.red("pylint expected errors {expected_errors}, "
                      "found {number_errors}!".format(
        expected_errors=expected_errors,
        number_errors=count_errors)))
    exit_status = 1
if beta_msgs and count_errors >= 0:
    print(helpers.green(
        "\nNext checks are still in beta "
        "they won't affect your build status for now: "
        '\n' + ', '.join(sorted(beta_msgs))))


def get_count_fails(linter_stats, msgs_no_count=None):
    """Verify the dictionary statistics to get number of errors.

    :param linter_stats: Dict of type pylint.lint.Run().linter.stats
    :param msgs_no_count: List of messages that will not add to the failure count.
    :return: Integer with quantity of fails found.
    """
    return sum([
        linter_stats['by_msg'][msg]
        for msg in linter_stats['by_msg']
        if msg not in msgs_no_count])


def flake():
    """Just run Flake8 per directory"""
    status = 0
    for addon in getaddons.get_modules(os.path.abspath('.')):
        fname = join(mqt.path, 'cfg', 'flake8__init__.cfg')
        status += subprocess.call(['flake8', '--config', fname, addon])
        fname = join(mqt.path, 'cfg', 'flake8.cfg')
        status += subprocess.call(['flake8', '--config', fname, addon])

    return 0 if status == 0 else 1
