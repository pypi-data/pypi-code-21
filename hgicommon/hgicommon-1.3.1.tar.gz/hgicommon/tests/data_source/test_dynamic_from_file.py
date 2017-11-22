"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import logging
import os
import shutil
import unittest
from tempfile import mkdtemp, mkstemp
from unittest.mock import MagicMock, call

from hgicommon.data_source.dynamic_from_file import register, unregister
from hgicommon.data_source.dynamic_from_file import registration_event_listenable_map
from hgicommon.models import RegistrationEvent
from hgicommon.tests.data_source._stubs import StubRegisteringDataSource


class TestRegister(unittest.TestCase):
    """
    Tests for `register` and `unregister`.
    """
    def tearDown(self):
        listeners = registration_event_listenable_map[int].get_listeners()
        for listener in listeners:
            registration_event_listenable_map[int].remove_listener(listener)

    def test_register(self):
        listener_1 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_1)
        listener_2 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_2)

        register(123)
        update_1 = RegistrationEvent(123, RegistrationEvent.Type.REGISTERED)
        listener_1.assert_called_once_with(update_1)
        listener_1.reset_mock()
        listener_2.assert_called_once_with(update_1)
        listener_2.reset_mock()

    def test_unregister(self):
        listener_1 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_1)
        listener_2 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_2)

        unregister(123)
        update_1 = RegistrationEvent(123, RegistrationEvent.Type.UNREGISTERED)
        listener_1.assert_called_once_with(update_1)
        listener_1.reset_mock()
        listener_2.assert_called_once_with(update_1)
        listener_2.reset_mock()

    def test_register_can_be_unsubscribed(self):
        listener_1 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_1)
        listener_2 = MagicMock()
        registration_event_listenable_map[int].add_listener(listener_2)

        register(123)
        update_1 = RegistrationEvent(123, RegistrationEvent.Type.REGISTERED)
        registration_event_listenable_map[int].remove_listener(listener_2)

        register(456)
        unregister(456)

        listener_2.assert_called_once_with(update_1)


class TestRegisteringDataSource(unittest.TestCase):
    """
    Tests for `RegisteringDataSource`.
    """
    def setUp(self):
        self.temp_directory = mkdtemp(suffix=TestRegisteringDataSource.__name__)
        self.source = StubRegisteringDataSource(self.temp_directory, int)
        self.source.is_data_file = MagicMock(return_value=True)

    def tearDown(self):
        self.source.stop()
        shutil.rmtree(self.temp_directory)

        listenable = registration_event_listenable_map[int]
        for listener in listenable.get_listeners():
            listenable.remove_listener(listener)

    def test_extract_data_from_file(self):
        listener = MagicMock()
        registration_event_listenable_map[int].add_listener(listener)

        rule_file_location = self._create_data_file_in_temp_directory()
        with open(rule_file_location, 'w') as file:
            file.write("from hgicommon.data_source import register\n"
                       "register(123)\n"
                       "register(456)")

        loaded = self.source.extract_data_from_file(rule_file_location)

        listener.assert_has_calls([
            call(RegistrationEvent(123, RegistrationEvent.Type.REGISTERED)),
            call(RegistrationEvent(456, RegistrationEvent.Type.REGISTERED))
        ])
        self.assertEqual(loaded, [123, 456])

    def test_extract_data_from_file_with_corrupted_file(self):
        rule_file_location = self._create_data_file_in_temp_directory()
        with open(rule_file_location, 'w') as file:
            file.write("~")

        logging.root.setLevel(level=logging.ERROR)
        self.assertRaises(Exception, self.source.extract_data_from_file, rule_file_location)

    def test_extract_data_from_file_with_wrong_file_extension(self):
        rule_file_location = self._create_data_file_in_temp_directory()
        new_rule_file_location = rule_file_location + "c"
        os.rename(rule_file_location, new_rule_file_location)

        logging.root.setLevel(level=logging.ERROR)
        self.assertRaises(Exception, self.source.extract_data_from_file, new_rule_file_location)

    def _create_data_file_in_temp_directory(self) -> str:
        """
        Creates a data file in the temp directory used by this test.
        :return: the file path of the created file
        """
        temp_file_location = mkstemp()[1]
        rule_file_location = "%s.py" % temp_file_location
        os.rename(temp_file_location, rule_file_location)
        return rule_file_location


if __name__ == "__main__":
    unittest.main()
