"""Assignment helper functions for Selenium testing."""

import calendar
import datetime
import inspect
import random
import string
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as expect
from selenium.webdriver.support.ui import WebDriverWait

__version__ = '0.0.36'

try:
    from staxing.page_load import SeleniumWait as Page
except ImportError:  # pragma: no cover
    from page_load import SeleniumWait as Page


class Assignment(object):
    """Shortcut functions to add, edit, and delete assignments."""

    READING = 'reading'
    HOMEWORK = 'homework'
    EXTERNAL = 'external'
    EVENT = 'event'

    BEFORE_TITLE = 'title'
    BEFORE_DESCRIPTION = 'description'
    BEFORE_PERIOD = 'period'
    BEFORE_SECTION_SELECT = 'section'
    BEFORE_READING_SELECT = 'reading'
    BEFORE_EXERCISE_SELECT = 'exercise'
    BEFORE_URL = 'url'
    BEFORE_STATUS_SELECT = 'status'

    WAIT_TIME = 15

    TUTOR_SELECTIONS = 'tutor'

    PUBLISH = 'publish'
    CANCEL = 'cancel'
    DRAFT = 'draft'
    DELETE = 'delete'

    def __init__(self):
        """Provide a switch-style dictionary to add assignments."""
        self.add = {
            Assignment.READING:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.add_new_reading(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    readings=reading_list,
                    status=state)
            ),
            Assignment.HOMEWORK:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.add_new_homework(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    problems=problems,
                    status=state,
                    feedback=feedback)
            ),
            Assignment.EXTERNAL:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.add_new_external(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    assignment_url=url,
                    status=state)
            ),
            Assignment.EVENT:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.add_new_event(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    status=state)
            ),
        }
        self.edit = {
            Assignment.READING:
            (
                lambda driver, name, description='', periods={},
                reading_list={}, state=Assignment.DRAFT, problems=None,
                url='', feedback='immediate':
                self.change_reading(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    readings=reading_list,
                    status=state)
            ),
            Assignment.HOMEWORK:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.change_homework(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    problems=problems,
                    status=state,
                    feedback=feedback)
            ),
            Assignment.EXTERNAL:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.change_external(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    assignment_url=url,
                    status=state)
            ),
            Assignment.EVENT:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.change_event(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    status=state)
            ),
        }
        self.remove = {
            Assignment.READING:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.delete_reading(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    readings=reading_list,
                    status=state)
            ),
            Assignment.HOMEWORK:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.delete_homework(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    problems=problems,
                    status=state,
                    feedback=feedback)
            ),
            Assignment.EXTERNAL:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.delete_external(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    assignment_url=url,
                    status=state)
            ),
            Assignment.EVENT:
            (
                lambda driver, name, description, periods, reading_list, state,
                problems, url, feedback:
                self.delete_event(
                    driver=driver,
                    title=name,
                    description=description,
                    periods=periods,
                    status=state)
            ),
        }

    @classmethod
    def rword(cls, length):
        """Return a <length>-character random string."""
        return ''.join(random.choice(string.ascii_lowercase)
                       for _ in range(length))

    @classmethod
    def scroll_to(cls, driver, element):
        """Execute a scroll until in view javascript."""
        driver.execute_script('return arguments[0].scrollIntoView();', element)
        driver.execute_script('window.scrollBy(0, -80);')

    @classmethod
    def send_keys(cls, driver, element, text):
        """Send data to an element using javascript."""
        Assignment.scroll_to(driver, element)
        element.clear()
        time.sleep(0.3)
        for ch in text:
            element.send_keys(ch)

    def open_assignment_menu(self, driver):
        """Open the Add Assignment menu if it is closed."""
        print('Open the assignment menu')
        assignment_menu = driver.find_element(
            By.CSS_SELECTOR,
            'button'
        )
        Assignment.scroll_to(driver, assignment_menu)
        color = assignment_menu.value_of_css_property('background-color')
        print('Current menu color: %s' % color.lower())
        if not color.lower() == 'rgba(153, 153, 153, 1)':
            # background isn't gray so the toggle is still closed
            assignment_menu.click()
            print('Open menu')
            return
        print('Menu already open')

    def modify_time(self, time):
        """Modify time string for react."""
        string = time
        string = str.replace(string, ':', '')
        string = str.replace(string, ' ', '')
        string = str.replace(string, 'm', '')
        return string

    def adjust_date_picker(self, driver, target, new_date):
        """Rotate the date picker to the correct month and year."""
        today = datetime.date.today()
        target.click()
        if today.year == new_date.year and today.month == new_date.month:
            return
        months = {v: k for k, v in enumerate(calendar.month_name)}

        next_month = driver.find_element(
            By.CLASS_NAME,
            'react-datepicker__navigation--next'
        )
        current = driver.find_element(
            By.CLASS_NAME,
            'react-datepicker__current-month'
        )
        month, year = current.text.split(' ')
        month = months[month]
        year = int(year)

        while year <= new_date.year and month < new_date.month:
            next_month.click()
            current = driver.find_element(
                By.CLASS_NAME,
                'react-datepicker__current-month'
            )
            month, year = current.text.split(' ')
            month = months[month]
            year = int(year)
            time.sleep(1.0)
        while year >= new_date.year and month > new_date.month:
            # because it will only ever go back one month it's okay to find
            # arrow inside the while loop
            previous_month = driver.find_element(
                By.CLASS_NAME,
                'react-datepicker__navigation--previous'
            )
            previous_month.click()
            current = driver.find_element(
                By.CLASS_NAME,
                'react-datepicker__current-month'
            )
            month, year = current.text.split(' ')
            month = months[month]
            year = int(year)
            time.sleep(1.0)

    def assign_time(self, driver, time,
                    option=None, is_all=False, target='due'):
        """Set the time for a particular period/section row."""
        start = option if option else driver
        path = '../..' if not is_all else ''
        path += '//div[contains(@class,"-%s-time")]//input' % target
        element = start.find_element(By.XPATH, path)
        element.clear()
        for char in self.modify_time(time):
            element.send_keys(char)

    def to_date_string(self, day_delta=0, str_format='%m/%d/%Y'):
        """System date format for Tutor."""
        return (datetime.date.today() + datetime.timedelta(days=day_delta)). \
            strftime(str_format)

    def assign_date(self, driver, date,
                    option=None, is_all=False, target='due'):
        """Set the date for a particular period/section row."""
        start = option if option else driver
        path = '../..' if not is_all else ''
        path += '//div[contains(@class,"-%s-date")]' % target
        path += '//div[contains(@class,"react-datepicker__input")]//input'
        date_element = start.find_element(By.XPATH, path)
        # get calendar to correct month
        split = date.split('/')
        change = datetime.date(int(split[2]), int(split[0]), int(split[1]))
        time.sleep(0.15)
        self.adjust_date_picker(driver, date_element, change)
        driver.find_element(
            By.XPATH,
            '//div[contains(@class,"react-datepicker__day") ' +
            'and not(contains(@class,"disabled")) ' +
            'and text()="%s"]' % change.day
        ).click()

    def assign_periods(self, driver, periods):
        """Assign dates and times to particular periods/sections."""
        # prepare assignment for all periods/sections together
        if 'all' in periods:
            # activate the collective time/date panel
            driver.find_element(By.ID, 'hide-periods-radio').click()
            opens_at = None
            closes_at = None
            opens_on, closes_on = periods['all']
            if isinstance(opens_on, tuple):
                opens_on, opens_at = opens_on
            if isinstance(closes_on, tuple):
                closes_on, closes_at = closes_on
            self.assign_date(driver=driver, date=closes_on,
                             is_all=True, target='due')
            if closes_at:
                self.assign_time(driver=driver, time=closes_at,
                                 is_all=True, target='due')
            self.assign_date(driver=driver, date=opens_on,
                             is_all=True, target='open')
            if opens_at:
                self.assign_time(driver=driver, time=opens_at,
                                 is_all=True, target='open')
            return
        # or locate important elements for each period/section
        options = {}
        # activate the individual period time/date panel
        driver.find_element(By.ID, 'show-periods-radio').click()
        period_boxes = driver.find_elements(
            By.XPATH,
            '//input[contains(@id,"period-toggle-period")]'
        )
        for period in period_boxes:
            options[
                driver.find_element(
                    By.XPATH,
                    '//label[@for="%s"]' % period.get_attribute('id')
                ).text
            ] = period
        period_match = False
        for period in options:
            print('Period:', period)
            # activate or deactivate a specific period/section row
            period_match = period_match or period in periods
            if period not in periods:
                if not options[period].is_displayed():
                    driver.execute_script(
                        "return arguments[0].scrollIntoView();",
                        options[period]
                    )
                if options[period].get_attribute('checked') is not None:
                    options[period].click()
                continue
            if options[period].get_attribute('checked') is None:
                options[period].click()
            # set dates
            opens_at = None
            closes_at = None
            opens_on, closes_on = periods[period]
            if isinstance(opens_on, tuple):
                opens_on, opens_at = opens_on
            if isinstance(closes_on, tuple):
                closes_on, closes_at = closes_on
            self.assign_date(driver=driver, date=closes_on,
                             option=options[period], target='due')
            if closes_at:
                self.assign_time(driver=driver, time=closes_at,
                                 option=options[period], target='due')
            self.assign_date(driver=driver, date=opens_on,
                             option=options[period], target='open')
            if opens_at:
                self.assign_time(driver=driver, time=opens_at,
                                 option=options[period], target='open')
        if not period_match:
            raise ValueError('No periods matched')

    def select_status(self, driver, status):
        """Select assignment status."""
        element = driver.find_element(
            By.XPATH, '//div[contains(@class,"footer")]')
        Assignment.scroll_to(driver, element)
        if status == self.PUBLISH:
            print('Publishing...')
            time.sleep(1)
            driver.find_element(
                By.XPATH, '//button[contains(@class,"-publish")]').click()
        elif status == self.DRAFT:
            print('Saving draft')
            time.sleep(1)
            element = driver.find_element(
                By.XPATH, '//button[contains(@class," -save")]').click()
        elif status == self.CANCEL:
            print('Canceling assignment')
            time.sleep(1)
            element = driver.find_element(
                By.XPATH,
                '//button[contains(text(),"Cancel") and @type="button"]'
            ).click()
            try:
                wait = WebDriverWait(driver, Assignment.WAIT_TIME)
                wait.until(
                    expect.visibility_of_element_located(
                        (By.XPATH, '//button[contains(@class,"ok")]')
                    )
                ).click()
            except:
                pass
        elif status == self.DELETE:
            print('Deleting assignment')
            time.sleep(1)
            element = driver.find_element(
                By.XPATH,
                '//button[contains(text(),"Delete")]'
            ).click()
            wait = WebDriverWait(driver, Assignment.WAIT_TIME)
            wait.until(
                expect.visibility_of_element_located(
                    (By.XPATH, '//button[contains(@class,"ok")]')
                )
            ).click()

    def open_chapter_list(self, driver, chapter):
        """Open the reading chapter list."""
        data_chapter = driver.find_element(
            By.XPATH,
            '//div[@data-chapter-section="%s"]/a' % chapter
        )
        if (data_chapter.get_attribute('aria-expanded')).lower() == 'false':
            data_chapter.click()

    def select_sections(self, driver, chapters):
        """Select the sections and chapters."""
        for section in chapters:
            if 'ch' in section:  # select the whole chapter
                print('Adding chapter: ' + section)
                chapter = driver.find_element(
                    By.XPATH,
                    '//div[@data-chapter-section="%s"]' % section[2:] +
                    '//i[contains(@class,"tutor-icon")]'
                )
                time.sleep(0.5)
                if not chapter.is_selected():
                    chapter.click()
            elif 'tutor' in section:
                continue
            else:  # select an individual section
                print('Adding section: ' + section)
                self.open_chapter_list(driver, section.split('.')[0])
                time.sleep(0.5)
                wait = WebDriverWait(driver, Assignment.WAIT_TIME)
                marked = wait.until(
                    expect.visibility_of_element_located((
                        By.XPATH,
                        ('//span[contains(@data-chapter-section' +
                         ',"{0}") and text()="{0}"]').format(section) +
                        '/preceding-sibling::span/input'
                    ))
                )
                if not marked.is_selected():
                    marked.click()

    def add_new_reading(self, driver, title, description, periods, readings,
                        status, break_point=None):
        """Add a new reading assignment.

        driver:      WebDriver - Selenium WebDriver instance
        title:       string    - assignment title
        description: string    - assignment description or additional
                                 instructions
        periods:     dict      - <key>:   string <period name> OR 'all'
                                 <value>: tuple  (<open date>, <close date>)
                                          date format is 'MM/DD/YYYY'
        readings:    [string]  - chapter and section numbers to include in the
                                 assignment; chapter numbers are prefixed with
                                 'ch'
        status:      string    - 'publish', 'cancel', or 'draft'
        """
        print('Creating a new Reading: %s' % title)
        self.open_assignment_menu(driver)
        driver.find_element(By.LINK_TEXT, 'Add Reading').click()
        time.sleep(1)
        wait = WebDriverWait(driver, Assignment.WAIT_TIME * 3)
        wait.until(
            expect.element_to_be_clickable(
                (By.ID, 'reading-title')
            )
        )
        if break_point == Assignment.BEFORE_TITLE:
            print('Break BEFORE_TITLE')
            return
        print('Enter the title')
        driver.find_element(By.ID, 'reading-title').send_keys(title)
        if break_point == Assignment.BEFORE_DESCRIPTION:
            print('Break BEFORE_DESCRIPTION')
            return
        print('Enter the description')
        driver.find_element(
            By.XPATH,
            '//div[contains(@class,"assignment-description")]//textarea' +
            '[contains(@class,"form-control")]'). \
            send_keys(description)
        if break_point == Assignment.BEFORE_PERIOD:
            print('Break BEFORE_PERIOD')
            return
        print('Assign periods')
        self.assign_periods(driver, periods)
        # add reading sections to the assignment
        print('Set reading section list')
        driver.find_element(By.ID, 'reading-select').click()
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//div[contains(@class,"reading-plan")]')
            )
        )
        if break_point == Assignment.BEFORE_SECTION_SELECT:
            print('Break BEFORE_SECTION_SELECT')
            return
        self.select_sections(driver, readings)
        if break_point == Assignment.BEFORE_READING_SELECT:
            print('Break BEFORE_READING_SELECT')
            return
        driver.find_element(By.XPATH,
                            '//button[text()="Add Readings"]').click()
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//button[contains(@class,"-publish")]')
            )
        )
        if break_point == Assignment.BEFORE_STATUS_SELECT:
            print('Break BEFORE_STATUS_SELECT')
            return
        print('Set assignment status: %s' % status)
        self.select_status(driver, status)

    def find_all_questions(self, driver, problems):
        """Final all available questions."""
        questions = {}
        section = ''
        wait = WebDriverWait(driver, 5)
        try:
            loading = wait.until(
                expect.visibility_of_element_located(
                    (By.XPATH, '//span[text()="Loading..."]')
                )
            )
            wait.until(expect.staleness_of(loading))
        except:
            pass
        rows = driver.find_elements(
            By.XPATH,
            '//div[contains(@class,"exercise-sections")]')
        for row in rows:
            children = row.find_elements(
                By.XPATH,
                './/div[@class="exercises"]//span[contains(text(),"ID:")]')
            section = row.find_element(
                By.XPATH,
                './label/span[@class="chapter-section"]').text

            if len(children) == 0:
                # print('FAQ - No children tags')
                questions[section] = []
            else:
                questions[section] = []
                for q in children:
                    question = q.text.split(' ')[1]
                    questions[section].append(question)
        return questions

    def get_chapter_list(self, problems, chapter_id):
        """Return available chapters."""
        available = []
        chapter = int(chapter_id[2:])
        for section in problems:
            if int(section.split('.')[0]) == chapter:
                for i in range(len(problems[section])):
                    available.append(problems[section][i])
        return available

    def set_tutor_selections(self, driver, problems):
        """Select the number of Tutor selected problems."""
        tutor_picks = driver.find_element(
            By.XPATH, '//div[@class="tutor-selections"]//h2')
        current = int(tutor_picks.text)
        change = int(problems['tutor']) - current
        if change != 0:
            increase = driver.find_element(
                By.XPATH,
                '//div[@class="tutor-selections"]' +
                '//button[contains(@class,"-move-exercise-down")]'
            )
            decrease = driver.find_element(
                By.XPATH,
                '//div[@class="tutor-selections"]' +
                '//button[contains(@class,"-move-exercise-up")]'
            )
            while change < 0:
                change += 1
                increase.click()
            while change > 0:
                change -= 1
                decrease.click()

    def add_homework_problems(self, driver, problems):
        """Add assessments to a homework."""
        wait = WebDriverWait(driver, Assignment.WAIT_TIME)
        driver.find_element(By.ID, 'problems-select').click()
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH,
                 '//div[@class="homework-plan-exercise-select-topics"]')
            )
        )
        self.select_sections(driver, list(problems.keys()))
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        driver.find_element(
            By.XPATH, '//button[contains(@class,"-show-problems")]'
        ).click()
        all_available = self.find_all_questions(driver, problems)
        using = []
        # print('AHP - Selection list: %s' % selections)
        for section in problems:
            if problems is None or str(problems).lower() == 'none':
                print('%s: No exercises (%s)' % (section, problems[section]))
                continue
            # Set maximum Tutor-selected problems
            if section == 'tutor':
                print('Using %s Tutor selections' % problems[section])
                self.set_tutor_selections(driver, problems)
            # Select all exercises in the section
            elif problems[section] == 'all':
                print('Selecting all from %s' % section)
                available = self.get_chapter_list(all_available, section) if \
                    'ch' in section else all_available[section]
                for ex in available:
                    using.append(ex)
            # Select between X and Y exercises, inclusive, from the section
            elif type(problems[section]) == tuple:
                low, high = problems[section]
                total = random.randint(int(low), int(high))
                print('Selecting %s random from %s (%s to %s)' %
                      (total, section, low, high))
                available = self.get_chapter_list(all_available, section) if \
                    'ch' in section else all_available[section]
                for _ in range(total):
                    ex = random.randint(0, len(available) - 1)
                    using.append(available[ex])
                    available.remove(available[ex])
            # Select the first X exercises from the section
            elif type(problems[section]) == int:
                print('Selecting first %s from %s' %
                      (problems[section], section))
                available = self.get_chapter_list(all_available, section) if \
                    'ch' in section else all_available[section]
                for position in range(problems[section]):
                    using.append(available[position])
            elif type(problems[section]) == list:
                print('Adding %s custom if available' % len(problems[section]))
                for ex in problems[section]:
                    for section in all_available:
                        if ex in all_available[section]:
                            using.append(ex)
        for exercise in set(using):
            add_button = driver.find_element(
                By.XPATH,
                '//span[contains(text(),"%s")]' % exercise +
                '/../../div[@class="controls-overlay"]')
            Assignment.scroll_to(driver, add_button)
            ac = ActionChains(driver)
            time.sleep(0.5)
            ac.move_to_element(add_button)
            for _ in range(60):
                ac.move_by_offset(-1, 0)
            ac.click()
            ac.perform()
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//*[text()="Next"]')
            )
        ).click()

    def add_new_homework(self, driver, title, description, periods, problems,
                         status, feedback, break_point=None):
        """Add a new homework assignment.

        driver:      WebDriver - Selenium WebDriver instance
        title:       string    - assignment title
        description: string    - assignment description or additional
                                 instructions
        periods:     dict      - <key>:   string <period name> OR 'all'
                                 <value>: tuple  (<open date>, <close date>)
                                          date format is 'MM/DD/YYYY'
        problems:    dict      - <key>:   string '<chapter.section>' or 'tutor'
                               - <value>: [string] Ex-IDs
                                          int use first <int> exercises
                                              available
                                          (int, int) between <min> and <max>
                                              exercises
                                          'all' select all exercises in a
                                              section
                                          int 'tutor' takes 2, 3, or 4
                                              default: 3
        status:      string    - 'publish', 'cancel', or 'draft'
        feedback:    string    - 'immediate', 'non-immediate'
        """
        print('Creating a new Homework: %s' % title)
        self.open_assignment_menu(driver)
        driver.find_element(By.LINK_TEXT, 'Add Homework').click()
        wait = WebDriverWait(driver, Assignment.WAIT_TIME)
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//div[contains(@class,"homework-plan")]')
            )
        )
        if break_point == Assignment.BEFORE_TITLE:
            return
        driver.find_element(By.ID, 'reading-title').send_keys(title)
        if break_point == Assignment.BEFORE_DESCRIPTION:
            return
        driver.find_element(
            By.XPATH,
            '//div[contains(@class,"assignment-description")]' +
            '//textarea[contains(@class,"form-control")]'). \
            send_keys(description)
        if break_point == Assignment.BEFORE_PERIOD:
            return
        self.assign_periods(driver, periods)
        if break_point == Assignment.BEFORE_EXERCISE_SELECT:
            return
        self.add_homework_problems(driver, problems)
        feedback = driver.find_element(By.ID, 'feedback-select')
        Assignment.scroll_to(driver, feedback)
        feedback.click()
        if feedback == 'immediate':
            driver.find_element(
                By.XPATH,
                '//option[@value="immediate"]'
            ).click()
        else:
            driver.find_element(By.XPATH, '//option[@value="due_at"]').click()
        if break_point == Assignment.BEFORE_STATUS_SELECT:
            return
        self.select_status(driver, status)

    def add_new_external(self, driver, title, description, periods,
                         assignment_url, status, break_point=None):
        """Add a new external assignment.

        driver:      WebDriver - Selenium WebDriver instance
        title:       string    - assignment title
        description: string    - assignment description or additional
                                 instructions
        periods:     dict      - <key>:   string <period name> OR 'all'
                                 <value>: tuple  (<open date>, <close date>)
                                          date format is 'MM/DD/YYYY'
        assignment_url:    string      - website name
        status:      string    - 'publish', 'cancel', or 'draft'
        """
        print('Creating a new External Assignment: %s' % title)
        self.open_assignment_menu(driver)
        driver.find_element(By.LINK_TEXT, 'Add External Assignment').click()
        time.sleep(1)
        wait = WebDriverWait(driver, Assignment.WAIT_TIME * 3)
        wait.until(
            expect.element_to_be_clickable(
                (By.ID, 'reading-title')
            )
        )
        if break_point == Assignment.BEFORE_TITLE:
            return
        driver.find_element(By.ID, 'reading-title').send_keys(title)
        if break_point == Assignment.BEFORE_DESCRIPTION:
            return
        driver.find_element(
            By.XPATH,
            '//div[contains(@class,"assignment-description")]//textarea' +
            '[contains(@class,"form-control")]'). \
            send_keys(description)
        if break_point == Assignment.BEFORE_PERIOD:
            return
        self.assign_periods(driver, periods)
        if break_point == Assignment.BEFORE_URL:
            return
        driver.find_element(By.ID, 'external-url').send_keys(assignment_url)
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//button[contains(@class,"-publish")]')
            )
        )
        if break_point == Assignment.BEFORE_STATUS_SELECT:
            return
        self.select_status(driver, status)

    def add_new_event(self, driver, title, description, periods, status,
                      break_point=None):
        """Add a new external assignment.

        driver:      WebDriver - Selenium WebDriver instance
        title:       string    - assignment title
        description: string    - assignment description or additional
                                 instructions
        periods:     dict      - <key>:   string <period name> OR 'all'
                                 <value>: tuple  (<open date>, <close date>)
                                          date format is 'MM/DD/YYYY'
        status:      string    - 'publish', 'cancel', or 'draft'
        """
        print('Creating a new Event: %s' % title)
        self.open_assignment_menu(driver)
        driver.find_element(By.LINK_TEXT, 'Add Event').click()
        time.sleep(1)
        wait = WebDriverWait(driver, Assignment.WAIT_TIME * 3)
        wait.until(
            expect.element_to_be_clickable(
                (By.ID, 'reading-title')
            )
        )
        if break_point == Assignment.BEFORE_TITLE:
            return
        driver.find_element(By.ID, 'reading-title').send_keys(title)
        if break_point == Assignment.BEFORE_DESCRIPTION:
            return
        driver.find_element(
            By.XPATH,
            '//div[contains(@class,"assignment-description")]//textarea' +
            '[contains(@class,"form-control")]'). \
            send_keys(description)
        if break_point == Assignment.BEFORE_PERIOD:
            return
        self.assign_periods(driver, periods)
        wait.until(
            expect.visibility_of_element_located(
                (By.XPATH, '//button[contains(@class,"-publish")]')
            )
        )
        if break_point == Assignment.BEFORE_STATUS_SELECT:
            return
        self.select_status(driver, status)

    def change_reading(self, driver, title, description='', periods={},
                       readings=[], status=DRAFT):
        """Edit a reading assignment."""
        print('Change Reading: %s' % title)
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def change_homework(self, driver, title, description, periods, problems,
                        feedback, status):
        """Edit a homework assignment."""
        print('Change Homework: %s' % title)
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def change_external(self, driver, title, description, periods,
                        assignment_url, status):
        """Edit an external assignment."""
        print('Change External: %s' % title)
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def change_event(self, driver, title, description, periods, status):
        """Edit an event."""
        print('Change Event: %s' % title)
        raise NotImplementedError(inspect.currentframe().f_code.co_name)

    def delete_reading(self, driver, title, description, periods, readings,
                       status):
        """Delete a reading assignment."""
        print('Delete Reading: %s' % title)
        wait = WebDriverWait(driver, Assignment.WAIT_TIME * 4)
        wait.until(
            expect.visibility_of_element_located(
                (By.CSS_SELECTOR, '.course-name')
            )
        )  # .click()
        due_date = ''
        for period in periods:
            _, due_date = periods[period]
            break
        print('Currently at: %s' % driver.current_url)
        url = driver.current_url.split('/')
        date = due_date.split('/')
        temp = []
        temp.append(date[2])
        temp.append(date[0])
        temp.append(date[1])
        date = '-'.join(temp)
        print('URL segments: %s' % str(url))
        url.append('month')
        url.append(date)
        url = '/'.join(url)
        print('Rebuit URL: %s' % str(url))
        driver.get(url)
        page = Page(driver, Assignment.WAIT_TIME)
        page.wait_for_page_load()
        wait.until(
            expect.presence_of_element_located(
                (By.XPATH, '//a[div[label[text()="%s"]]]' % title)
            )
        ).click()
        time.sleep(0.3)
        try:
            modal = driver.find_element(By.CLASS_NAME, '-edit-assignment')
            Assignment.scroll_to(driver, modal)
            modal.click()
        except:
            pass
        page.wait_for_page_load()
        wait.until(
            expect.presence_of_element_located(
                (By.CLASS_NAME, 'delete-link')
            )
        ).click()
        wait.until(
            expect.presence_of_element_located(
                (By.XPATH, '//div[@class="controls"]/button[text()="Yes"]')
            )
        ).click()
        page.wait_for_page_load()

    def delete_homework(self, driver, title, description, periods, problems,
                        feedback, status):
        """Delete a homework assignment."""
        print('Delete Homework: %s' % title)
        self.remove[Assignment.HOMEWORK](
            driver=driver,
            title=title,
            description=None,
            periods=periods,
            problems=None,
            status=None
        )

    def delete_external(self, driver, title, description, periods,
                        assignment_url, status):
        """Delete an external assignment."""
        print('Delete External: %s' % title)
        self.remove[Assignment.EXTERNAL](
            driver=driver,
            title=title,
            description=None,
            periods=periods,
            problems=None,
            status=None
        )

    def delete_event(self, driver, title, description, periods, status):
        """Delete an event."""
        print('Delete Event: %s' % title)
        self.remove[Assignment.EVENT](
            driver=driver,
            title=title,
            description=None,
            periods=periods,
            problems=None,
            status=None
        )


if __name__ == '__main__':  # pragma: no cover
    # Test Assignment work
    initialization = Assignment
