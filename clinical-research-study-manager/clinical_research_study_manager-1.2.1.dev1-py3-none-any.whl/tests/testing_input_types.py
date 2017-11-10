import datetime
from unittest.mock import patch

from research_study_manager import data_request_functions


@patch('builtins.input', lambda x: '11/1/2017')
def test_date_input():
    assert data_request_functions.get_date_info('Follow Up') == datetime.date(2017, 11, 1)


@patch('builtins.input', lambda x: '23:30')
def test_time_input():
    assert data_request_functions.get_time_info('Follow Up') == datetime.time(23, 30)


@patch('builtins.input', lambda x: '25')
def test_age_input():
    assert data_request_functions.get_info_from_user('age') == '25'


@patch('builtins.input', lambda x: 'M')
def test_sex_input():
    assert data_request_functions.get_info_from_user('sex') == 'M'


@patch('builtins.input', lambda x: 'Y')
def test_eligibility_status_input():
    assert data_request_functions.get_info_from_user('eligibility status') == 'Y'


@patch('builtins.input', lambda x: 'NA')
def test_reason_ineligible_input():
    assert data_request_functions.get_info_from_user('reason ineligible') == 'NA'


@patch('builtins.input', lambda x: 'N')
def test_enrollment_input():
    assert data_request_functions.get_info_from_user('enrollment status') == 'N'


@patch('builtins.input', lambda x: 'Declined')
def test_reason_not_enrolled_input():
    assert data_request_functions.get_info_from_user('reason not enrolled') == 'Declined'


@patch('builtins.input', lambda x: 'ABC')
def test_initials_input():
    assert data_request_functions.get_info_from_user('research assistant initials') == 'ABC'


@patch('builtins.input', lambda x: '-25')
def test_bad_age_input():
    assert data_request_functions.get_info_from_user('age') == 'Please enter a number greater than 0'


# TODO: Figure out how to test bad input since we are using a while loop for that. Is that a bad idea?


def main():
    test_date_input()
    test_time_input()
    test_sex_input()
    test_eligibility_status_input()
    test_reason_ineligible_input()
    test_enrollment_input()
    test_reason_not_enrolled_input()
    test_initials_input()


if __name__ == '__main__':
    main()
