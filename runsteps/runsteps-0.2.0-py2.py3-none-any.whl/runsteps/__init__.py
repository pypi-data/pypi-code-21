"""runsteps module - manage execution of ordered steps"""
import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
import time

HELPER_FUNC = """
runsteps_save_keypair () {
    [ -n "$1" ] || return 1
    [ -n "$RUNSTEPS_DATA" ] || return 2
    [ -d "$RUNSTEPS_DATA" ] || return 3
    key=$1
    shift
    val=$@
    tmpfile="${RUNSTEPS_DATA}/env/$(date +%s).json"
    printf '{"%s": "%s"}\n' "$key" "$val" >"$tmpfile"
}
"""

PYENVCMD = """{} -c 'import json, os, sys;
sys.stdout.write(json.dumps(dict(os.environ)))'"""


def _find_top_level_files(directory):
    """Find files in the top level of a directory

    Args:
        directory: String of a path to a directory
    Returns:
        A list of paths to files existing in the given directory
    """
    (path, dirs, files) = next(os.walk(directory))
    return [os.path.abspath('/'.join([path, item])) for item in files]


def _assert_is_list(obj):
    """Assert that the given object is a list"""
    try:
        assert isinstance(obj, list)
    except AssertionError:
        obj_type = type(obj)
        raise RunnerException(
            'Expected a list of steps. Got a {}.'.format(obj_type))


def _format_time(epoch_time, format_string="%Y-%m-%d %H:%M:%S"):
    """Return a formatted representation of an epoch timestmap"""
    return time.strftime(format_string, time.localtime(epoch_time))


class RunnerException(Exception):
    """A simple exception that doesn't output a stack trace"""
    def __init__(self, message, return_code=1):
        super(RunnerException, self).__init__(message)
        logging.error('%s', message)
        sys.exit(return_code)


class Runner(object):
    """ The main class for managing and executing ordered steps."""
    def __init__(self):
        """Initialization of a Runner instance"""
        self.history = []
        self.datadir = '/'.join([os.getenv('HOME', '.'), '.runsteps'])
        self.envdir = '/'.join([self.datadir, 'env'])
        self.logdir = '/'.join([self.datadir, 'logs'])
        self.history_file = '/'.join([self.datadir, 'history'])
        self._steps = []
        self._env = {
            'RUNSTEPS_DATA': self.datadir,
            'RUNSTEPS_ENV': self.envdir,
            'RUNSTEPS_LOGS': self.logdir
        }
        for directory in [self.datadir, self.envdir, self.logdir]:
            if not os.path.exists(directory):
                os.mkdir(directory)
        with open('{}/runsteps_helpers.sh'.format(self.envdir),
                  'w') as helper:
            helper.write(HELPER_FUNC)

    def _add_to_history(self, step, start, stop, code):
        duration = stop - start
        self.history.append({
            "step": step,
            "start_time": _format_time(start),
            "end_time": _format_time(stop),
            "duration": str(datetime.timedelta(seconds=duration)),
            "return_code": code})
        with open(self.history_file, 'w') as history:
            json.dump(self.history, history)

    def _update_env_from_files(self):
        for jsonfile in _find_top_level_files(self.envdir):
            if jsonfile.split('.')[-1] == 'json':
                with open(jsonfile, 'r') as jsonfilefd:
                    self._env.update(json.load(jsonfilefd))

    def _execute_step(self, step, logfd, outfd):
        process = subprocess.Popen(
            step.split(' '), env=self._env,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = process.stdout.readline().decode('utf_8')
            if line:
                if logfd:
                    logfd.write(line)
                if outfd:
                    outfd.write(line)
                    outfd.flush()
            else:
                returncode = process.wait()
                if returncode != 0:
                    raise RunnerException(
                        'Step {} failed with status: {}'.format(
                            step, returncode),
                        returncode)
                else:
                    break
        return returncode

    def print_history(self, out=sys.stdout):
        """Output the history data in json format"""
        try:
            with open(self.history_file, 'r') as history:
                items = json.load(history)
        except IOError:
            raise RunnerException('Cannot open history file')
        out.write(json.dumps(items, indent=4) + '\n')
        out.flush()

    def dryrun(self, out=sys.stdout):
        """Don't execute anything, just list the steps as they have been
           collected
        """
        _assert_is_list(self._steps)
        if out:
            out.write(json.dumps(self._steps, indent=4) + '\n')
            out.flush()
            sys.exit(0)

    def run(self, inherit_env=False, logs=True, out=sys.stdout):
        """Execute each item in the list of steps

        Args:
            inherit_env:
                An optional boolean. If True, adds the user's current and
                default environment variables to the step environment.
            logs:
                An optional boolean. If True, a log file will be written with
                output from stdout and stderr for each step.  If False, no logs
                are created.
            out:
                An output fd, or None, if quiet is requested.
        """
        _assert_is_list(self._steps)

        if inherit_env:
            self._env.update(os.environ)

        for step in self._steps:
            logfd = None

            # Update the environment again, based on what the user with a
            # login shell would see. Do this now because os.environ is set
            # at the time the os module is imported, and the user's default
            # login environment may have changed
            if inherit_env:
                shell = os.getenv('SHELL', '/bin/sh')
                envs = subprocess.check_output(
                    [shell, '-l', '-c', PYENVCMD.format(sys.executable)])
                self._env.update(json.loads(envs))

            logging.debug('Running step: %s', step)
            start = time.time()
            start_ts = _format_time(start, format_string="%Y%m%d%H%M%S")
            if logs:
                base = '{}-{}.log'.format(os.path.basename(step), start_ts)
                logfile = '/'.join([self.logdir, base])
                logfd = open(logfile, 'w')
            try:
                returncode = self._execute_step(step, logfd, out)
            except Exception:
                returncode = 1
                raise RunnerException(
                    'Missing or bad executable: {}'.format(step))
            finally:
                stop = time.time()
                if logfd:
                    logfd.close()
                self._update_env_from_files()
                self._add_to_history(step, start, stop, returncode)

    def load(self, steps):
        """Accept a list of steps (commands) to run"""
        _assert_is_list(steps)
        self._steps = steps

    def load_from_path(self, path):
        """Accept a path and forward request to either
           load_from_dir or load_from_file
        """
        if not os.path.exists(path):
            raise RunnerException('No such file or directory; {}'.format(path))
        if os.path.isdir(path):
            self.load_from_dir(path)
        else:
            self.load_from_file(path)

    def load_from_dir(self, directory):
        """Find executable files inside a given directory, sort them
           alphabetically and load them into self._steps

        Args:
            directory: string containing a path to a directory.
        """
        try:
            assert os.path.isdir(directory)
        except AssertionError:
            raise IOError('No such directory "{}"'.format(directory))
        logging.debug('Loading steps from directory: %s', directory)
        executables_found = []
        for newfile in _find_top_level_files(directory):
            if os.access(newfile, os.X_OK):
                executables_found.append(newfile)
        self.load(sorted(executables_found))

    def load_from_file(self, jsonfile):
        """Open jsonfile, parse its contents, and if it contains a single
           list, load that list into self._steps

        Args:
            jsonfile: A string containing a path to a json-formatted file.
        """
        logging.debug('Loading steps from file: %s', jsonfile)
        with open(jsonfile, 'r') as jsonfiled:
            steps = json.load(jsonfiled)
        self.load(steps)


def main(args=sys.argv[1:]):
    """Entry point for the console script"""
    mainparser = argparse.ArgumentParser(
        description='run a series of sequential steps')
    exclusive = mainparser.add_mutually_exclusive_group()
    exclusive.add_argument(
        '-d', '--dry-run',
        dest='dryrun',
        action='store_true',
        help='print what steps would have been run')
    mainparser.add_argument(
        '-i', '--inherit-env',
        dest='ienv',
        action='store_true',
        help='each step inherits current environment variables')
    mainparser.add_argument(
        '-n', '--no-logs',
        dest='logs',
        action='store_false',
        help='disable the creation of log files for each step')
    exclusive.add_argument(
        '-q', '--quiet',
        action='store_false',
        dest='out',
        default=sys.stdout,
        help='do not write step output to stdout')
    exclusive.add_argument(
        '-v', '--verbose',
        action='store_true')
    mainparser.add_argument(
        'path',
        help='a directory containing executable files to run in alphabetical '
             'order, or a file containing a json list of commands to execute '
             'sequentially')
    parser = mainparser.parse_args(args)

    if parser.verbose:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.INFO
    logging.basicConfig(
        level=loglevel,
        format='%(asctime)s %(levelname)-6s %(message)s')

    runner = Runner()
    runner.load_from_path(parser.path)
    if parser.dryrun:
        runner.dryrun()
    else:
        runner.run(inherit_env=parser.ienv, logs=parser.logs, out=parser.out)
