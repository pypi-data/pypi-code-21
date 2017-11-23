"""
Unit tests for ..gdal_build_debug/config_test_fns.py
"""

from gdal_build_debug.config_test_fns import \
    style_results, get_pass, get_success, get_failure, \
    regex_test, default_test, check_result, \
    main, make_test  # ,default_filter,
from .fixtures.line_endings_that_should_fail import \
    line_endings_that_should_fail
from .fixtures.line_endings_that_should_pass import \
    line_endings_that_should_pass
import pytest
import re
import os

__location__ = os.path.realpath(
    os.path.join(
        os.getcwd(),
        os.path.dirname(__file__)
    )
)


def test_style_results():
    results = {'foo': [(1, ('success', (0, 1)), 'bar', True)]}
    assert style_results(results)
    results = {'foo': [(1, ('failure', (0, 1)), 'bar', True)]}
    assert not style_results(results)
    results = {'foo': [(1, ('failure', (0, 1)), 'bar', False)]}
    assert not style_results(results)
    results = {'foo': [(1, ('success', (0, 1)), 'bar', False)]}
    assert style_results(results)
    results = {'foo': [(1, ('pass', (0, 1)), 'bar', False)]}
    assert style_results(results)
    results = {'foo': [(1, (None, None), 'bar', False)]}
    assert style_results(results)
    results = {'foo': [(1, (None, None), 'bar', True)]}
    assert style_results(results)


def test_get_group():
    match = re.match('abc:\s*(1)', 'abc: 1')
    assert get_pass(match) == (None, None)
    assert get_success(match)
    assert not get_failure(match)
    match = re.match('abc: (foo)?(?P<success>1)', 'abc: 1')
    assert get_pass(match) == (None, None)
    assert get_success(match)
    assert get_failure(match)  # faiure looks at group 2
    assert regex_test('pass', match)
    assert regex_test('pass', match)[0] == 'success'
    match = re.match('abc: (foo)?(?P<failure>1)', 'abc: 1')
    assert get_pass(match) == (None, None)
    assert not get_success(match)
    assert get_failure(match)


def test_check_results():
    data = [(1, ('success', (0, 1)), 'bar', True)]
    assert check_result(data)
    data = [
        (1, ('success', (0, 1)), 'bar', True),
        (2, ('success', (1, 2)), 'bar', True)
    ]
    assert check_result(data)
    data = [
        (1, ('success', (0, 1)), 'bar', True),
        (2, ('failure', (1, 2)), 'bar', True)
    ]
    assert not check_result(data)
    data = [
        (1, ('success', (0, 1)), 'bar', True),
        (2, ('failure', (1, 2)), 'bar', True)
    ]
    assert not check_result(data)
    data = [
        (1, ('success', (0, 1)), 'bar', True),
        (2, ('failure', (1, 2)), 'bar', False)
    ]
    assert check_result(data)
    assert check_result(data[::-1])


def response_obj_assertions(resp_obj):
    print(resp_obj)
    assert type(resp_obj) is tuple
    assert len(resp_obj) == 2
    # success, indexes = resp_obj
    # assert type(line_num) is int
    check_success, indexes = resp_obj
    assert type(check_success) is str or check_success is None
    assert indexes is None or \
        type(indexes[0]) is int and type(indexes[1]) is int


@pytest.mark.parametrize('data', line_endings_that_should_pass)
def test_default_test_fn_returns_true(data):
    resp_obj = default_test(data)
    response_obj_assertions(resp_obj)
    assert resp_obj[0] == 'success'


@pytest.mark.parametrize('data', line_endings_that_should_fail)
def test_default_test_fn_returns_false(data):
    resp_obj = default_test(data)
    response_obj_assertions(resp_obj)
    assert resp_obj[0] == 'failure'


@pytest.mark.parametrize('present', (True, False))
def test_make_test(present):
    _test = make_test('foo', present)
    expected = 'success' if present else 'failure'
    assert _test('yes ok enabled')[0] == expected
    expected = 'failure' if present else 'success'
    assert _test('no nope not this one disabled')[0] == expected


@pytest.mark.parametrize('params', (
    (['json'], [], []),
    ([], ['pdf'], []),
    ([], ['mongodb'], []),
    ([], [], ['postgresql:::(no)']),
    (['json', 'MRF'], [], [])
    )
)
def test_main_passes(params):
    with open(__location__ + '/fixtures/configure.log') as log_file:
        log = log_file.read()
    assert main(log, *params)


@pytest.mark.parametrize('params', (
    (['pdf'], [], []),
    (['postgresql'], [], []),
    ([], [], ['postgresql:::(yes)|(no)'])
    )
)
def test_main_fails(params):
    with open(__location__ + '/fixtures/configure.log') as log_file:
        log = log_file.read()
    assert not main(log, *params)
