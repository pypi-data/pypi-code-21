# -*- coding: utf-8 -*-
# bypass: Copyright (C) 2017, Richard Berry

import os

import bypass as bp
from click.testing import CliRunner
import pytest


@pytest.fixture(autouse=True)
def patch_config_file(monkeypatch):
    if os.path.isfile(bp.BYPASS_CONFIG):
        monkeypatch.setattr('bypass.BYPASS_CONFIG', None)


# -- test_bypass_cli_command_gen

def get_params_test_bypass_cli_command_gen():
    mock1_kwargs = {'length': None, 'lowercase': True,
                    'uppercase': True, 'digits': True,
                    'additional': None}
    params = (
        ([],
         mock1_kwargs),
        (['--length', '25'],
         {**mock1_kwargs, 'length': 25}),
        (['--additional', '!'],
         {**mock1_kwargs, 'additional': '!'}),
        (['--no-lowercase'],
         {**mock1_kwargs, 'lowercase': False}),
        (['--no-uppercase'],
         {**mock1_kwargs, 'uppercase': False}),
        (['--no-digits'],
         {**mock1_kwargs, 'digits': False}),
    )
    ids = ('No CLI arguments',
           'CLI argument: --length',
           'CLI argument: --additional',
           'CLI argument: --no-lowercase',
           'CLI argument: --no-uppercase',
           'CLI argument: --no-digits',)

    return {'params': params, 'ids': ids}


@pytest.fixture(**get_params_test_bypass_cli_command_gen())
def params_test_bypass_cli_command_gen(request):
    return request.param


@pytest.mark.cli
def test_bypass_cli_command_gen(mocker,
                                params_test_bypass_cli_command_gen):
    p = params_test_bypass_cli_command_gen
    cli_args = p[0]
    mock1_kwargs = p[1]

    mocker.patch('bypass.check_init')
    mocker.patch('bypass.gen_pass')
    bp.gen_pass.side_effect = ['test_password']
    mocker.patch('bypass.update_credential')

    runner = CliRunner()
    result = runner.invoke(bp.gen, ['test_entry'] + cli_args, obj={})

    assert bp.check_init.call_count == 1
    assert bp.gen_pass.call_count == 1
    assert bp.update_credential.call_count == 1

    bp.gen_pass.assert_called_with(**mock1_kwargs)
