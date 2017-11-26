#!/usr/bin/env python3
'''
wal - web automation layer.
Simple web automation using yaml syntax.
'''

import argparse
import os
import sys
import yaml
import time
import logging
import signal
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import *
from selenium.webdriver.common.action_chains import ActionChains


# Configuration for now
DEFAULT = {'homepage': 'http://about:blank',
           'screen_width': '1366',
           'screen_height': '768'}


class Interpreter(object):
    '''
    interprets commands from scripts and executes
    the corresponding functions
    '''

    def __init__(self, driver):
        '''
        sets up interpreter

        :param driver: - Selenium driver to use.
        '''

        self.driver = driver
        self.select = None
        self.commands = self.get_commands()


    def get_commands(self):
        '''
        creates a dictionary of command strings to functions
        '''

        return {'back': back,
                'backward': back,
                'backwards': back,
                'clear': clear,
                'click': click,
                'current_url': current_url,
                'deselect': deselect,
                'forward': forward,
                'forwards': forward,
                'foreach': foreach,
                'get': get,
                'go': get,
                'save_screenshot': save_screenshot,
                'screenshot': save_screenshot,
                'select': select,
                'select_by_class': select_by_class,
                'select_by_id': select_by_id,
                'select_by_name': select_by_name,
                'select_by_tagname': select_by_tagname,
                'select_by_value': select_by_value,
                'select_by_xpath': select_by_xpath,
                'send_keys': send_keys,
                'set_window_size': set_window_size,
                'sleep': _sleep_,
                'submit': submit}


    def execute(self, command):
        '''
        executes wal command and return string to be logged

        :param commands: str or list - commands to be ran
        '''

        # get command
        for item in command.keys():
            com = item

        # get argument
        argument = ''
        for item in command.values():
            argument = item

        # connect yaml commands to selenium driver commands
        if com in self.commands.keys():
            # execute command  with argument and return string for logging
            return self.commands[com](self, argument)


def back(wal, argument):
    '''
    go back one page
    '''

    wal.driver.back()
    return 'browser went back one page'


def clear(wal, argument):
    '''
    clears the driver's selection
    '''

    wal.driver.clear()
    wal.select = None

    return 'selection cleared'


def click(wal, argument):
    '''
    clicks argument or previously selected element
    if no argument was given
    '''

    if type(argument) == list:
        argument = argument[0]

    if type(argument) == str:

        # click selected item if no argument is given
        if len(argument) == 0:
            wal.driver.click(wal.select)

        wal.select = select_element(wal, argument)
        wal.driver.click(wal.select)

    return 'clicked %s' % wal.select


def current_url(wal, argument):
    '''
    returns current url
    '''

    return 'currently at: %s' % wal.driver.current_url


def deselect(wal, argument):
    '''
    deselects selections
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.driver.dselect_all()

    return 'delected selections'


def foreach(wal, argument):
    '''
    a statement used to iterate elements
    '''
    return_string = ''

    if type(argument) is list:
        for arg in argument:
            key = list(arg.keys())[0]
            value = list(arg.values())[0]

            if key == 'class':
                wal.select = wal.driver.find_element_by_class_name(value)
                class_name = value

            if key == 'print_href':
                print_href = True

        if class_name:
            if print_href:

                elements = wal.driver.find_elements_by_class_name(class_name)

                for element in elements:
                    return_string += '\n' + element.get_attribute('href')

                return return_string


def forward(wal, argument):
    '''
    go forward one page
    '''

    wal.driver.forward()
    return 'browser went forward one page'


def get(wal, argument):
    '''
    loads a web page
    '''

    if type(argument) is list:
        argument = argument[0]
    if type(argument) is str:
        wal.driver.get(argument)

    return 'loaded %s' % argument


def save_screenshot(wal, argument):
    '''
    saves a screenshot named by the argument

    :param argument: str - file name
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.driver.save_screenshot(argument)

    return 'saved a screenshot named %s' % argument


def select(wal, argument):
    '''
    select element by id, class, or name
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        if argument[:1] == '#':
            wal.select = wal.driver.find_element_by_id(argument[1:])
            return 'selected %s by id' % argument
        elif argument[:1] == '.':
            wal.select = wal.driver.find_element_by_class_name(argument[1:])
            return 'selected %s by class' % argument
        else:
            wal.select = wal.driver.find_element_by_name(argument)
            return 'selected %s by name' % argument
    else:
        return 'no argument %s to select' % argument


def select_by_class(wal, argument):
    '''
    select element by class
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_class_name(argument)

    return 'selected %s by class' % argument


def select_by_id(wal, argument):
    '''
    select by id
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_id(argument)

    return 'selected %s by id' % argument


def select_by_tagname(wal, argument):
    '''
    select by tagname
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_tagname(argument)

    return 'selected %s by tagname' % argument


def select_by_value(wal, argument):
    '''
    select by value
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_value(argument)

    return 'selected %s by value' % argument


def select_by_xpath(wal, argument):
    '''
    select by xpath
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_xpath(argument)

    return 'selected %s by xpath' % argument


def set_window_size(wal, argument):
    '''
    sets browser's windows size by string or list
    '''

    if type(argument) is list:
        wal.driver.set_window_size(int(argument[0]),
                               int(argument[1]))
        return 'set window size to %s by %s.' % (width, height)

    if type(argument) is str:
        seperator = argument.find('x')
        width = argument[0:seperator]
        height = argument[-(seperator - 1):]
        wal.driver.set_window_size(int(width), int(height))
        return 'set window size to %s by %s.' % (width, height)


def send_keys(wal, argument):
    '''
    send keys to seleceted element
    '''

    # TODO: add support for special keys
    if type(argument) is list:
        for arg in argument:
            wal.select.send_keys(argument)

    if type(argument) is str:
        wal.select.send_keys(argument)

    return 'sent %s to %s' % (argument, wal.select)


def select(wal, argument):
    '''
    select an element by id, class or name
    '''

    if argument[:1] == '#':
        return wal.driver.find_element_by_id(argument[1:])
    elif argument[:1] == '.':
        return wal.driver.find_element_by_class(argument[1:])
    else:
        return wal.driver.find_element_by_name(argument)


def select_by_name(wal, argument):
    '''
    select an element by name
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = wal.driver.find_element_by_name(argument)

    return 'selected element %s by name' % argument


def _sleep_(wal, argument):
    '''
    sleeps for the amount of seconds specified
    '''

    sleep_time = 0
    if type(argument) is list:
        argument = argument[0]

    try: 
        sleep_time = int(argument)
    except ValueError:
        pass
    time.sleep(int(sleep_time))

    return 'slept for: %s seconds' % sleep_time


def submit(wal, argument):
    '''
    execute the submit function of an element
    useful for submitting forms
    '''

    if type(argument) is None:
        if type(wal.select) is None:
            print('Error: submit: Nothing is selected.')
        try:
            wal.select.submit()
        except NoSuchElementException as error:
            return str(error)

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        wal.select = select_element(wal, argument)
        try:
            wal.select.submit()
        except NoSuchElementException as error:
            return str(error)
    try:
        wal.select.submit()
    except NoSuchElementException as error:
        return str(error)


def select_element(wal, argument):
    '''
    select element by id, class, or name
    '''

    if type(argument) is list:
        argument = argument[0]

    if type(argument) is str:
        if argument[:1] == '#':
            return wal.driver.find_element_by_id(argument[1:])
        elif argument[:1] == '.':
            return wal.driver.find_element_by_class_name(argument[1:])
        else:
            return wal.driver.find_element_by_name(argument)
    else:
        return None


def inspect(element):
    '''returns information about an html element:
         - tag
         - name
         - id
         - class
         - selenium id
    '''
    
    return ('        tag: <%s>', element.tag_name + 
            '       name: %s', element.get_attribute('name') + 
            '         id: %s', element.get_attribute('id') +
            '      class: %s', element.get_attribute('class') +
            'selenium_id: %s', element.id)


class Wal(object):
    '''
    web automation layer
    '''
    def __init__(self):
        '''
        Set up wal. Use -h to see available commands.
        '''

        self.args = self.parse_arguments()
        self.logger = self.setup_logger()
        self.driver = self.setup_web_driver()
        self.scripts = self.load_all_scripts()
        self.interpreter = Interpreter(self.driver)


    def parse_arguments(self):
        '''
        Parses command line arguments and returns the arguments

        for more information:
        https://docs.python.org/3/library/argparse.html
        '''

        # Define arguments
        parser = argparse.ArgumentParser(description=__doc__)
        argument = parser.add_argument
        argument('input_files',
                 default=sys.stdin,
                 nargs='*')
        argument('--verbose', '-v', action='count')

        return parser.parse_args()


    def setup_logger(self):
        '''
        return a logger with default values
        '''

        if self.args.verbose:
            if self.args.verbose >= 3:
                logging.basicConfig(level=logging.DEBUG)
            elif self.args.verbose == 2:
                logging.basicConfig(level=logging.INFO)
            elif self.args.verbose == 1:
                logging.basicConfig(level=logging.WARNING)
        else:
            logging.basicConfig(level=logging.CRITICAL)

        return logging.getLogger('wal')


    def setup_web_driver(self):
        '''
        returns a selenium web driver using PhantomJS and sensible defaults

        for more information:
        http://selenium-python.readthedocs.io/
        '''

        driver = webdriver.PhantomJS(service_log_path=os.path.devnull)
        driver.get(DEFAULT['homepage'])
        driver.set_window_size(DEFAULT['screen_width'],
                               DEFAULT['screen_height'])

        # add functions from ActionChains
        actions = ActionChains(driver)
        driver.click = actions.click
        driver.click_and_hold = actions.click_and_hold
        driver.context_click = actions.context_click
        driver.double_click = actions.double_click
        driver.drag_and_drop = actions.drag_and_drop
        driver.drag_and_drop_by_offset = actions.drag_and_drop_by_offset
        driver.key_down = actions.key_down
        driver.key_up = actions.key_up
        driver.move_by_offset = actions.move_by_offset
        driver.move_to_element = actions.move_to_element
        driver.move_to_element_with_offset = actions.move_to_element_with_offset
        driver.perform = actions.perform
        driver.release = actions.release
        driver.send_keys = actions.send_keys
        driver.send_keys_to_element = actions.send_keys_to_element

        return driver


    def load_all_scripts(self):
        '''
        return dict object of scripts
        '''

        scripts = []
        
        for script_name in self.args.input_files:
            scripts.append({script_name: self.load_script(script_name)})

        return scripts
        

    def load_script(self, script):
        '''
        loads the scripts and interprets the yaml content
        '''

        with open(script, 'r') as stream:
            try:
                commands = yaml.load(stream)
            except yaml.YAMLError as error:
                self.logger.error(error)

        return commands


    def run(self):
        '''
        uses interpreter to run commands
        '''

        try:
            for script in self.scripts:
                for script_name in script.keys():
                    line = '_' * 80
                    run_text = ('\n%s\n\nRunning script %s\n%s' %
                                (line, script_name, line))
                    self.logger.debug(run_text)
                    try:
                        for commands in script.values():
                            for com in commands:
                                self.logger.info(self.interpreter.execute(com))

                    except WebDriverException as error:
                        self.logger.error("Web Driver Error:" + str(error))
        finally:
            self.driver.service.process.send_signal(signal.SIGTERM)
            self.driver.quit()

        
def main():
    '''
    execute wal as a program when calling wal directly
    '''

    wal = Wal()
    wal.run()


if __name__ == "__main__":
    main()
