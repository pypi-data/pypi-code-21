import betamax
import os
import pytest
from click.testing import CliRunner

from labelord import web, cli
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

def test_create_app():
    """Test the app creating and its name"""
    app = web.create_app()
    assert app.name == 'labelord.web'

@pytest.fixture
def testapp(betamax_parametrized_session):
    from labelord import app
    app.config['TESTING'] = True
    app.my_config = invoker.configs() + invoker.real_config()
    app.my_session = betamax_parametrized_session
    return app.test_client()

def test_welcome(testapp):
    assert 'Welcome!' in testapp.get('/').data.decode('utf-8')

@pytest.mark.parametrize('repo', invoker.target_repos())
def test_repos(testapp, repo):
    assert repo in testapp.get('/').data.decode('utf-8')

def test_get_info():
    assert web.get_info( invoker.target_repos() ) == invoker.info()

def test_post_webhook_unauthorized(testapp):
    result = testapp.post('/')
    assert result.data.decode('utf-8') == 'UNAUTHORIZED'

@pytest.mark.parametrize('event', ['label_created', 'label_edited', 'label_deleted'])
def test_post_webhook(testapp, event):
    header = ''
    if( event == 'label_created'):
        header = invoker.header_created()
    elif( event == 'label_deleted' ):
        header = invoker.header_deleted()
    elif( event == 'label_edited' ):
        header = invoker.header_edited()

    result = testapp.post('/',
                          data=invoker.load_data( event ),
                          headers= header )
    assert result.data.decode('utf-8') == '200'

def test_run_server_help(testapp):
    """Test the list_repos output and exit code"""
    runner = CliRunner()
    result = runner.invoke(cli, ['-c', invoker.configs() + invoker.real_config(), 'run_server', '--help'], obj={'app': testapp})
    assert 'Show this message and exit.' in result.output

def test_repo_link():
    """Test the converting repo to link"""
    assert web.repo_link('Test') == 'https://github.com/Test'