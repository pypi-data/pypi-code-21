import os

import betamax
import click
import pytest

from labelord import web_support
from tests_unit.conftest import invoker


with betamax.Betamax.configure() as config:
    config.cassette_library_dir = invoker.cassette()
    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')
    if 'GITHUB_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'once'
    else:
        token = invoker.token_true()
        config.default_cassette_options['record_mode'] = 'once'
    config.define_cassette_placeholder('<TOKEN>', token)

def test_set_config():
    result = ''
    if (("LABELORD_CONFIG" in os.environ) == False):
        result = web_support.set_config()
    assert  result == 'config.cfg'

def test_get_config_repos():
    repos = web_support.get_config_repos( invoker.configs() + invoker.real_config() )
    assert repos == invoker.target_repos()

def test_get_tkn():
    token = web_support.get_tkn(  invoker.configs() + invoker.real_config() )
    assert token == invoker.token_true()

def test_get_tkn_bad(capsys):
    with pytest.raises(SystemExit):
        web_support.get_tkn(invoker.configs() + invoker.bad_config())
        out, err = capsys.readouterr()
        assert click.unstyle(err.strip()) == 'No repositories specification has been found'

def test_get_secret():
    secret = web_support.get_secret(  invoker.configs() + invoker.real_config() )
    assert secret == invoker.secret_true()

def test_get_tkn_bad(capsys):
    with pytest.raises(SystemExit):
        secret = web_support.get_secret(invoker.configs() + invoker.bad_config())
        out, err = capsys.readouterr()
        assert click.unstyle(err.strip()) == 'No webhook secret has been provided'

def test_session_labels(betamax_parametrized_session):
    repos = invoker.target_repos()
    assert web_support.create_label('label123', '#FF00FF', repos, betamax_parametrized_session, origin = repos[0]) == '200'
    assert web_support.edit_label('label123', 'label321', '#FF00FF', repos, betamax_parametrized_session, origin=repos[0]) == '200'
    assert web_support.delete_label('label321', repos, betamax_parametrized_session, origin=repos[0]) == '200'

def test_check_signature():
    assert web_support.check_signature( invoker.secret_true(), request = invoker.request() ) == False
    assert web_support.get_signature(request = invoker.request()) == invoker.request().headers['X-Hub-Signature']