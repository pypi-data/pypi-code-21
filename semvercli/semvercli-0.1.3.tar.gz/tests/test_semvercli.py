#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `semvercli` package."""


import unittest
from click.testing import CliRunner

from semvercli import semvercli
from semvercli import cli


class TestSemvercli(unittest.TestCase):
    """Tests for `semvercli` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_command_line_interface(self):
        """Test the CLI."""
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        # assert 'semvercli.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output

        bump_major_result = runner.invoke(cli.main, ['bump', 'major', '0.2.3'])
        assert bump_major_result.exit_code == 0
        assert '1.0.0' in bump_major_result.output

        bump_minor_result = runner.invoke(cli.main, ['bump', 'minor', '0.2.3'])
        assert bump_minor_result.exit_code == 0
        assert '0.3.0' in bump_minor_result.output

        bump_patch_result = runner.invoke(cli.main, ['bump', 'patch', '0.2.3'])
        assert bump_patch_result.exit_code == 0
        assert '0.2.4' in bump_patch_result.output
