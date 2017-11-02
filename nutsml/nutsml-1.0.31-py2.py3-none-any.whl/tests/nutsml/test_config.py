"""
.. module:: test_config
   :synopsis: Unit tests for config module
"""

import pytest

import nutsml.config as nc


def test_Config():
    cfg = nc.Config({'number': 13})
    assert cfg['number'] == 13
    assert cfg.number == 13

    cfg.name = 'Stefan'
    assert cfg['name'] == 'Stefan'
    assert cfg.name == 'Stefan'


def test_isjson():
    assert nc.Config.isjson('mydir/somefile.json')
    assert nc.Config.isjson('mydir/somefile.JSON')
    assert not nc.Config.isjson('mydir/somefile.yaml')


def test_save_load():
    cfg = nc.Config({'number': 13, 'name': 'Stefan'})

    cfg.save('tests/data/configuration.yaml')
    newcfg = nc.Config()
    loaded_cfg = newcfg.load('tests/data/configuration.yaml')
    assert newcfg.number == 13
    assert newcfg == cfg
    assert loaded_cfg == cfg

    cfg.save('tests/data/configuration.JSON')
    newcfg = nc.Config()
    newcfg.load('tests/data/configuration.JSON')
    assert newcfg.number == 13
    assert newcfg == cfg


def test_load_config():
    cfg = nc.load_config('tests/data/config.yaml')
    assert cfg.filepath == 'c:/Maet'
    assert cfg['imagesize'] == [100, 200]

    with pytest.raises(IOError) as ex:
        nc.load_config('does not exist')
    assert str(ex.value).startswith('Configuration file not found')
