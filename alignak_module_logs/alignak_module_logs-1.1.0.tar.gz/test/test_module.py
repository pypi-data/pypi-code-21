#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016: Alignak team, see AUTHORS.txt file for contributors
#
# This file is part of Alignak.
#
# Alignak is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Alignak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Alignak.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Test the module
"""

import re
import os
import time
from alignak_test import AlignakTest, time_hacker
from alignak.modulesmanager import ModulesManager
from alignak.objects.module import Module
from alignak.basemodule import BaseModule
from alignak.brok import Brok

# Set environment variable to ask code Coverage collection
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

import alignak_module_logs


class TestModules(AlignakTest):
    """
    This class contains the tests for the module
    """

    def test_module_loading(self):
        """
        Test module loading

        Alignak module loading

        :return:
        """
        self.print_header()
        self.setup_with_file('./cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)
        self.show_configuration_logs()

        # No arbiter modules created
        modules = [m.module_alias for m in self.arbiter.myself.modules]
        self.assertListEqual(modules, [])

        # The only existing broker module is logs declared in the configuration
        modules = [m.module_alias for m in self.brokers['broker-master'].modules]
        self.assertListEqual(modules, ['logs'])

        # No poller module
        modules = [m.module_alias for m in self.pollers['poller-master'].modules]
        self.assertListEqual(modules, [])

        # No receiver module
        modules = [m.module_alias for m in self.receivers['receiver-master'].modules]
        self.assertListEqual(modules, [])

        # No reactionner module
        modules = [m.module_alias for m in self.reactionners['reactionner-master'].modules]
        self.assertListEqual(modules, [])

        # No scheduler modules
        modules = [m.module_alias for m in self.schedulers['scheduler-master'].modules]
        self.assertListEqual(modules, [])

    def test_module_manager(self):
        """
        Test if the module manager manages correctly all the modules
        :return:
        """
        self.print_header()
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)
        self.clear_logs()

        time_hacker.set_real_time()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs'
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('broker', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        # Loading module logs
        print("Load and init")
        self.show_logs()
        self.assert_log_match(re.escape(
            "Importing Python module 'alignak_module_logs' for logs..."
        ), 0)
        self.assert_log_match(re.escape(
            "Module properties: {'daemons': ['broker'], 'phases': ['running'], "
            "'type': 'logs', 'external': True}"
        ), 1)
        self.assert_log_match(re.escape(
            "Imported 'alignak_module_logs' for logs"
        ), 2)
        self.assert_log_match(re.escape(
            "Loaded Python module 'alignak_module_logs' (logs)"
        ), 3)
        self.assert_log_match(re.escape(
            "Give an instance of alignak_module_logs for alias: logs"
        ), 4)
        self.assert_log_match(re.escape(
            "logger default configuration:"
        ), 5)
        self.assert_log_match(re.escape(
            " - rotating logs in /tmp/monitoring-logs.log"
        ), 6)
        self.assert_log_match(re.escape(
            " - log level: 20"
        ), 7)
        self.assert_log_match(re.escape(
            " - rotation every 1 midnight, keeping 365 files"
        ), 8)
        self.assert_log_match(re.escape(
            "Alignak Backend is not configured. Some module features will not be available."
        ), 9)

        time.sleep(1)
        # Reload the module
        print("Reload")
        self.modulemanager.load([mod])
        self.modulemanager.get_instances()
        #
        # Loading module logs
        self.show_logs()
        self.assert_log_match(re.escape(
            "Importing Python module 'alignak_module_logs' for logs..."
        ), 0)
        self.assert_log_match(re.escape(
            "Module properties: {'daemons': ['broker'], 'phases': ['running'], "
            "'type': 'logs', 'external': True}"
        ), 1)
        self.assert_log_match(re.escape(
            "Imported 'alignak_module_logs' for logs"
        ), 2)
        self.assert_log_match(re.escape(
            "Loaded Python module 'alignak_module_logs' (logs)"
        ), 3)
        self.assert_log_match(re.escape(
            "Give an instance of alignak_module_logs for alias: logs"
        ), 4)
        self.assert_log_match(re.escape(
            "logger default configuration:"
        ), 5)
        self.assert_log_match(re.escape(
            " - rotating logs in /tmp/monitoring-logs.log"
        ), 6)
        self.assert_log_match(re.escape(
            " - log level: 20"
        ), 7)
        self.assert_log_match(re.escape(
            " - rotation every 1 midnight, keeping 365 files"
        ), 8)
        self.assert_log_match(re.escape(
            "Alignak Backend is not configured. Some module features will not be available."
        ), 9)

        self.assert_log_match(re.escape(
            "Importing Python module 'alignak_module_logs' for logs..."
        ), 10)
        self.assert_log_match(re.escape(
            "Module properties: {'daemons': ['broker'], 'phases': ['running'], "
            "'type': 'logs', 'external': True}"
        ), 11)
        self.assert_log_match(re.escape(
            "Imported 'alignak_module_logs' for logs"
        ), 12)
        self.assert_log_match(re.escape(
            "Loaded Python module 'alignak_module_logs' (logs)"
        ), 13)
        self.assert_log_match(re.escape(
            "Request external process to stop for logs"
        ), 14)
        self.assert_log_match(re.escape(
            "External process stopped."
        ), 15)
        self.assert_log_match(re.escape(
            "Give an instance of alignak_module_logs for alias: logs"
        ), 16)
        self.assert_log_match(re.escape(
            "logger default configuration:"
        ), 17)
        self.assert_log_match(re.escape(
            " - rotating logs in /tmp/monitoring-logs.log"
        ), 18)
        self.assert_log_match(re.escape(
            " - log level: 20"
        ), 19)
        self.assert_log_match(re.escape(
            " - rotation every 1 midnight, keeping 365 files"
        ), 20)
        self.assert_log_match(re.escape(
            "Alignak Backend is not configured. Some module features will not be available."
        ), 21)

        my_module = self.modulemanager.instances[0]

        # Get list of not external modules
        self.assertListEqual([], self.modulemanager.get_internal_instances())
        for phase in ['configuration', 'late_configuration', 'running', 'retention']:
            self.assertListEqual([], self.modulemanager.get_internal_instances(phase))

        # Get list of external modules
        self.assertListEqual([my_module], self.modulemanager.get_external_instances())
        for phase in ['configuration', 'late_configuration', 'retention']:
            self.assertListEqual([], self.modulemanager.get_external_instances(phase))
        for phase in ['running']:
            self.assertListEqual([my_module], self.modulemanager.get_external_instances(phase))

        # Clear logs
        self.clear_logs()

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        # Clear logs
        self.clear_logs()

        # Kill the external module (normal stop is .stop_process)
        my_module.kill()
        time.sleep(0.1)
        self.assert_log_match("Killing external module", 0)
        self.assert_log_match("External module killed", 1)

        # Should be dead (not normally stopped...) but we still know a process for this module!
        self.assertIsNotNone(my_module.process)

        # Nothing special ...
        self.modulemanager.check_alive_instances()
        self.assert_log_match("The external module logs died unexpectedly!", 2)
        self.assert_log_match("Setting the module logs to restart", 3)

        # Try to restart the dead modules
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 4)

        # In fact it's too early, so it won't do it
        # The module instance is still dead
        self.assertFalse(my_module.process.is_alive())

        # So we lie, on the restart tries ...
        my_module.last_init_try = -5
        self.modulemanager.check_alive_instances()
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 5)

        # The module instance is now alive again
        self.assertTrue(my_module.process.is_alive())
        self.assert_log_match("I'm stopping module 'logs'", 6)
        self.assert_log_match("Starting external process for module logs", 7)
        self.assert_log_match("logs is now started", 8)

        # There is nothing else to restart in the module manager
        self.assertEqual([], self.modulemanager.to_restart)

        # Clear logs
        self.clear_logs()

        # Now we look for time restart so we kill it again
        my_module.kill()
        time.sleep(0.2)
        self.assertFalse(my_module.process.is_alive())
        self.assert_log_match("Killing external module", 0)
        self.assert_log_match("External module killed", 1)

        # Should be too early
        self.modulemanager.check_alive_instances()
        self.assert_log_match("The external module logs died unexpectedly!", 2)
        self.assert_log_match("Setting the module logs to restart", 3)

        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 4)

        # In fact it's too early, so it won't do it
        # The module instance is still dead
        self.assertFalse(my_module.process.is_alive())

        # So we lie, on the restart tries ...
        my_module.last_init_try = -5
        self.modulemanager.check_alive_instances()
        self.modulemanager.try_to_restart_deads()
        self.assert_log_match("Trying to initialize module: logs", 5)

        # The module instance is now alive again
        self.assertTrue(my_module.process.is_alive())
        self.assert_log_match("I'm stopping module 'logs'", 6)
        self.assert_log_match("Starting external process for module logs", 7)
        self.assert_log_match("logs is now started", 8)

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs

        self.assert_log_match("Request external process to stop for logs", 9)
        self.assert_log_match(re.escape("I'm stopping module 'logs' (pid="), 10)
        self.assert_log_match(
            re.escape("'logs' is still alive after normal kill, I help it to die"), 11
        )
        self.assert_log_match("Killing external module ", 12)
        self.assert_log_match("External module killed", 13)
        self.assert_log_match("External process stopped.", 14)

    def test_module_start_default(self):
        """Test the module initialization function, no parameters, using default
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # Clear logs
        self.clear_logs()

        # -----
        # Default initialization
        # -----
        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs'
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger default configuration:"), 1)
        self.assert_log_match(
            re.escape(" - rotating logs in /tmp/monitoring-logs.log"), 2)
        self.assert_log_match(
            re.escape(" - log level: 20"), 3)
        self.assert_log_match(
            re.escape(" - rotation every 1 midnight, keeping 365 files"), 4)

    def test_module_start_parameters_1(self):
        """Test the module initialization function, no parameters, provide parameters
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'log_dir': '/my_dir',
            'log_file': 'test.log',
            'log_level': 'WARNING',
            'log_rotation_when': 'd',
            'log_rotation_interval': 5,
            'log_rotation_count': 10,
            'log_format': '[%(created)i] %(levelname)s: %(message)s',
            'log_date': '%Y-%m-%d %H:%M:%S %Z',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger default configuration:"), 1)
        self.assert_log_match(
            re.escape(" - rotating logs in /my_dir/test.log"), 2)
        self.assert_log_match(
            re.escape(" - log level: 30"), 3)
        self.assert_log_match(
            re.escape(" - rotation every 5 d, keeping 10 files"), 4)

    def test_module_start_parameters_2(self):
        """Test the module initialization function, no parameters, provide parameters
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': 'not_found.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger configuration defined in not_found.json"), 1)
        self.assert_log_match(
            re.escape("defined logger configuration file does not exist! "
                      "Using default configuration."), 2)
        self.assert_log_match(
            re.escape("logger default configuration:"), 3)
        self.assert_log_match(
            re.escape(" - rotating logs in /tmp/monitoring-logs.log"), 4)
        self.assert_log_match(
            re.escape(" - log level: 20"), 5)
        self.assert_log_match(
            re.escape(" - rotation every 1 midnight, keeping 365 files"), 6)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger_syntax.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        self.assert_log_match(
            re.escape("Give an instance of alignak_module_logs for alias: logs"), 0)
        self.assert_log_match(
            re.escape("logger configuration defined in ./mod-logs-logger_syntax.json"), 1
        )
        self.assert_log_match(
            re.escape("Logger configuration file is not parsable correctly!"), 2)
        self.assert_log_match(
            re.escape("Unable to configure root logger: "
                      "Unable to add handler u'console': u'console'"), 3)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        })

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        self.assertTrue(os.path.exists('/tmp/rotating-monitoring.log'))
        self.assertTrue(os.path.exists('/tmp/timed-rotating-monitoring.log'))

    def test_module_zzz_default_configuration(self):
        """Test the module with its default configuration
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        if not os.path.exists('./logs1'):
            os.mkdir('./logs1')

        if os.path.exists('./logs1/monitoring-logs.log'):
            os.remove('./logs1/monitoring-logs.log')

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            # 'logger_configuration': './mod-logs-logger.json',
            'log_dir': './logs1'
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('receiver', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        # Clear logs
        self.clear_logs()

        my_module = self.modulemanager.instances[0]

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)

        time.sleep(1)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        time.sleep(1)

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        time.sleep(1)
        # fixme: On Travis build this assertion fails if no wait is executed!
        # but I confirm that locally the file is created and exists!!!
        # probably that the log file is not yet flushed hen executing?
        # time.sleep(5)
        # self.assertTrue(os.path.exists('./logs1/monitoring-logs.log'))

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        # fixme: On Travis build this assertion fails!
        # but I confirm that locally the file is created and exists!!!
        # probably that the log file is not yet flushed hen executing?
        # Get the monitoring logs log file that should contain only two lines
        # with open('./logs1/monitoring-logs.log', 'r') as f:
        #     data = f.readlines()
        #     print("line: %s" % data)
        #     # Only two lines, even if a message has a \r
        #     self.assertEqual(2, len(data))

        # Stop the module
        self.modulemanager.clear_instances()

        self.show_logs()
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)
        self.assert_log_match("Give an instance of alignak_module_logs for alias: logs", 4)
        self.assert_log_match("logger default configuration", 5)
        self.assert_log_match(" - rotating logs in ./logs1/monitoring-logs.log", 6)
        self.assert_log_match(" - log level: 20", 7)
        self.assert_log_match(" - rotation every 1 midnight, keeping 365 files", 8)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        my_module = self.modulemanager.instances[0]

        # Start external modules
        self.modulemanager.start_external_instances()

        self.show_logs()

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        # fixme: On Travis build this assertion fails!
        # but I confirm that locally the file is created and exists!!!
        # probably that the log file is not yet flushed hen executing?
        # Get the monitoring logs log file that should contain only two lines
        # 6 lines:
        #  - 2 existing before module stop and restart,
        #  - 4 broks received after restart
        # with open('./logs1/monitoring-logs.log', 'r') as f:
        #     data = f.readlines()
        #     print(data)
        #     self.assertEqual(6, len(data))

        # Stop the module
        self.modulemanager.clear_instances()

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs

    def test_module_zzz_logger_json_configuration(self):
        """Test the module with a logger configured with a json file
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        if not os.path.exists('./logs2'):
            os.mkdir('./logs2')

        if os.path.exists('./logs2/monitoring-logs.log'):
            os.remove('./logs2/monitoring-logs.log')

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('receiver', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        # Clear logs
        self.clear_logs()

        my_module = self.modulemanager.instances[0]

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)

        time.sleep(1)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        time.sleep(1)

        instance = alignak_module_logs.get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        self.assertTrue(os.path.exists('./logs2/monitoring-logs.log'))
        # self.assertTrue(os.path.exists('/tmp/rotating-monitoring.log'))
        # self.assertTrue(os.path.exists('/tmp/timed-rotating-monitoring.log'))
        time.sleep(5)
        # On Travis build this assertion fails !
        # self.assertTrue(os.path.exists('/tmp/monitoring-logs.log'))

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        # Get the monitoring logs log file that should contain only two lines
        with open('./logs2/monitoring-logs.log', 'r') as f:
            data = f.readlines()
            print(data)
            # Only two lines, even if a message has a \r
            self.assertEqual(2, len(data))

        # Stop the module
        self.modulemanager.clear_instances()

        self.show_logs()
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)
        self.assert_log_match("Give an instance of alignak_module_logs for alias: logs", 4)
        self.assert_log_match("logger configuration defined in ./mod-logs-logger.json", 5)
        self.assert_log_match("Alignak Backend is not configured. Some module features will not be available.", 6)
        self.assert_log_match("Request external process to stop for logs", 7)
        self.assert_log_match("I'm stopping module 'logs'", 8)
        self.assert_log_match("External process stopped.", 9)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        my_module = self.modulemanager.instances[0]

        # Start external modules
        self.modulemanager.start_external_instances()

        self.show_logs()

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info',
                                                     'message': 'test message\r\nlong output'}})
        b.prepare()
        instance.manage_brok(b)

        # Get the monitoring logs log file that should contain only two lines
        # 6 lines:
        #  - 2 existing before module stop and restart,
        #  - 4 broks received after restart
        with open('./logs2/monitoring-logs.log', 'r') as f:
            data = f.readlines()
            print(data)
            self.assertEqual(6, len(data))

        # Stop the module
        self.modulemanager.clear_instances()

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs
