import os

import betamax
import pytest

from labelord import cli
from tests_unit.conftest import invoker
from click.testing import CliRunner

with betamax.Betamax.configure() as config:
    config.cassette_library_dir = invoker.cassette()
    token = os.environ.get('GITHUB_TOKEN', '<TOKEN>')
    if 'GITHUB_TOKEN' in os.environ:
        config.default_cassette_options['record_mode'] = 'once'
    else:
        token = invoker.token_true()
        config.default_cassette_options['record_mode'] = 'once'
    config.define_cassette_placeholder('<TOKEN>', token)

def test_listed_repos(betamax_parametrized_session):
    """Test the list_repos output and exit code"""
    runner = CliRunner()
    betamax_parametrized_session.headers.update({'Accept-Encoding': 'identity'})
    result = runner.invoke(cli, ['-c', invoker.configs() + invoker.real_config(), 'list_repos'], obj={'session': betamax_parametrized_session} )
    assert result.output.split('\n') == invoker.repos()
    assert result.exit_code == 0

def test_listed_labels(betamax_parametrized_session):
    """Test the list labels output and exit code"""
    runner = CliRunner()
    betamax_parametrized_session.headers.update({'Accept-Encoding': 'identity'})
    result = runner.invoke(cli, ['-c', invoker.configs() + invoker.real_config(), 'list_labels', 'HalfDeadPie/LoRa-FIIT'], obj={'session': betamax_parametrized_session} )
    assert result.output.split('\n') == invoker.repo_labels()
    assert result.exit_code == 0

@pytest.mark.parametrize('repo', ['MrFakeMan/AndHisFakeRepo', 'HalfDeadPie/NotFound', 'BlaBlaBla'])
def test_listed_labels_not_found(betamax_parametrized_session, repo):
    """Test the list labels output and exit code for 404"""
    runner = CliRunner()
    betamax_parametrized_session.headers.update({'Accept-Encoding': 'identity'})
    result = runner.invoke(cli, ['-c', invoker.configs() + invoker.real_config(), 'list_labels', repo], obj={'session': betamax_parametrized_session} )
    assert result.output == 'GitHub: ERROR 404 - Not Found\n'
    assert result.exit_code == 5

def test_run(betamax_parametrized_session):
    """Test the run dry function"""
    runner = CliRunner()
    betamax_parametrized_session.headers.update({'Accept-Encoding': 'identity'})
    result = runner.invoke(cli, ['-c', invoker.configs() + invoker.real_config(), 'run', '-v', '-d', 'update'], obj={'session': betamax_parametrized_session} )
    assert result.output.split('\n') == invoker.run_dry()
    assert result.exit_code == 0







