#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_freckles
----------------------------------

Tests for `freckles` module.
"""

from contextlib import contextmanager

import pytest
from click.testing import CliRunner

# from freckles import cli, freckles


@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')
    pass


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string
    pass

# def test_command_line_interface():
    # runner = CliRunner()
    # result = runner.invoke(cli.cli)
    # help_result = runner.invoke(cli.cli, ['--help'])
    # assert help_result.exit_code == 0
    # assert 'Show this message and exit.' in help_result.output
