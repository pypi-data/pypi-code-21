# -*- coding: utf-8 -*-
'''
Functions supporting testing of the config log
'''

import re
import click
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)
debug = logger.debug


def check_result(data):
    '''
    Returns a boolean whether the test passed or encountered fatal failures.
    Args:
        data: a list of tuples of the form (_, (str result, _), _, bool
        essential)
    Returns:
        A boolean value whether all tests of essential lines or all test of
            non-essential lines succeeded
    '''
    essential_success = True
    non_essential_success = False
    essential_lines_present = False
    for _, (result, _), _, essential in data:
        if essential:
            essential_success &= result != 'failure'
            if not essential_lines_present:
                essential_lines_present = True
        elif not essential_lines_present:
            non_essential_success |= result != 'failure'
    if essential_lines_present:
        return essential_success
    else:
        return non_essential_success


def style_result(line_num, test_output, line, essential):
    '''
    echoes lines related to a test result with ANSI colors
    Args:
        line_num: 1-indexed int
        test_output: a tuple (str or NoneType , (int start, int end))
        line: the entire str line that was tested
        essential: boolean value of whether the line is essential to package
        inclusion
    Returns:
        None
    '''
    test_result, indexes = test_output
    final = ''
    color = 'white'
    start = 0
    end = len(line)
    logger.debug('style_result input data ' + str(test_output) + str(line_num))
    if test_result[0] == 'passes':
        start, end = indexes
        color = 'green'
    elif test_result[0] == 'failure':
        start, end = indexes
        color = 'red'
    else:
        color = 'white'
    final = '{}\t{}{}{}'.format(
        line_num,
        click.style(line[0:start], fg='white'),
        click.style(line[start:end], fg=color),
        click.style(line[end:len(line)], fg='white')
    )
    click.echo(final)


def style_results(results, quiet=False):
    '''
    Echoes styled results to the command line and returns a boolean, whether
    all tests passed.
    Args:
        results: a dict mapping search name to a list of tuples representing
        tested lines
    Returns:
        a boolean, whether all tests passed
    '''
    all_clear = True
    if not quiet:
        click.echo('{:-^80}'.format('configuration tests'))
    for result in sorted(results.items(), key=lambda item: item[0].lower()):
        key, data = result
        if check_result(data):
            if not quiet:
                if len(data) > 0:
                    click.echo(
                        '{:31}:  {}'.format(
                            key,
                            click.style('✓', fg='green')
                        )
                    )
        else:
            all_clear = False
            if not quiet:
                click.echo(
                    '{:31}:  {}'.format(
                        key,
                        click.style('×', fg='red')
                    )
                )
                for line in data:
                    style_result(*line)
    return all_clear


def get_group(match, *names):
    '''
    Returns the first resolved regex match group from the given identifiers
    Args:
        match: a re.match object
        names: multiple int or str group indexes/names, in the order they
        should be tried
    Returns:
        a tuple of the start and end indexes of the match group
    '''
    logger.debug(match)
    if match:
        for name in names:
            try:
                return match.group(name) and (
                    match.start(name), match.end(name)
                )
            except IndexError:
                continue  # try the next name
        else:
            return  # return None if no recognized name present


# unit testing material
# match = re.match('abc: (?P<a>1)', 'abc: 1')
# assert not get_pass(match)
# assert get_success(match)
# assert not get_failure(match)


def get_success(match):
    'Returns a matched success condition or None'
    success = get_group(match, 'success', 1)
    return ('success', success) if success else None


def get_pass(match):
    '''
    Returns a matched pass condition or None.
    contains no group index since as an optional value, it must be explicityly
    named
    '''
    acceptable = get_group(match, 'pass')
    return ('pass', acceptable) if acceptable else (None, None)


def get_failure(match):
    '''
    Returns a matched failure condition or None.
    '''
    failure = get_group(match, 'fail', 'failure', 2)
    return ('failure', failure) if failure else None


def default_filter(query, line):
    '''
    Returns a string to test iff the query matches the line
    '''
    if query in line.lower():
        split = re.split(':|(\.\.\.)', line)
        #                       ^ the default line / result separator
        return split[-1]


def default_test(response, present=True, accept_internal=True):
    '''
    Returns a test response tuple based on a given response string
    '''
    def resolve(result):
        expected = 'present' if present else 'absent'
        passes_test = result == expected
        logger.debug('{}, expected {}'.format(result, expected))
        return 'success' if passes_test else 'failure'

    def make_answer(answer):
        return (resolve(answer), (0, len(response)))
    failing_answers = ['no', 'disabled', 'not found']
    if any([a in response for a in ['yes', 'enabled', 'none needed']]):
        return make_answer('present')
    elif not any([a in response for a in failing_answers]):
        if accept_internal:
            return make_answer('present')
        else:
            return make_answer('present')
    else:
        return make_answer('absent')


def regex_filter(query, line):
    '''
    Returns a regex match or None
    '''
    return query.search(line)


def regex_test(query, to_test):
    match = query.search(to_test) if type(to_test) is str else to_test
    # logger.debug('success: {}'.format(get_success(match)))
    # logger.debug('failure: {}'.format(get_failure(match)))
    return get_success(match) or get_failure(match) or get_pass(match)

# unit testing material:
# def check_response(resp_obj):
#  assert type(resp_obj) is tuple;
#  assert len(resp_obj) == 4
#  line_num, test_resp, line, is_essential = resp_obj
#  assert type(line_num) is int
#  assert type(test_success) is str or test_success is None
#  test_success, (start, end) = test_resp
#  assert start is None or type(start) is int
#  assert end is None or type(end) is int
#  assert type(line) is str
#  assert type(is_essential) is bool


def is_regex_str(query):
    'a naive check of whether a str is intended to be regex'
    return any([i in query for i in '[()]\\'])


def make_test(query, present=True, accept_internal=True):
    '''
    Returns a test function of whether a passed line succeeded or not
    '''
    query = query.partition(':::')
    query = query[2] or query[0]
    if is_regex_str(query):
        regex = re.compile(query)

        def test(line):
            return regex_test(regex, line)
    else:
        def test(line):
            return default_test(line, present, accept_internal)
    return test


def make_search(query):
    'returns a filter function based on a query'
    if type(query) is not str:
        raise ValueError('query is not a string')
    # the search for matching lines
    query = query.split(':::')[0]
    if is_regex_str(query):
        regex = re.complile(query, flags=re.I)

        def search(line):
            return regex_filter(regex, line)
    else:
        def search(line):
            return default_filter(query, line)
    return search


def check_lines(filter_fn, test_fn, config_log_lines, essential=False):
    '''
    Pipes all lines through the filter- and test_fns, returns the resulting
    list of tuples
    '''
    results = []
    for index, line in config_log_lines:
        match = filter_fn(line)
        if match:
            logger.debug('{} -> {}'.format(line, match))
            results.append(
                (index + 1, test_fn(match), line, essential)
            )
    return results


def parse_query(query, query_type):
    search_fn = make_search(query)
    if query_type == 'regex':
        return (query, search_fn, make_test(query))
    else:
        formatted_query = '{} {}'.format(query, query_type)
        is_present = query_type == 'present'
        return formatted_query, search_fn, make_test(query, present=is_present)


def main(
    config_log, lib_present, lib_absent, searches, accept_internal=True,
    level=logging.INFO
):
    '''
    Given a string config_log, and an iterable of queries (either supported
    libraries or custom searches), runs the full 'test suite'
    '''
    ch.setLevel(level)
    lines = config_log.split('\n')
    lib_lines, support_lines = [], []
    essential_line = False
    for line_index, line in enumerate(lines):
        if 'GDAL is now configured' in line:
            essential_line = True
        if essential_line:
            support_lines.append((line_index, line))
        else:
            lib_lines.append((line_index, line))
    results = {}
    queries = [parse_query(query.lower(), 'present') for query in lib_present]
    queries += [parse_query(query, 'regex') for query in searches]
    queries += [parse_query(query.lower(), 'absent') for query in lib_absent]
    for _query, search_fn, test_fn in queries:
        results[_query] = check_lines(search_fn, test_fn, support_lines, True)
        results[_query] += check_lines(search_fn, test_fn, lib_lines, False)
    return style_results(results)
