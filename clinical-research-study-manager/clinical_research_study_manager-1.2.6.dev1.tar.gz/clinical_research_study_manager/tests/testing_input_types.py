import datetime
import unittest
from unittest import TestCase
from unittest.mock import patch

from clinical_research_study_manager import data_request_functions_test as data_request_functions
from clinical_research_study_manager import exceptions_test as exceptions


class TestValidUserInput(TestCase):
    @patch('builtins.input', lambda x: '11/1/2017')
    def test_date_input(self):
        self.assertEqual(data_request_functions.get_date_info('Follow Up'), datetime.date(2017, 11, 1))

    @patch('builtins.input', lambda x: '23:30')
    def test_time_input(self):
        self.assertEqual(data_request_functions.get_time_info('Follow Up'), datetime.time(23, 30))

    @patch('builtins.input', lambda x: '25')
    def test_age_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('age'), '25')

    @patch('builtins.input', lambda x: 'M')
    def test_sex_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('sex'), 'M')

    @patch('builtins.input', lambda x: 'Y')
    def test_eligibility_status_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('eligibility status'), 'Y')

    @patch('builtins.input', lambda x: 'NA')
    def test_reason_ineligible_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('reason ineligible'), 'NA')

    @patch('builtins.input', lambda x: 'N')
    def test_enrollment_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('enrollment status'), 'N')

    @patch('builtins.input', lambda x: 'Declined')
    def test_reason_not_enrolled_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('reason not enrolled'), 'Declined')

    @patch('builtins.input', lambda x: 'ABC')
    def test_initials_input(self):
        self.assertEqual(data_request_functions.get_info_from_user('research assistant initials'), 'ABC')


class TestInvalidUserInput(unittest.TestCase):
    @patch('builtins.input', lambda x: '-25')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_info_from_user('age')

    @patch('builtins.input', lambda x: 'ABC')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_info_from_user('sex')

    @patch('builtins.input', lambda x: 'ABC')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_info_from_user('eligibility status')

    @patch('builtins.input', lambda x: '-ABC')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_info_from_user('enrollment status')

    @patch('builtins.input', lambda x: '-1/1/2017')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_date_info('Follow Up')

    @patch('builtins.input', lambda x: '-11:30')
    def test_bad_age_input(self):
        with self.assertRaises(exceptions.InputException):
            data_request_functions.get_time_info('Follow Up')


# TODO: Figure out how to test bad input since we are using a while loop for that. Is that a bad idea?
# TODO: Figure out how to call test using setup.py


def run_tests():
    main()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
