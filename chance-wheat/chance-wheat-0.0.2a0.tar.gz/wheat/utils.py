#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: wheat/utils.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 14.11.2017
import os

from wheat.constant import PACKAGE_VERSION


def directories_to_create(project_name):
    """Generate a list of directories to be created

    Args:
        project_name: a str as the project name

    Return:
        a list of str as the directories to be created
    """
    return [
        project_name,
        os.path.join(project_name, project_name),
        os.path.join(project_name, 'tests'),
        os.path.join(project_name, project_name, 'conf'),
        os.path.join(project_name, 'tests', 'unit'),
        os.path.join(project_name, 'tests', 'integration'),
        os.path.join(project_name, 'tests', 'functional'),
        os.path.join(project_name, project_name, 'models')
    ]


def files_to_generate(project_name):
    """Generate a list of files to be genereated

    Args:
        project_name: a str as the project name

    Return:
        a list of str as the files to be generated
    """
    return [
        os.path.join(project_name, 'setup.py'),
        os.path.join(project_name, 'setup.cfg'),
        os.path.join(project_name, '.gitignore'),
        os.path.join(project_name, 'README.md'),
        os.path.join(project_name, project_name, 'main.py'),
        os.path.join(project_name, project_name, 'constant.py'),
        os.path.join(project_name, project_name, '__init__.py'),
        os.path.join(project_name, project_name, 'models', '__init__.py'),
        os.path.join(
            project_name, project_name, 'models',
            '{0}_statistics.py'.format(project_name)
        ),
        os.path.join(project_name, 'tests', 'unit', '__init__.py'),
        os.path.join(project_name, 'tests', 'unit', 'test_main_unit.py'),
        os.path.join(project_name, 'tests', 'integration', '__init__.py'),
        os.path.join(
            project_name, 'tests', 'integration', 'test_main_integration.py'
        ),
        os.path.join(
            project_name, 'tests', 'integration',
            'test_{0}_statistics.py'.format(project_name)
        ),
        os.path.join(project_name, 'tests', 'functional', '__init__.py'),
        os.path.join(
            project_name, 'tests', 'functional', 'test_main_functional.py'
        ),
        os.path.join(
            project_name, project_name, 'conf', 'test_service_config.yml'
        ),
        os.path.join(
            project_name, project_name, 'conf', 'logging.yaml'
        ),
        os.path.join(
            project_name, project_name, 'conf', '__init__.py'
        ),
        os.path.join(
            project_name, 'tests', 'integration', 'test_service.py'
        ),
    ]


def generate_match_rules(project_name, files):
    """Generate template match rules

    Args:
        project_name: a str as the project name
        files: a list of str

    Return:
        a dict as {file: template_name}
    """
    match_rule = {
        f: '.'.join([os.path.basename(f).lstrip('.'), 'template'])
        for f in files if 'statistics' not in f
    }
    match_rule[
        os.path.join(
            project_name, project_name, 'models',
            '_'.join([project_name, 'statistics.py'])
        )
    ] = 'statistics.py.template'
    match_rule[
        os.path.join(
            project_name, 'tests', 'integration',
            '_'.join(['test', project_name, 'statistics.py'])
        )
    ] = 'test_statistics.py.template'
    return match_rule


def generate_other_requirements():
    """Generate other requirements according to packages

    Return:
        a str
    """
    return ',\n        '.join(
        [
            ''.join(
                ['\'', package, '>=', version, '\'']
            ) for package, version in PACKAGE_VERSION.iteritems()
        ]
    )
