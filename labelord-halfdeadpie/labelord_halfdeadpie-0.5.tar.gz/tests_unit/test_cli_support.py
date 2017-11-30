import pytest
import click

from labelord import cli_support
from labelord.cli_support import Label, is_named
from tests_unit.conftest import invoker


def create_label():
    """Test the label creating"""
    label = Label('test','black')
    assert label.n == 'test'
    assert label.c == 'black'

@pytest.mark.parametrize(['token','config'],
                         [('JustSomeRandomTokenForTesting',''),
                           (None, invoker.configs() + 'config_basic.cfg')])
def test_get_token(token, config):
    """Test the function that return the token"""
    check = cli_support.get_token(token, config)
    assert check == invoker.token()

def test_get_token_null():
    """Test the function that return None token"""
    check = cli_support.get_token(None, '')
    assert check == None

def test_check_token():
    """Test the function that exit from the application if token is none"""
    with pytest.raises(SystemExit):
        cli_support.check_token(None)


def test_authorization():
    """Test the function that set the User-Agent and authorization function to request session"""
    session = cli_support.authorization(invoker.ctx(), invoker.token())
    assert session.headers['User-Agent'] == 'Python'
    assert session.auth != None

def test_cmp_labels():
    """Test the function that compare labels"""
    a = Label('first','#000000')
    b = Label('first','#000000')
    c = Label('second', '#000000')
    d = Label('sEcOnD', '#000000')
    assert cli_support.cmp_labels(a, b)
    assert cli_support.cmp_labels(a, c) == False
    assert cli_support.same_lower_name(c, d)
    assert cli_support.different_case(c, d)

def test_is_named():
    """Test the function to check if the label is in the template"""
    label_true = Label('label1', 'FFAA00')
    label_false = Label('RandomLabel', 'FFAA00')
    template = invoker.labels()
    assert is_named(template, label_true)
    assert is_named(template, label_false) == False

def test_print_version(capsys):
    """Test the version printing"""
    cli_support.print_version(invoker.ctx(), param='', value='Value')
    out, err = capsys.readouterr()
    assert click.unstyle(out.strip()) == 'labelord, version 0.5'

def test_add_updated():
    """Test the function that add updated repo to list"""
    ctx = invoker.ctx()
    repo = 'repo123'
    cli_support.add_updated(ctx, repo)
    assert repo in ctx.obj['updated']