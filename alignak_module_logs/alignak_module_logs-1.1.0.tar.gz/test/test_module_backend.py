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
Test the module with an lignak backend connection
"""

import os
import time
import shlex
import subprocess

import requests

from alignak_test import AlignakTest
from alignak.modulesmanager import ModulesManager
from alignak.objects.module import Module
from alignak.basemodule import BaseModule
from alignak.brok import Brok

from alignak_backend_client.client import Backend

# Set environment variable to ask code Coverage collection
os.environ['COVERAGE_PROCESS_START'] = '.coveragerc'

from alignak_module_logs.logs import get_instance
from alignak_module_logs.logevent import LogEvent


class TestModuleConnection(AlignakTest):

    @classmethod
    def setUpClass(cls):

        # Set test mode for alignak backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-module-logs-backend-test'

        # Delete used mongo DBs
        print ("Deleting Alignak backend DB...")
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        cls.p = subprocess.Popen(['uwsgi', '--plugin', 'python', '-w', 'alignakbackend:app',
                                  '--socket', '0.0.0.0:5000',
                                  '--protocol=http', '--enable-threads', '--pidfile',
                                  '/tmp/uwsgi.pid'])
        time.sleep(3)

        endpoint = 'http://127.0.0.1:5000'

        # Backend authentication
        headers = {'Content-Type': 'application/json'}
        params = {'username': 'admin', 'password': 'admin', 'action': 'generate'}
        # Get admin user token (force regenerate)
        response = requests.post(endpoint + '/login', json=params, headers=headers)
        resp = response.json()
        cls.token = resp['token']
        cls.auth = requests.auth.HTTPBasicAuth(cls.token, '')

        # Get admin user
        response = requests.get(endpoint + '/user', auth=cls.auth)
        resp = response.json()
        cls.user_admin = resp['_items'][0]

        # Get realms
        response = requests.get(endpoint + '/realm', auth=cls.auth)
        resp = response.json()
        cls.realmAll_id = resp['_items'][0]['_id']

        # Add a user
        data = {'name': 'test', 'password': 'test', 'back_role_super_admin': False,
                'host_notification_period': cls.user_admin['host_notification_period'],
                'service_notification_period': cls.user_admin['service_notification_period'],
                '_realm': cls.realmAll_id}
        response = requests.post(endpoint + '/user', json=data, headers=headers,
                                 auth=cls.auth)
        resp = response.json()
        print("Created a new user: %s" % resp)

    @classmethod
    def tearDownClass(cls):
        cls.p.kill()

    def test_connection_accepted(self):
        """ Test module backend connection accepted """
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'alignak_backend': 'http://127.0.0.1:5000',
            'username': 'admin',
            'password': 'admin',
        }))
        self.assertTrue(mod.backend_available)

    def test_connection_refused(self):
        """ Test module backend connection refused """
        # No backend data defined
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
        }))
        self.assertFalse(mod.backend_available)

        # Backend bad URL
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'alignak_backend': 'http://bad_url',
            'username': 'admin',
            'password': 'admin',
        }))
        self.assertFalse(mod.backend_available)

        # Backend refused login
        mod = get_instance(Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'alignak_backend': 'http://127.0.0.1:5000',
            'username': 'fake',
            'password': 'fake',
        }))
        self.assertFalse(mod.backend_available)

    def test_module_zzz_get_logs(self):
        """
        Test the module log collection functions
        :return:
        """
        self.print_header()
        # Obliged to call to get a self.logger...
        self.setup_with_file('cfg/cfg_default.cfg')
        self.assertTrue(self.conf_is_correct)

        # -----
        # Provide parameters - logger configuration file (exists)
        # -----
        # Clear logs
        self.clear_logs()

        if not os.path.exists('./logs2'):
            os.mkdir('./logs2')

        if os.path.exists('./logs2/monitoring-logs.log'):
            os.remove('./logs2/monitoring-logs.log')

        if os.path.exists('./logs2/rotating-monitoring.log'):
            os.remove('./logs2/rotating-monitoring.log')

        if os.path.exists('./logs2/timed-rotating-monitoring.log'):
            os.remove('./logs2/timed-rotating-monitoring.log')

        # Create an Alignak module
        mod = Module({
            'module_alias': 'logs',
            'module_types': 'logs',
            'python_name': 'alignak_module_logs',
            'logger_configuration': './mod-logs-logger.json',
            'alignak_backend': 'http://127.0.0.1:5000',
            'username': 'admin',
            'password': 'admin',
        })

        # Create the modules manager for a daemon type
        self.modulemanager = ModulesManager('broker', None)

        # Load an initialize the modules:
        #  - load python module
        #  - get module properties and instances
        self.modulemanager.load_and_init([mod])

        my_module = self.modulemanager.instances[0]

        # Clear logs
        self.clear_logs()

        # Start external modules
        self.modulemanager.start_external_instances()

        # Starting external module logs
        self.assert_log_match("Trying to initialize module: logs", 0)
        self.assert_log_match("Starting external module logs", 1)
        self.assert_log_match("Starting external process for module logs", 2)
        self.assert_log_match("logs is now started", 3)
        # self.assert_log_match("Process for module logs is now running", 4)

        time.sleep(1)

        # Check alive
        self.assertIsNotNone(my_module.process)
        self.assertTrue(my_module.process.is_alive())

        time.sleep(1)

        instance = get_instance(mod)
        self.assertIsInstance(instance, BaseModule)

        # No more logs because the logger got re-configured... but some files exist
        time.sleep(1)
        # fixme: On Travis build this assertion fails if no wait is executed!
        # but I confirm that locally the file is created and exists!!!
        # probably that the log file is not yet flushed hen executing?
        time.sleep(5)
        self.assertTrue(os.path.exists('./logs2/monitoring-logs.log'))

        # Unknown brok type
        b = Brok({'type': 'unknown', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        assert False == instance.manage_brok(b)

        # Unknown log level
        b = Brok({'type': 'monitoring_log', 'data': {'level': 'unknown', 'message': 'test message'}})
        b.prepare()
        assert False == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {'level': 'info', 'message': 'test message'}})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'TIMEPERIOD TRANSITION: 24x7;-1;1'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'RETENTION LOAD: scheduler'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'RETENTION SAVE: scheduler'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'SERVICE ALERT: cogny;Load;OK;HARD;4;OK - load average: 0.74, 0.89, 1.03'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'warning',
            'message': 'SERVICE NOTIFICATION: admin;localhost;check-ssh;'
                       'CRITICAL;notify-service-by-email;Connection refused'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'CURRENT SERVICE STATE: lachassagne;Zombies;'
                       'OK;HARD;1;PROCS OK: 0 processes with STATE = Z'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'ACKNOWLEDGE_HOST_PROBLEM;pi2;2;1;1;admin;Acknowledge requested from WebUI'
        }})
        b.prepare()
        assert True == instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'SERVICE DOWNTIME ALERT: cogny;CPU;STARTED; '
                       'Service has entered a period of scheduled downtime'
        }})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': 'SERVICE FLAPPING ALERT: lachassagne;I/O stats disk 2;STARTED; '
                       'Service appears to have started flapping (51.6% change >= 50.0% threshold)'
        }})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': "ACTIVE SERVICE CHECK: localhost;Nrpe-status;OK;HARD;1;NRPE v2.15"
        }})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': "PASSIVE SERVICE CHECK: localhost;nsca_uptime;0;OK: uptime: 02:38h, "
                       "boot: 2017-08-31 06:18:03 (UTC)|'uptime'=9508s;2100;90000"
        }})
        b.prepare()
        instance.manage_brok(b)

        b = Brok({'type': 'monitoring_log', 'data': {
            'level': 'info',
            'message': "SERVICE COMMENT: pi2;load;alignak;Service comment"
        }})
        b.prepare()
        instance.manage_brok(b)

        # Get log file that should contain one line
        with open('./logs2/monitoring-logs.log', 'r') as f:
            data = f.readlines()
        print("Read data: %s" % data)
        self.assertEqual(13, len(data))
        logs = []
        for line in data:
            line = line.replace('ERROR: ', '')
            line = line.replace('WARNING: ', '')
            line = line.replace('INFO: ', '')
            logs.append(line)

        assert 'test message' in data[0]
        assert 'TIMEPERIOD' in data[1]
        assert 'RETENTION LOAD' in data[2]
        assert 'RETENTION SAVE' in data[3]
        assert 'SERVICE ALERT: cogny;Load;OK;HARD;4;OK - load average: 0.74, 0.89, 1.03' in data[4]
        assert 'SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
               'CRITICAL;notify-service-by-email;Connection refused' in data[5]
        assert 'CURRENT SERVICE STATE: lachassagne;Zombies;' \
                'OK;HARD;1;PROCS OK: 0 processes with STATE = Z' in data[6]
        assert 'ACKNOWLEDGE_HOST_PROBLEM;pi2;2;1;1;admin;' \
               'Acknowledge requested from WebUI' in data[7]
        assert 'SERVICE DOWNTIME ALERT: cogny;CPU;STARTED' in data[8]
        assert 'SERVICE FLAPPING ALERT: lachassagne;I/O stats disk 2;STARTED' in data[9]
        assert 'ACTIVE SERVICE CHECK: localhost;Nrpe-status;OK;HARD;1;NRPE v2.15' in data[10]
        assert "PASSIVE SERVICE CHECK: localhost;nsca_uptime;0;OK: uptime: 02:38h, " \
               "boot: 2017-08-31 06:18:03 (UTC)|'uptime'=9508s;2100;90000" in data[11]
        assert "SERVICE COMMENT: pi2;load;alignak;Service comment" in data[12]

        log = logs[2]
        log = log[13:]
        log = '[1480152711] ' + log
        print log
        log = '[1402515279] SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
              'CRITICAL;notify-service-by-email;Connection refused'
        expected = {
            'hostname': 'localhost',
            'event_type': 'NOTIFICATION',
            'service_desc': 'check-ssh',
            'state': 'CRITICAL',
            'contact': 'admin',
            'time': 1402515279,
            'notification_method': 'notify-service-by-email',
            'notification_type': 'SERVICE',
            'output': 'Connection refused',
        }
        event = LogEvent(log)
        print event
        assert event.valid
        assert event.data == expected

        # And we clear all now
        self.modulemanager.stop_all()
        # Stopping module logs

        # Get backend history for the monitoring logs
        backend = Backend('http://127.0.0.1:5000')
        backend.login("admin", "admin", "force")

        r = backend.get('history')
        for item in r['_items']:
            print("- %s" % item)
        self.assertEqual(len(r['_items']), 6)

        assert r['_items'][0]['host_name'] == 'n/a'
        assert r['_items'][0]['service_name'] == 'n/a'
        assert r['_items'][0]['type'] == 'monitoring.timeperiod_transition'
        assert r['_items'][0]['message'] == 'TIMEPERIOD TRANSITION: 24x7;-1;1'

        assert r['_items'][1]['host_name'] == 'cogny'
        assert r['_items'][1]['service_name'] == 'Load'
        assert r['_items'][1]['type'] == 'monitoring.alert'
        assert r['_items'][1]['message'] == 'SERVICE ALERT: cogny;Load;OK;HARD;4;' \
                                            'OK - load average: 0.74, 0.89, 1.03'

        assert r['_items'][2]['host_name'] == 'localhost'
        assert r['_items'][2]['service_name'] == 'check-ssh'
        assert r['_items'][2]['type'] == 'monitoring.notification'
        assert r['_items'][2]['message'] == 'SERVICE NOTIFICATION: admin;localhost;check-ssh;' \
                                            'CRITICAL;notify-service-by-email;Connection refused'

        assert r['_items'][3]['host_name'] == 'cogny'
        assert r['_items'][3]['service_name'] == 'CPU'
        assert r['_items'][3]['type'] == 'monitoring.downtime_start'
        assert r['_items'][3]['message'] == 'SERVICE DOWNTIME ALERT: cogny;CPU;STARTED; ' \
                                            'Service has entered a period of scheduled downtime'

        assert r['_items'][4]['host_name'] == 'lachassagne'
        assert r['_items'][4]['service_name'] == 'I/O stats disk 2'
        assert r['_items'][4]['type'] == 'monitoring.flapping_start'
        assert r['_items'][4]['message'] == 'SERVICE FLAPPING ALERT: lachassagne;I/O stats disk 2;' \
                                            'STARTED; Service appears to have started flapping ' \
                                            '(51.6% change >= 50.0% threshold)'

        assert r['_items'][5]['host_name'] == 'pi2'
        assert r['_items'][5]['service_name'] == 'load'
        assert r['_items'][5]['user_name'] == 'alignak'
        assert r['_items'][5]['type'] == 'webui.comment'
        assert r['_items'][5]['message'] == 'Service comment'

        # Note that RETENTION, CURRENT STATE, and CHECKS monitoring log
        # are not stored as events in the Alignak backend!
