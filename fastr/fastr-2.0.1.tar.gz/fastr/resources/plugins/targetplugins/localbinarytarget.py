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

import datetime
import os
import platform
import psutil
import subprocess
import time
import threading
import shellescape
import sys

import fastr
from fastr import exceptions
from fastr.core.target import Target, ProcessUsageCollection
from fastr.data import url

# Check if environment modules are available
try:
    from fastr.execution.environmentmodules import EnvironmentModules
    ENVIRONMENT_MODULES = EnvironmentModules(fastr.config.protected_modules)
    ENVIRONMENT_MODULES_LOADED = True
except exceptions.FastrValueError:
    ENVIRONMENT_MODULES = None
    ENVIRONMENT_MODULES_LOADED = False


class LocalBinaryTarget(Target):
    """
    A tool target that is a local binary on the system. Can be found using
    environmentmodules or a path on the executing machine. A local binary
    target has a number of fields that can be supplied:

    * ``binary (required)``: the name of the binary/script to call, can also be called ``bin``
      for backwards compatibility.
    * ``modules``: list of modules to load, this can be environmentmodules or lmod
      modules. If modules are given, the ``paths``, ``environment_variables`` and ``initscripts``
      are ignored.
    * ``paths``: a list of paths to add following the structure ``{"value": "/path/to/dir", "type": "bin"}``.
      The types can be ``bin`` if the it should be added to $PATH or ``lib`` if it should be
      added to te library path (e.g. $LD_LIBRARY_PATH for linux).
    * ``environment_variables``: a dictionary of environment variables to set.
    * ``initscript``: a list of script to run before running the main tool
    * ``interpreter``: the interpreter to use to call the binary e.g. ``python``

    The LocalBinaryTarget will first check if there are modules given and the module subsystem is loaded.
    If that is the case it will simply unload all current modules and load the given modules. If not it
    will try to set up the environment itself by using the following steps:

    1. Prepend the bin paths to $PATH
    2. Prepend the lib paths to the correct environment variable
    3. Setting the other environment variables given ($PATH and the system
       library path are ignored and cannot be set that way)
    4. Call the initscripts one by one

    The definition of the target in JSON is very straightforward:

    .. code-block:: json

        {
          "binary": "bin/test.py",
          "interpreter": "python",
          "paths": [
            {
              "type": "bin",
              "value": "vfs://apps/test/bin"
            },
            {
              "type": "lib",
              "value": "./lib"
            }
          ],
          "environment_variables": {
            "othervar": 42,
            "short_var": 1,
            "testvar": "value1"
          },
          "initscripts": [
            "bin/init.sh"
          ],
          "modules": ["elastix/4.8"]
        }

    In XML the definition would be in the form of:

   .. code-block:: xml

        <target os="linux" arch="*" modules="elastix/4.8" bin="bin/test.py" interpreter="python">
          <paths>
            <path type="bin" value="vfs://apps/test/bin" />
            <path type="lib" value="./lib" />
          </paths>
          <environment_variables short_var="1">
            <testvar>value1</testvar>
            <othervar>42</othervar>
          </environment_variables>
          <initscripts>
            <initscript>bin/init.sh</initscript>
          </initscripts>
        </target>
    """

    DYNAMIC_LIBRARY_PATH_DICT = {
        'windows': 'PATH',  # Not Tested
        'linux': 'LD_LIBRARY_PATH',  # Tested
        'darwin': 'DYLD_LIBRARY_PATH',  # Tested
    }

    _platform = platform.system().lower()
    if _platform not in DYNAMIC_LIBRARY_PATH_DICT:
        fastr.log.warning('"Dynamic library path not supported on platform: {}"'.format(_platform))

    def __init__(self, binary, paths=None, environment_variables=None,
                 initscripts=None, modules=None, interpreter=None, **kwargs):
        """
        Define a new local binary target. Must be defined either using paths and optionally environment_variables
        and initscripts, or enviroment modules.
        """
        self.binary = binary
        if modules is None:
            if 'module' in kwargs and kwargs['module'] is not None:
                fastr.log.warning('Using deprecated module in target (modules is new way to do it)')
                self._modules = (kwargs['module'],)
            else:
                self._modules = None
        elif isinstance(modules, str):
            self._modules = (modules.strip(),)
        else:
            self._modules = tuple(x.strip() for x in modules)

        if isinstance(paths, str):
            self._paths = [{'type': 'bin', 'value': paths}]
        elif paths is None and 'location' in kwargs and kwargs['location'] is not None:
            fastr.log.warning('Using deprecated location in target (paths is the new way to do it)')
            self._paths = [{'type': 'bin', 'value': kwargs['location']}]
        else:
            self._paths = paths

        if self._paths is not None:
            for path_entry in self._paths:
                if not url.isurl(path_entry['value']):
                    fastr.log.info('Changing {}'.format(path_entry['value']))
                    path_entry['value'] = os.path.abspath(path_entry['value'])

        if environment_variables is None:
            environment_variables = {}
        self._envvar = environment_variables

        if initscripts is None:
            initscripts = []
        self._init_scripts = [os.path.abspath(x) for x in initscripts]

        self.interpreter = interpreter

        self._roll_back = None

    def __enter__(self):
        """
        Set the environment in such a way that the target will be on the path.
        """
        super(LocalBinaryTarget, self).__enter__()

        # Create dictionary of possible platforms, to set dynamic labrary path
        # Add check to see if _platform is present in dictionary
        if self._platform in self.DYNAMIC_LIBRARY_PATH_DICT:
            dynamic_library_path = self.DYNAMIC_LIBRARY_PATH_DICT[self._platform]
        else:
            dynamic_library_path = None

        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            # Clear the enviroment modules and load all required modules
            ENVIRONMENT_MODULES.clear()
            for module_ in self._modules:
                if not ENVIRONMENT_MODULES.isloaded(module_):
                    ENVIRONMENT_MODULES.load(module_)
                    fastr.log.info('loaded module: {}'.format(module_))
            fastr.log.info('LoadedModules: {}'.format(ENVIRONMENT_MODULES.loaded_modules))
        elif self._paths is not None:
            # Prepend PATH and LD_LIBRARY_PATH as required
            self._roll_back = {'PATH': os.environ.get('PATH', None)}

            # Prepend extra paths to PATH
            bin_path = os.environ.get('PATH', None)
            bin_path = [bin_path] if bin_path else []
            extra_path = [x['value'] for x in self._paths if x['type'] == 'bin']
            extra_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_path]
            fastr.log.info('Adding extra PATH: {}'.format(extra_path))
            os.environ['PATH'] = os.pathsep.join(extra_path + bin_path)

            # Prepend extra paths to LB_LIBRARY_PATH
            extra_ld_library_path = [x['value'] for x in self._paths if x['type'] == 'lib']
            if len(extra_ld_library_path) > 0:
                if dynamic_library_path is None:
                    message = 'Cannot set dynamic library path on platform: {}'.format(self._platform)
                    fastr.log.critical(message)
                    raise exceptions.FastrNotImplementedError(message)

                self._roll_back[dynamic_library_path] = os.environ.get(dynamic_library_path, None)

                lib_path = os.environ.get(dynamic_library_path, None)
                lib_path = [lib_path] if lib_path else []
                extra_ld_library_path = [fastr.vfs.url_to_path(x) if url.isurl(x) else x for x in extra_ld_library_path]

                fastr.log.info('Adding extra LIB: {}'.format(extra_ld_library_path))
                os.environ[dynamic_library_path] = os.pathsep.join(extra_ld_library_path + lib_path)

            # Set other environment variables as indicated
            for var, value in self._envvar.items():
                if var in ['PATH', dynamic_library_path]:
                    continue

                self._roll_back[var] = os.environ.get(var, None)
                os.environ = str(value)

            # Run init script(s) if required
            for script in self._init_scripts:
                if isinstance(script, str):
                    script = [script]

                subprocess.call(script)
        else:
            raise exceptions.FastrNotImplementedError(
                'Binary targets must have either paths or modules set! (binary {})'.format(self.binary)
            )

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Cleanup the environment
        """
        if ENVIRONMENT_MODULES_LOADED and self._modules is not None and len(self._modules) > 0:
            ENVIRONMENT_MODULES.clear()
        elif self._roll_back is not None:
            for var, value in self._roll_back.items():
                if value is not None:
                    os.environ[var] = value
                else:
                    del os.environ[var]

            self._roll_back = None

    def call_subprocess(self, command):
        """
        Call a subprocess with logging/timing/profiling

        :param list command: the command to execute
        :return: execution info
        :rtype: dict
        """
        sysuse = ProcessUsageCollection()
        start_time = time.time()
        fastr.log.info('Calling command arguments: {}'.format(command))
        printable_command = []
        for item in command:
            printable_command.append(shellescape.quote(item))
        fastr.log.info('Calling command: "{}"'.format(' '.join(printable_command)))
        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except OSError as exception:
            if exception.errno == 2:
                raise exceptions.FastrExecutableNotFoundError(command[0])
            elif exception.errno == 13:
                # Permission denied
                raise exceptions.FastrNotExecutableError('Cannot execute {}, permission denied!'.format(command[0]))
            else:
                raise exception
        monitor_thread = threading.Thread(target=self.monitor_process, name='SubprocessMonitor', args=(process, sysuse))
        monitor_thread.daemon = True  # Make sure this Thread does not block exiting the script
        monitor_thread.start()
        stdout, stderr = process.communicate()
        return_code = process.poll()
        end_time = time.time()

        if monitor_thread.is_alive():
            monitor_thread.join(2 * self._MONITOR_INTERVAL)
            if monitor_thread.is_alive():
                fastr.log.warning('Ignoring unresponsive monitor thread!')

        return {'returncode': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'command': command,
                'resource_usage': list(sysuse),
                'time_elapsed': end_time - start_time}

    def monitor_process(self, process, resources):
        """
        Monitor a process and profile the cpu, memory and io use. Register the
        resource use every _MONITOR_INTERVAL seconds.

        :param subproces.Popen process: process to monitor
        :param ProcessUsageCollection resources: list to append measurements to
        """
        psproc = psutil.Process(process.pid)

        # Loop initialization
        psproc.cpu_percent()  # Get rid of meaningless 0.0 at start
        last_timestamp = datetime.datetime.utcnow()

        while process.poll() is None:
            try:
                # The sleep duration is adapted to loop duration so aggregation will not cause
                # extended intervals
                sleep_duration = self._MONITOR_INTERVAL - (datetime.datetime.utcnow() - last_timestamp).total_seconds()
                sleep_duration = 0.0 if sleep_duration < 0.0 else sleep_duration
                time.sleep(sleep_duration)

                # Get process usage information
                memory_info = psproc.memory_info()

                if self._platform == 'darwin':
                    io_read = None
                    io_write = None
                else:
                    io_info = psproc.io_counters()
                    io_read = io_info.read_bytes
                    io_write = io_info.write_bytes

                last_timestamp = datetime.datetime.utcnow()
                usage = resources.usage_type(timestamp=last_timestamp.isoformat(),
                                             cpu_percent=psproc.cpu_percent(),
                                             vmem=memory_info.vms,
                                             rmem=memory_info.rss,
                                             read_bytes=io_read,
                                             write_bytes=io_write)

                resources.append(usage)

            except psutil.Error:
                # If the error occured because during the interval of meassuring the CPU use
                # the process stopped, we do not mind
                if process.poll() is None:
                    raise

    def run_command(self, command):
        if self.interpreter is not None:
            paths = [x['value'] for x in self._paths if x['type'] == 'bin']
            fastr.log.info('Options: {}'.format(paths))
            containing_path = next(x for x in paths if os.path.exists(os.path.join(x, command[0])))
            interpreter = self.interpreter

            command = [interpreter, os.path.join(containing_path, command[0])] + command[1:]

        fastr.log.debug('COMMAND: "{}" ({})'.format(command, type(command).__name__))
        return self.call_subprocess(command)
