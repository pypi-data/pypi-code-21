# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
The module containing the classes describing the targets.
"""

from abc import ABCMeta, abstractmethod
from collections import deque, namedtuple, Sequence

import fastr
from fastr.core.baseplugin import Plugin
from fastr.core.pluginmanager import PluginSubManager

SystemUsageInfo = namedtuple('SystemUsageInfo', ['timestamp',
                                                 'cpu_percent',
                                                 'vmem',
                                                 'rmem',
                                                 'read_bytes',
                                                 'write_bytes'])


class ProcessUsageCollection(Sequence):
    # It has to be defined in module for pickling purposes
    usage_type = SystemUsageInfo

    def __init__(self):
        self.seconds_info = deque()
        self.minutes_info = []

    def __len__(self):
        return len(self.seconds_info) + len(self.minutes_info)

    def __getitem__(self, item):
        # First look in minutes, then in seconds
        if item < len(self.minutes_info):
            return self.minutes_info[item]._asdict()
        else:
            return self.seconds_info[item - len(self.minutes_info)]._asdict()

    def append(self, value):
        if not isinstance(value, self.usage_type):
            raise ValueError('Cannot add a non {}.usage_type'.format(type(self).__name__))

        self.seconds_info.append(value)

        if len(self.seconds_info) >= 120:
            self.aggregate(60)

    def aggregate(self, number_of_points):
        oldest_data = [self.seconds_info.popleft() for _ in range(number_of_points)]

        timestamp = oldest_data[-1].timestamp
        cpu_percent = sum(x.cpu_percent for x in oldest_data) / len(oldest_data)
        vmem = max(x.vmem for x in oldest_data)
        rmem = max(x.rmem for x in oldest_data)
        read_bytes = oldest_data[-1].read_bytes
        write_bytes = oldest_data[-1].write_bytes

        self.minutes_info.append(self.usage_type(timestamp=timestamp,
                                                 cpu_percent=cpu_percent,
                                                 vmem=vmem,
                                                 rmem=rmem,
                                                 read_bytes=read_bytes,
                                                 write_bytes=write_bytes))


class Target(Plugin):
    """
    The abstract base class for all targets. Execution with a target should
    follow the following pattern:

    >>> with Target() as target:
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])
    ...     target.run_commmand(['sleep', '10'])

    The Target context operator will set the correct paths/initialization.
    Within the context command can be ran and when leaving the context the
    target reverts the state before.
    """
    __metaclass__ = ABCMeta

    # Monitor interval for profiling
    _MONITOR_INTERVAL = 1.0

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment where needed
        """

    @abstractmethod
    def run_command(self, command):
        pass

    @classmethod
    def test(cls):
        """
        Test the plugin, interfaces do not need to be tested on import
        """
        pass


class TargetManager(PluginSubManager):
    """
    Container holding all the ExecutionPlugins known to the Fastr system
    """

    def __init__(self):
        """
        Initialize a ExecutionPluginManager and load plugins.

        :param path: path to search for plugins
        :param recursive: flag for searching recursively
        :return: newly created ExecutionPluginManager
        """
        super(TargetManager, self).__init__(parent=fastr.plugin_manager,
                                            plugin_class=Target)


