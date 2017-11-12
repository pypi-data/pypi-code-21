
__all__ = ['init', 'is_initialized']

import os, sys, configparser, re, inspect
from os.path import exists, isdir, abspath, join, dirname, isabs
import logging, logging.handlers


_STDOUT = sys.stdout
_GREEN = '\033[1m\033[32m'
_RESET = '\033[1m\033[0m'

_filename = None
# The fully qualified config file that was found by init.


def init(filename='.config', searchfrom=None, env=None, relpath=None):
    """
    filename
      The name of the configuration file.

      This can be a simple filename, in which case the file will be searched for.  It can also
      be a fully qualified filename such as '/etc/project.conf'.

      If not provided, a file named ".config" will be searched for.

    searchfrom
      Optional directory to start searching from.  If not provided, the default is the current
      working directory.  To search from the directory where the calling code is located, use::

        autoconfig.init(searchfrom=__file__)

      This parameter is ignored if `filename` is a path since no search is performed.

    env
      Additional section names to treat as environment variables.  This can be a string for a
      single section or a list of names.

    relpath
      One or more directories (as a single string or a sequence of strings), relative to the
      caller (not the config file or current directory) to append to the system path.

      This is useful for scripts that have a private library directory, particularly in a
      mono-repo design with many small utilities.  If a library is specifically for a
      particular utility, it may be confusing to put it into a global area.

        autoconfig.init(relpath='lib')

    Raises FileNotFoundError if the configuration file is not found.
    """
    global _filename

    _filename = _locate_config(filename, searchfrom)

    p = Parser()
    p.read(_filename)

    _copy_env(_filename, p, env)
    _add_relpath(_filename, relpath)
    _setup_logging(p)


def is_initialized():
    """
    Return True if init has already been called; False otherwise.
    """
    return bool(_filename)


def get_filename():
    """
    Returns the fully qualified name of the config file found by init.
    """
    return _filename


class Parser(configparser.ConfigParser):
    # I want to use Python's ConfigParser to read the file, but it lowercases keys by default.
    # This is not acceptable for the [env] section.  I would like other sections to lowercase,
    # however, and there doesn't seem to be a good way to do that.  I tried providing a Boolean
    # and toggling it but that doesn't work.  For now I'm going to keep the case and lowercase
    # the keys myself.
    def __init__(self):
        configparser.ConfigParser.__init__(self, allow_no_value=True, comment_prefixes='#',
                                           interpolation=configparser.ExtendedInterpolation())

    def optionxform(self, option):
        return option


class _StdoutWrapper(object):
    """
    We replace sys.stdout with an instance of this to add color to print
    statements.  You should only use print statements when developing /
    debugging.  Do not leave them in!
    """
    def __init__(self):
        self._stdout = sys.stdout

    def write(self, *args):
        # Note: Print statements in Python 3 seem to print the text and then a
        # new line.  Don't bother to color the newline.
        self._stdout.write(_GREEN)
        self._stdout.write(' '.join(args))
        self._stdout.write(_RESET)

    def flush(self):
        self._stdout.flush()

    def __getattr__(self, name):
        return getattr(self._stdout, name)


def _setup_logging(p):
    if 'logging' not in p.sections():
        return

    d = {key.lower(): p.get('logging', key) for key in p.options('logging')}
    # (See the note in Parser about case.)

    # Setup file and console handlers if requested.  If colorlog exists, the console output
    # will be in color.

    handlers = []
    filename = d.get('filename')
    if filename:
        format = d.get('format', "%(levelname).1s %(name)s %(message)s")
        h = logging.handlers.TimedRotatingFileHandler(filename, when='midnight', backupCount=6)
        h.setLevel(logging.DEBUG)
        h.setFormatter(logging.Formatter(format))
        handlers.append(h)

    console = d.get('console', 'false')
    if console == 'systemd':
        # Format for writing to the systemd journal.  Prefix with <1>, etc. for log levels, do
        # not put a timestamp (since the journal already has it), and remove newlines from
        # stack traces so they show up as a single line.
        formatter = SystemdFormatter()
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(formatter)
        h.setLevel(logging.DEBUG)
        handlers.append(h)

    elif console.lower() in ('true', 'short', 'long', 'systemd'):
        format = '%(asctime)s %(levelname).1s %(name)s %(message)s'
        if console == 'long':
            format = '%(asctime)s ' + format

        try:
            from colorlog import ColoredFormatter
            formatter = ColoredFormatter(
                '%(log_color)s' + format,
                reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'white',
                    'WARNING': 'yellow',
                    'ERROR': 'bg_red,white',
                    'CRITICAL': 'bg_red,white',
                },
                secondary_log_colors={},
                style='%')
        except:
            formatter = logging.Formatter(format)

        h = logging.StreamHandler(sys.stdout)
        h.setLevel(logging.DEBUG)
        h.setFormatter(formatter)
        handlers.append(h)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    if handlers:
        root.handlers = handlers

    re_sep = re.compile(r'[\s,]+')
    names = set()
    names.update(name for name in re_sep.split(os.environ.get('DEBUG', '')) if name)
    names.update(name for name in re_sep.split(d.get('debug', '')) if name)

    for name in names:
        l = logging.getLogger(name)
        l.setLevel(logging.DEBUG)

    # Redirect stdout so we can color print statements too.
    sys.stdout = _StdoutWrapper()


def _copy_env(fqn, p, env):
    """
    Copies the items from the [env] section, and any additional sections listed in 'env'
    to os.environ.

    If PYTHONPATH is provided, it is parsed and prefixed to the system path.

    fqn
      The fully qualified path of the configuration file.

    p
      The ConfigParser

    env
      Optional list of environment sections to add to the environment.
    """
    envs = ['env']
    if env:
        assert isinstance(env, (str, list))
        if isinstance(env, str):
            envs.append(env)
        else:
            envs.extend(env)

    paths = []

    root = dirname(fqn)

    for name in envs:
        if name in p.sections():
            for key, value in p[name].items():
                if value is None or value == '':
                    # A key with no value is used to "unset".
                    if key in os.environ:
                        del os.environ[key]
                else:
                    if key == 'PYTHONPATH':
                        a = _make_absolute(root, value)
                        if a:
                            value = os.pathsep.join(a)
                            paths.extend(a)

                    # Do we need to check the encoding?
                    os.environ[key] = value

    # If we found any PYTHONPATH entries, add them to the system path.  Make sure you keep the
    # original order.  If they are not fully qualified, they are relative to the configuration
    # file

    if paths:
        sys.path[:0] = paths


def _make_absolute(root, paths):
    """
    Given a string of one or more paths, split them into an array and make relative paths
    absolute.

    * root: The fully-qualified directory applied to relative directories in `paths`.
    * paths: A path string using the operating systems path separator ("/usr:/sys" or
      "c:\test;c:\bogus").
    """
    paths = [p.strip() for p in paths.strip().split(os.pathsep) if p.strip()]
    if not paths:
        return None
    return [(p if isabs(p) else join(root, p)) for p in paths]


def _locate_config(filename, searchfrom):
    """
    Locates the configuration file.

    We're going to allow filename to be a path to a different file so we can accept __file__.
    """
    if os.sep in filename and searchfrom:
        raise ValueError('Cannot provide a path in `filename` and a `searchfrom` value.')

    if isabs(filename):
        if not exists(filename):
            raise FileNotFoundError('Did not find configuration file.  filename=%r' % filename)
        return filename

    searchfrom = abspath(searchfrom or os.getcwd())
    path = searchfrom

    while 1:
        if isdir(path):
            fqn = join(path, filename)
            if exists(fqn) and not isdir(fqn):
                return fqn

        parent = dirname(path)
        if parent == path:
            raise FileNotFoundError('Did not find configuration file.  filename=%r searchfrom=%s' % (filename, searchfrom))
        path = parent


def _add_relpath(fqn, relpath):
    """
    If relpath was provided, add each entry in it to the Python path.
    """
    paths = _path_to_list(relpath)
    if not paths:
        return

    # Entries are relative to the *caller* of init.  We'll inspect the stack and backup.  (This
    # is what makes Python awesome.  Yes it is hard to optimize because of this, but when you
    # need it is great.)
    #
    # Frames:
    # * 0 - this function
    # * 1 - the init function that called this function
    # * 2 - the caller of init  <--  Hello, Sailor!

    frames = inspect.stack()
    if not frames:
        raise RuntimeError('Stack traces are not supported by this Python environment')
    root = dirname(frames[2][1])

    for path in paths:
        if not isabs(path):
            path = join(root, path)
        sys.path.append(path)


def _path_to_list(path):
    """
    Accepts a string or list of strings, each being a set of paths separated by the
    OS path separator (os.pathsep, e.g. ':' on Liux, ';' on Windows).
    """
    if path is None:
        return None

    if isinstance(path, str):
        paths = [path]

    result = []
    for p in paths:
        result.extend(part.strip() for part in p.split(os.pathsep))
    result = [part for part in result if part]
    return result


PREFIX = {
    logging.CRITICAL: '<2>',
    logging.ERROR: '<3>',
    logging.WARNING: '<4>',
    logging.INFO: '<6>',
    logging.DEBUG: '<7>',
    logging.NOTSET: '<7>'
}


class SystemdFormatter(logging.Formatter):
    """
    A logging formatter for writing to stdout for systemd.
    """
    def format(self, record):
        s = logging.Formatter.format(self, record)
        s = PREFIX[record.levelno] + s.replace('\n', '\\n')
        return s
