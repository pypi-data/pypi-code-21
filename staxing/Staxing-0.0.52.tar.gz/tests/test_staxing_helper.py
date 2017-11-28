"""Staxing test files - Helper."""

import os
import datetime
import logging
import pytest
import time
import unittest

from random import randint
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.ui import WebDriverWait
from staxing.assignment import Assignment
from staxing.helper import Helper, Teacher, Student, Admin, ContentQA, User

__version__ = '0.0.10'
TESTS = os.getenv(
    'CASELIST',
    str([
        101, 102, 103, 104, 105, 106,
        201, 202, 203, 204, 205, 206, 207, 208,
        301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 315
        # 401,
        # 501,
        # 601,
        # 701,
        # 801,
    ])
)
LOGGER.setLevel(logging.WARNING)


class TestStaxingHelper(unittest.TestCase):
    """Staxing case tests for Helper."""

    def setUp(self):
        """Pretest settings."""
        self.helper = Helper()

    def tearDown(self):
        """Test destructor."""
        try:
            self.helper.delete()
        except:
            pass

    @pytest.mark.skipif(str(101) not in TESTS, reason='Excluded')
    def test_helper_set_window_size_101(self):
        """Set the browser window size."""
        self.helper.set_window_size(1300, 700)
        new_size = {'width': 1300, 'height': 700}
        assert(self.helper.driver.get_window_size() == new_size), \
            'Window not resized: %s' % str(new_size)
        self.helper.set_window_size(200, 200)
        new_size = {'width': 200, 'height': 200}
        self.helper.set_window_size(maximize=True)
        assert(self.helper.driver.get_window_size() != new_size), \
            'Window not maximized: %s' % str(new_size)

    @pytest.mark.skipif(str(102) not in TESTS, reason='Excluded')
    def test_helper_set_new_wait_time_102(self):
        """Change the wait time."""
        old_wait = self.helper.wait_time
        self.helper.change_wait_time(5)
        new_wait = self.helper.wait_time
        assert(new_wait == 5), 'Wait time not changed: %s' % new_wait
        self.helper.change_wait_time(old_wait)

    @pytest.mark.skipif(str(103) not in TESTS, reason='Excluded')
    def test_helper_date_strings_103(self):
        """Render multiple date strings."""
        today = datetime.date.today()
        in_5 = today + datetime.timedelta(days=5)
        in_5 = in_5.strftime('%m/%d/%Y')
        formatted = today.strftime('%Y-%m-%d')
        in_12_formatted = today + datetime.timedelta(days=12)
        in_12_formatted = in_12_formatted.strftime('%Y%m%d')

        assert(self.helper.date_string() == today.strftime('%m/%d/%Y')), \
            'Default failed: %s != %s' % (
                self.helper.date_string(),
                today
        )
        assert(self.helper.date_string(5) == str(in_5)), \
            'Set +5 failed: %s != %s' % (
                self.helper.date_string(5),
                in_5
        )
        assert(self.helper.date_string(str_format='%Y-%m-%d') == formatted), \
            'Formatted failed: %s != %s' % (
                self.helper.date_string(str_format='%Y-%m-%d'),
                formatted
            )
        assert(self.helper.date_string(12, '%Y%m%d') == in_12_formatted), \
            'Set +12 formatted failed: %s != %s' % (
                self.helper.date_string(12, '%Y%m%d'),
                in_12_formatted
            )

    @pytest.mark.skipif(str(104) not in TESTS, reason='Excluded')
    def test_helper_get_webpage_104(self):
        """Get a webpage."""
        self.helper.get('https://www.google.com/')
        assert('Google' in self.helper.driver.title)

    @pytest.mark.skipif(str(105) not in TESTS, reason='Excluded')
    def test_helper_get_window_size_105(self):
        """Read window size."""
        new_height = randint(300, 600)
        new_width = randint(300, 600)
        self.helper.driver.set_window_size(new_width, new_height)
        current_size = self.helper.driver.get_window_size()
        helper_size = self.helper.get_window_size()

        assert(helper_size == current_size), \
            'Window size is incorrect: %s != %s' % \
            (helper_size, current_size)
        helper_size = self.helper.get_window_size('height')
        assert(helper_size == current_size['height']), \
            'Window height is incorrect: %s != %s' % \
            (helper_size, current_size['height'])
        helper_size = self.helper.get_window_size('width')
        assert(helper_size == current_size['width']), \
            'Window width is incorrect: %s != %s' % \
            (helper_size, current_size['width'])

    @pytest.mark.skipif(str(106) not in TESTS, reason='Excluded')
    def test_helper_sleep_within_two_percent_accuracy_106(self):
        """Sleep command is accurate to +-2%."""
        sleep_length = randint(3, 8) / 1.0
        start_time = time.time()
        self.helper.sleep(sleep_length)
        end_time = time.time()
        duration = end_time - start_time
        assert(duration >= sleep_length * 0.98), \
            'Sleep shorter than expected: %s < %s' % \
            (duration, sleep_length * 0.98)
        assert(duration <= sleep_length * 1.02), \
            'Sleep longer than expected: %s > %s' % \
            (duration, sleep_length * 1.02)


class TestStaxingUser(unittest.TestCase):
    """Staxing case tests for User."""

    def setUp(self):
        """Pretest settings."""
        self.user = User('', '', '')
        print(self.user.driver.get_window_size())
        self.user.set_window_size(height=700, width=1200)
        print(self.user.driver.get_window_size())
        self.server = ''.join(('https://', os.getenv('SERVER_URL')))
        self.login = os.getenv('STUDENT_USER_MULTI')
        self.password = os.getenv('STUDENT_PASSWORD')

    def tearDown(self):
        """Test destructor."""
        try:
            self.user.delete()
        except:
            pass

    @pytest.mark.skipif(str(201) not in TESTS, reason='Excluded')
    def test_user_tutor_login_201(self):
        """Log into Tutor."""
        self.user.login(self.server, self.login, self.password)
        was_successful = 'course' in self.user.current_url() or \
            'dashboard' in self.user.current_url() or \
            'calendar' in self.user.current_url()
        assert(was_successful), 'Failed to log into %s' % self.server

    @pytest.mark.skipif(str(202) not in TESTS, reason='Excluded')
    def test_user_tutor_logout_202(self):
        """Log out of Tutor"""
        self.user.login(self.server, self.login, self.password)
        self.user.logout()
        was_successful = \
            'http://cc.openstax.org/' in self.user.current_url() or \
            'https://tutor-qa.openstax.org/?' in self.user.current_url()
        assert(was_successful), 'Failed to log out of %s' % self.server

    @pytest.mark.skipif(str(203) not in TESTS, reason='Excluded')
    def test_user_accounts_login_203(self):
        """Log into Accounts."""
        accounts = self.server.replace('tutor', 'accounts')
        self.user.login(accounts, self.login, self.password)
        assert('profile' in self.user.current_url()), \
            'Failed to log into %s' % accounts

    @pytest.mark.skipif(str(204) not in TESTS, reason='Excluded')
    def test_user_accounts_logout_204(self):
        """Log out of Accounts."""
        accounts = self.server.replace('tutor', 'accounts')
        self.user.login(accounts, self.login, self.password)
        self.user.logout()
        assert('login' in self.user.current_url()), \
            'Failed to log out of %s' % accounts

    @pytest.mark.skipif(str(205) not in TESTS, reason='Excluded')
    def test_user_select_course_by_title_205(self):
        """Select a course by its title."""
        self.user.login(self.server, self.login, self.password)
        print(self.user.current_url())
        courses = self.user.get_course_list()
        course_number = 0 if len(courses) <= 1 \
            else randint(1, len(courses)) - 1
        title = courses[course_number].get_attribute('data-title')
        Assignment.scroll_to(self.user.driver, courses[course_number])
        self.user.select_course(title=title)
        was_successful = 'course' in self.user.current_url() or \
            'list' in self.user.current_url() or \
            'calendar' in self.user.current_url() or \
            'contents' in self.user.current_url()
        assert(was_successful), \
            'Failed to select course in URL: %s' % self.user.current_url()
        if 'contents' in self.user.current_url():
            return
        course_name = self.user.find(
            By.CLASS_NAME,
            'book-title-text'
        ).text
        assert(title == course_name), 'Failed to select course "%s"' % title

    @pytest.mark.skipif(str(206) not in TESTS, reason='Excluded')
    def test_user_select_course_by_appearance_206(self):
        """Select a course by its appearance."""
        self.user.login(self.server, self.login, self.password)
        courses = self.user.get_course_list()
        course_number = 0 if len(courses) == 1 \
            else randint(1, len(courses)) - 1
        assert(course_number >= 0), 'No courses found.'
        appearance = courses[course_number].get_attribute('data-appearance')
        appearance_courses = self.user.find_all(
                By.XPATH,
                '//div[contains(@data-appearance,"%s")]' % appearance
            )
        title = ''
        if isinstance(appearance_courses, list):
            for course in appearance_courses:
                title = title.join((' ', course.text))
        else:
            title = courses[course_number].text
        Assignment.scroll_to(self.user.driver, courses[course_number])
        self.user.select_course(appearance=appearance)
        was_successful = 'course' in self.user.current_url() or \
            'list' in self.user.current_url() or \
            'calendar' in self.user.current_url() or \
            'contents' in self.user.current_url()
        assert(was_successful), \
            'Failed to select course in URL: %s' % self.user.current_url()
        if 'contents' in self.user.current_url():
            return
        course_name = self.user.find(
            By.CLASS_NAME,
            'book-title-text'
        ).text
        assert(course_name in title.replace('\n', ' ')), \
            'Failed to select course "%s"' % course_name

    @pytest.mark.skipif(str(207) not in TESTS, reason='Excluded')
    def test_user_go_to_course_list_207(self):
        """No test placeholder."""
        self.user.login(self.server, self.login, self.password)
        courses = self.user.get_course_list()
        course_number = 0 if len(courses) <= 1 \
            else randint(1, len(courses)) - 1
        print(course_number)
        Assignment.scroll_to(self.user.driver, courses[course_number])
        self.user.select_course(
            title=courses[course_number].get_attribute('data-title'))
        url = self.user.current_url()
        was_successful = 'course' in url or \
            'list' in url or \
            'calendar' in url
        print('%s in %s == %s' %
              ('(course,list,calendar)', url, was_successful))
        assert(was_successful), 'Failed to select course'
        self.user.goto_course_list()
        course_picker = self.server + '/dashboard'
        url = self.user.current_url()
        print('%s ?= %s' % (url, course_picker))
        assert(url == course_picker), \
            'Failed to return to the course picker'

    @pytest.mark.skipif(str(208) not in TESTS, reason='Excluded')
    def test_user_open_the_reference_book_208(self):
        """No test placeholder."""
        self.user.login(self.server, self.login, self.password)
        main_window = self.user.driver.current_window_handle
        courses = self.user.get_course_list()
        course_number = 0 if len(courses) <= 1 \
            else randint(1, len(courses)) - 1
        Assignment.scroll_to(self.user.driver, courses[course_number])
        self.user.select_course(
            title=courses[course_number].get_attribute('data-title'))
        url = self.user.current_url()
        was_successful = 'course' in url or \
            'list' in url or \
            'calendar' in url
        print('%s in %s == %s' %
              ('(course,list,calendar)', url, was_successful))
        assert(was_successful), 'Failed to select course'
        self.user.view_reference_book()
        self.user.sleep(1)
        self.user.driver.switch_to_window(self.user.driver.window_handles[1])
        WebDriverWait(self.user.driver, 60).until(
            expect.presence_of_element_located(
                (By.CLASS_NAME, 'center-panel')
            )
        )
        assert('contents' in self.user.current_url() or
               'books' in self.user.current_url()), \
            'Failed to open the reference or WebView book.'
        self.user.driver.close()
        self.user.driver.switch_to_window(main_window)
        was_successful = 'course' in self.user.current_url() or \
            'list' in self.user.current_url() or \
            'calendar' in self.user.current_url()
        assert(was_successful), 'Failed to return to the primary browser tab'


class TestStaxingTutorTeacher(unittest.TestCase):
    """Staxing case tests."""

    book_sections = None
    class_start_end_dates = None

    def setUp(self):
        """Pretest settings."""
        self.teacher = Teacher(use_env_vars=True, driver='chrome')
        self.teacher.username = os.getenv('TEACHER_USER_MULTI',
                                          self.teacher.username)
        self.teacher.set_window_size(height=700, width=1200)
        self.teacher.login()
        courses = self.teacher.get_course_list()
        course = courses[randint(0, len(courses) - 1)]
        self.teacher.select_course(title=course.get_attribute('data-title'))
        if not self.__class__.book_sections:
            self.__class__.book_sections = self.teacher.get_book_sections()
            self.teacher.goto_calendar()
        if not self.__class__.class_start_end_dates:
            self.__class__.class_start_end_dates = \
                self.teacher.get_course_begin_end()
            self.teacher.goto_calendar()
        self.book_sections = self.__class__.book_sections
        self.start_end = self.__class__.class_start_end_dates

    def tearDown(self):
        """Test destructor."""
        try:
            self.teacher.delete()
        except:
            pass

    @pytest.mark.skipif(str(301) not in TESTS, reason='Excluded')
    def test_add_reading_assignment_individual_publish_301(self):
        """Build reading assignments."""
        # Reading, individual periods, publish

        assignment_title = 'Reading-%s' % Assignment.rword(5)

        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date_1 = self.teacher.date_string(day_delta=left_delta)
        start_date_2 = self.teacher.date_string(day_delta=left_delta + 1)
        start_date_3 = self.teacher.date_string(day_delta=left_delta + 2)
        if not self.teacher.date_is_valid(left):
            start_date_1 = self.class_start_end_dates[0]
            start_date_2 = self.class_start_end_dates[0] \
                + datetime.timedelta(1)
            start_date_3 = self.class_start_end_dates[0] \
                + datetime.timedelta(2)
        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date_1 = self.teacher.date_string(day_delta=right_delta)
        end_date_2 = self.teacher.date_string(day_delta=right_delta + 1)
        end_date_3 = self.teacher.date_string(day_delta=right_delta + 2)
        if not self.teacher.date_is_valid(right):
            end_date_1 = self.class_start_end_dates[1] - datetime.timedelta(2)
            end_date_2 = self.class_start_end_dates[1] - datetime.timedelta(1)
            end_date_3 = self.class_start_end_dates[1]
        print('Left: %s  Right: %s' % (left, right))
        start_time_2 = '6:30 am'
        end_time_2 = '11:59 pm'
        # start_date_3 = (left + datetime.timedelta(2)). \
        #     strftime('%m/%d/%Y')
        # end_date_3 = (right + datetime.timedelta(2)). \
        #     strftime('%m/%d/%Y')
        self.book_sections = self.teacher.get_book_sections()
        reading_start = randint(0, (len(self.book_sections) - 1))
        reading_end = reading_start + randint(1, 5)
        reading_list = self.book_sections[reading_start:reading_end]
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'description': 'Staxing test reading - individual periods - ' +
                               'publish',
                'periods': {
                    '1st': (start_date_1, end_date_1),
                    '2nd': ((start_date_2, start_time_2),
                            (end_date_2, end_time_2)),
                    '3rd': (start_date_3, end_date_3),
                },
                'reading_list': reading_list,
                'status': 'publish',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        self.teacher.rotate_calendar(end_date_1)
        reading = self.teacher.find(
            By.XPATH,
            '//label[text()="%s"]' % assignment_title
        )
        time.sleep(5.0)
        assert(reading), '%s not publishing on %s' % (assignment_title,
                                                      end_date_3)

    @pytest.mark.skipif(str(302) not in TESTS, reason='Excluded')
    def test_add_reading_assignment_all_publish_302(self):
        """Build reading assignments."""
        # Reading, all periods, publish
        assignment_title = 'Reading-%s' % Assignment.rword(5)

        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date_1 = self.teacher.date_string(day_delta=left_delta)
        start_date_2 = self.teacher.date_string(day_delta=left_delta + 1)
        if not self.teacher.date_is_valid(left):
            start_date_1 = self.class_start_end_dates[0]
            start_date_2 = self.class_start_end_dates[0] \
                + datetime.timedelta(1)

        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date_1 = self.teacher.date_string(day_delta=right_delta)
        end_date_2 = self.teacher.date_string(day_delta=right_delta + 1)
        if not self.teacher.date_is_valid(right):
            end_date_1 = self.class_start_end_dates[1] - 2
            end_date_2 = self.class_start_end_dates[1] - 1
        print('Left: %s  Right: %s' % (left, right))
        # self.book_sections = self.teacher.get_book_sections()
        reading_start = randint(0, (len(self.book_sections) - 1))
        reading_end = reading_start + randint(1, 5)
        reading_list = self.book_sections[reading_start:reading_end]
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'description': 'Staxing test reading - all periods - publish',
                'periods': {
                    '1st': (start_date_1, end_date_1),
                    'all': (start_date_2, end_date_2),
                },
                'reading_list': reading_list,
                'status': 'publish',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        time.sleep(2.0)
        self.teacher.rotate_calendar(end_date_1)
        reading = self.teacher.find(
            By.XPATH,
            '//label[text()="%s"]' % assignment_title
        )
        time.sleep(5.0)
        assert(reading), '%s not publishing on %s' % (assignment_title,
                                                      end_date_2)

    @pytest.mark.skipif(str(303) not in TESTS, reason='Excluded')
    def test_add_reading_assignment_individual_draft_303(self):
        """Build reading assignments."""
        # Reading, individual periods, draft
        assignment_title = 'Reading-%s' % Assignment.rword(5)
        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date_1 = self.teacher.date_string(day_delta=left_delta)
        start_date_2 = self.teacher.date_string(day_delta=left_delta + 1)
        start_date_3 = self.teacher.date_string(day_delta=left_delta + 2)
        if not self.teacher.date_is_valid(left):
            start_date_1 = self.class_start_end_dates[0]
            start_date_2 = self.class_start_end_dates[0] \
                + datetime.timedelta(1)
            start_date_3 = self.class_start_end_dates[0] \
                + datetime.timedelta(2)

        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date_1 = self.teacher.date_string(day_delta=right_delta)
        end_date_2 = self.teacher.date_string(day_delta=right_delta + 1)
        end_date_3 = self.teacher.date_string(day_delta=right_delta + 2)
        if not self.teacher.date_is_valid(right):
            end_date_1 = self.class_start_end_dates[1] - 2
            end_date_2 = self.class_start_end_dates[1] - 1
            end_date_3 = self.class_start_end_dates[1]
        print('Left: %s  Right: %s' % (left, right))
        # self.book_sections = self.teacher.get_book_sections()
        reading_start = randint(0, (len(self.book_sections) - 1))
        reading_end = reading_start + randint(1, 5)
        reading_list = self.book_sections[reading_start:reading_end]
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'description': 'Staxing test reading - individual periods ' +
                               '- draft',
                'periods': {
                    '1st': (start_date_1, end_date_1),
                    '2nd': (start_date_2, end_date_2),
                    '3rd': (start_date_3, end_date_3),
                },
                'reading_list': reading_list,
                'status': 'draft',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        self.teacher.rotate_calendar(end_date_1)
        reading = self.teacher.find(
            By.XPATH,
            '//label[text()="%s"]' % assignment_title
        )
        time.sleep(5.0)
        assert(reading), '%s not publishing on %s' % (assignment_title,
                                                      end_date_3)

    @pytest.mark.skipif(str(304) not in TESTS, reason='Excluded')
    def test_add_reading_assignment_all_draft_304(self):
        """Build reading assignments."""
        # Reading, all periods, draft
        assignment_title = 'Reading-%s' % Assignment.rword(5)
        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date_1 = self.teacher.date_string(day_delta=left_delta)
        if not self.teacher.date_is_valid(left):
            start_date_1 = self.class_start_end_dates[0]

        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date_1 = self.teacher.date_string(day_delta=right_delta)
        if not self.teacher.date_is_valid(right):
            end_date_1 = self.class_start_end_dates[1] - 2
        print('Left: %s  Right: %s' % (left, right))
        # self.book_sections = self.teacher.get_book_sections()
        reading_start = randint(0, (len(self.book_sections) - 1))
        reading_end = reading_start + randint(1, 5)
        reading_list = self.book_sections[reading_start:reading_end]
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'description': 'Staxing test reading - all periods - draft',
                'periods': {
                    'all': (start_date_1, end_date_1),
                },
                'reading_list': reading_list,
                'status': 'draft',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        self.teacher.rotate_calendar(end_date_1)
        reading = self.teacher.find(
            By.XPATH,
            '//label[text()="%s"]' % assignment_title
        )
        time.sleep(5.0)
        assert(reading), '%s not publishing on %s' % (assignment_title,
                                                      end_date_1)

    @pytest.mark.skipif(str(305) not in TESTS, reason='Excluded')
    def test_add_reading_assignment_one_cancel_305(self):
        """Build reading assignments."""
        # Reading, one period, cancel
        assignment_title = 'Reading-%s' % Assignment.rword(5)
        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date_1 = self.teacher.date_string(day_delta=left_delta)
        if not self.teacher.date_is_valid(left):
            start_date_1 = self.class_start_end_dates[0]

        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date_1 = self.teacher.date_string(day_delta=right_delta)
        if not self.teacher.date_is_valid(right):
            end_date_1 = self.class_start_end_dates[1] - 2
        print('Left: %s  Right: %s' % (left, right))
        # self.book_sections = self.teacher.get_book_sections()
        reading_start = randint(0, (len(self.book_sections) - 1))
        reading_end = reading_start + randint(1, 5)
        reading_list = self.book_sections[reading_start:reading_end]
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'description': 'Staxing test reading - cancel',
                'periods': {
                    '1st': (start_date_1, end_date_1),
                },
                'reading_list': reading_list,
                'status': 'cancel',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        self.teacher.rotate_calendar(end_date_1)
        time.sleep(5.0)
        with pytest.raises(NoSuchElementException):
            self.teacher.find(
                By.XPATH,
                '//label[text()="%s"]' % assignment_title
            )

    @pytest.mark.skipif(str(306) not in TESTS, reason='Excluded')
    def test_change_assignment_306(self):
        """No test placeholder."""
        pass

    @pytest.mark.skipif(str(307) not in TESTS, reason='Excluded')
    def test_delete_assignment_307(self):
        """No test placeholder."""
        assignment_title = 'Reading-%s' % Assignment.rword(5)
        left_delta = randint(0, 20)
        left = datetime.date.today() + datetime.timedelta(left_delta)
        start_date = self.teacher.date_string(day_delta=left_delta)
        if not self.teacher.date_is_valid(left):
            start_date = self.class_start_end_dates[0]

        right_delta = left_delta + randint(1, 10)
        right = datetime.date.today() + datetime.timedelta(right_delta)
        end_date = self.teacher.date_string(day_delta=right_delta)
        if not self.teacher.date_is_valid(right):
            end_date = self.class_start_end_dates[1] - 2
        self.teacher.add_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'periods': {
                    'all': (start_date, end_date),
                },
                'reading_list': ['1', '1.1'],
                'status': 'publish',
                'break_point': None,
            }
        )
        assert('course' in self.teacher.current_url()), \
            'Not at dashboard'
        self.teacher.rotate_calendar(end_date)
        reading = self.teacher.find(
            By.XPATH,
            '//label[text()="%s"]' % assignment_title
        )
        print('Waiting for publish')

        # assert('course' in self.teacher.current_url()), \
        #     'Not at dashboard'
        # self.teacher.rotate_calendar(end_date_1)
        # reading = self.teacher.find(
        #     By.XPATH,
        #     '//label[text()="%s"]' % assignment_title
        # )
        # time.sleep(5.0)
        # assert(reading), '%s not publishing on %s' % (assignment_title,
        #                                               end_date_3)

        time.sleep(5.0)
        assert(reading), \
            '%s not publishing on %s' % (assignment_title, end_date)
        # new_date = start_date.split('/')
        # new_date = '%s/%s' % (int(new_date[0]), int(new_date[1]))
        # self.teacher.wait.until(
        #     expect.presence_of_element_located(
        #         (By.XPATH,
        #          '//label[@data-title="%s" and @data-opens-at="%s"]' %
        #          (assignment_title, new_date))
        #     )
        # )
        self.teacher.delete_assignment(
            assignment='reading',
            args={
                'title': assignment_title,
                'periods': {
                    'all': (start_date, end_date),
                },
            }
        )
        self.teacher.rotate_calendar(end_date)
        time.sleep(5.0)
        try:
            self.teacher.find(
                By.XPATH,
                '//label[text()="%s"]' % assignment_title
            )
            assert(False), '%s still exists' % assignment_title
        except:
            pass

    @pytest.mark.skipif(str(308) not in TESTS, reason='Excluded')
    def test_goto_menu_item_308(self):
        """No test placeholder."""
        pass

    @pytest.mark.skipif(str(309) not in TESTS, reason='Excluded')
    def test_goto_calendar_309(self):
        """No test placeholder."""
        pass

    @pytest.mark.skipif(str(310) not in TESTS, reason='Excluded')
    def test_goto_performance_forecast_310(self):
        """No test placeholder."""
        self.teacher.goto_performance_forecast()

    @pytest.mark.skipif(str(311) not in TESTS, reason='Excluded')
    def test_goto_student_scores_311(self):
        """No test placeholder."""
        self.teacher.goto_student_scores()

    @pytest.mark.skipif(str(312) not in TESTS, reason='Excluded')
    def test_goto_course_roster_312(self):
        """No test placeholder."""
        self.teacher.goto_course_roster()

    @pytest.mark.skipif(str(313) not in TESTS, reason='Excluded')
    def test_goto_course_settings_313(self):
        """No test placeholder."""
        self.teacher.goto_course_settings()

    @pytest.mark.skipif(str(314) not in TESTS, reason='Excluded')
    def test_add_course_section_314(self):
        """Add a course section to a class."""
        section_name = 'New Section'
        self.teacher.add_course_section(section_name)
        classes = self.teacher.find_all(By.CSS_SELECTOR, 'a[role*="tab"]')
        section_names = []
        for section in classes:
            section_names.append(section.get_attribute('innerHTML'))
        assert(section_name in section_names), \
            '%s not in %s' % (section_name, section_names)
        self.teacher.goto_course_settings()
        self.teacher.find

    @pytest.mark.skipif(str(315) not in TESTS, reason='Excluded')
    def test_get_enrollment_code_315(self):
        """No test placeholder."""
        code = self.teacher.get_enrollment_code()
        assert('enroll' in code and code[-6:].isdigit()), \
            '%s is not the correct enrollment URL' % code


'''class TestStaxingConceptCoachTeacher(unittest.TestCase):
    """Staxing case tests."""

    def setUp(self):
        """Pretest settings."""
        self.teacher = Teacher(username='', password='', site='')
        self.teacher.set_window_size(height=700, width=1200)

    def tearDown(self):
        """Test destructor."""
        try:
            self.teacher.delete()
        except:
            pass

    # @pytest.mark.skipif(str(401) not in TESTS, reason='Excluded')
    # def test_base_case_401(self):
    #     """No test placeholder."""
    #     pass'''


class TestStaxingTutorStudent(unittest.TestCase):
    """Staxing case tests."""

    def setUp(self):
        """Pretest settings."""
        self.student = Student(use_env_vars=True)
        self.student.set_window_size(height=700, width=1200)

    def tearDown(self):
        """Test destructor."""
        try:
            self.student.delete()
        except:
            pass

    # @pytest.mark.skipif(str(501) not in TESTS, reason='Excluded')
    # def test_base_case_501(self):
    #     """No test placeholder."""
    #     pass


'''class TestStaxingConceptCoachStudent(unittest.TestCase):
    """Staxing case tests."""

    def setUp(self):
        """Pretest settings."""
        self.student = Student(use_env_vars=True)
        self.student.set_window_size(height=700, width=1200)

    def tearDown(self):
        """Test destructor."""
        try:
            self.student.delete()
        except:
            pass

    # @pytest.mark.skipif(str(601) not in TESTS, reason='Excluded')
    # def test_base_case_601(self):
    #     """No test placeholder."""
    #     pass'''


class TestStaxingAdmin(unittest.TestCase):
    """Staxing case tests."""

    def setUp(self):
        """Pretest settings."""
        self.admin = Admin(use_env_vars=True)
        self.admin.set_window_size(height=700, width=1200)

    def tearDown(self):
        """Test destructor."""
        try:
            self.admin.delete()
        except:
            pass

    # @pytest.mark.skipif(str(701) not in TESTS, reason='Excluded')
    # def test_base_case_701(self):
    #     """No test placeholder."""
    #     pass


class TestStaxingContentQA(unittest.TestCase):
    """Staxing case tests."""

    def setUp(self):
        """Pretest settings."""
        self.content = ContentQA(use_env_vars=True)
        self.content.set_window_size(height=700, width=1200)

    def tearDown(self):
        """Test destructor."""
        try:
            self.content.delete()
        except:
            pass

    # @pytest.mark.skipif(str(801) not in TESTS, reason='Excluded')
    # def test_base_case_801(self):
    #     """No test placeholder."""
    #     pass
