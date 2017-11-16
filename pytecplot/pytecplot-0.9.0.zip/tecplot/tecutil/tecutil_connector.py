from __future__ import print_function

import os
import calendar
import ctypes
import logging
import platform
import re
import socket
import sys
import time

from ctypes import (c_char, c_char_p, c_int, c_size_t, c_void_p, POINTER,
                    pointer, c_bool, cast, byref)
from ctypes.util import find_library
from collections import Counter, namedtuple
from datetime import date
from enum import Enum
from locale import setlocale, LC_NUMERIC
from os import path
from six import string_types
from subprocess import Popen, PIPE
from textwrap import dedent
from warnings import warn

from .captured_output import captured_output
from ..constant import *
from ..exception import *
from .tecutil import TecUtil

try:
    from .tecutil_client import TecUtilClient
except ImportError:
    TecUtilClient = None


log = logging.getLogger(__name__)


class ManagerStartReturnCode(Enum):
    Ok                              = 0
    HomeDirectoryNotSpecified       = 1
    LicenseFileNotFound             = 2
    LicenseIsInvalid                = 3
    LicenseExpired                  = 4
    InternalInitializationError     = 5
    EngineUninitialized             = 6
    LicenseFileContainsPermanent    = 7


def find_file(filenames, searchpaths):
    if isinstance(searchpaths, string_types):
        searchpaths = searchpaths.split(os.pathsep)
    for filename in filenames:
        for searchpath in searchpaths:
            fpath = path.join(searchpath, filename)
            if path.exists(fpath):
                return fpath


SDKVersion = namedtuple('SDKVersion', ['MajorVersion', 'MinorVersion',
                                       'MajorRevision', 'MinorRevision'])


class TecUtilConnector(object):

    Message = namedtuple('Message', ['level', 'message'])

    def __init__(self):
        # ensure log messages get out to console
        logging.basicConfig()

        self.handle = None
        self.tecutil_handle = None
        self.libbatch_path = None
        self.started = None
        self.stopped = None
        self._last_message = None
        self._load_library_error = None

        self.client = None
        if TecUtilClient is not None:
            self.client = TecUtilClient()

        if __debug__:
            self._tecutil_call_count = Counter()
            self._style_call_count = {'GET': Counter(), 'SET': Counter()}

        if ctypes.sizeof(c_void_p) != 8:
            msg = '64-bit Python is required to use PyTecplot'
            raise TecplotLibraryNotLoadedError(msg)

        # In Windows, libraries which use Qt or are dependant on Qt
        # must be imported after importing tecplot.

        # We can detect this by checking to see if 'PyQt4' has been imported,
        # however this can also be a false positive if the client is not
        # running a pyqt script.

        # Therefore, just print an information message if we find PyQt in
        # the path. davido 12/7/16

        if any(lib in sys.modules for lib in ('PyQt4', 'PySide')):
            log.info('''If your script uses PyQt, you must import tecplot
                        before importing PyQt.''')

        load = {'Darwin': self.load_darwin,
                'Linux': self.load_linux,
                'Windows': self.load_windows}

        log.debug('Attempting to load Tecplot batch library')
        try:
            load[platform.system()]()
            self.init_local_library()
            msg = 'Successfully loaded Tecplot batch library: {}'
            log.info(msg.format(self.libbatch_path))
        except KeyError as e:
            self._load_library_error = TecplotLibraryNotFoundError, str(e)
        except AttributeError as e:
            self._load_library_error = TecplotOutOfDateEngineError, (2017, 1, 0)
        except Exception as e:
            self._load_library_error = type(e), str(e)

    @property
    def connected(self):
        return self.client is not None and self.client.connected

    def connect(self, host='localhost', port=7600, timeout=10, quiet=False):
        if self.client is None:
            raise ImportError(dedent('''\
                Could not load the TecUtilClient class.
                Please install the required Python modules
                pyzmq and flatbuffers.'''))
        self.client.connect(host, port, timeout, quiet=quiet)
        if self.connected:
            self.update_sdk_version()

    def disconnect(self):
        self.client.disconnect()
        self.update_sdk_version()
        log.info('Disconnected from Tecplot 360 instance.')

    @property
    def tecsdkhome(self):
        if not hasattr(self, '_tecsdkhome'):
            if self.connected:
                self._tecsdkhome = _tecutil.TecplotGetHomeDirectory()
            else:
                try:
                    self._tecsdkhome = os.environ['TECSDKHOME']
                    if not path.isdir(self._tecsdkhome):
                        raise OSError
                except (KeyError, OSError):
                    if self.libbatch_path is not None:
                        log.debug('reading tecutilbatch path to get SDK home')
                        tecutilbatch_dir = path.dirname(self.libbatch_path)
                        self._tecsdkhome = path.dirname(tecutilbatch_dir)
                    else:
                        self._tecsdkhome = ''
        return self._tecsdkhome

    def init_local_library(self):
        setlocale(LC_NUMERIC, 'C')
        os.environ['LC_NUMERIC'] = 'C'
        self.handle.AcquireLicense.restype = c_bool
        self.handle.GetTUAssertErrorMessage.restype = c_char_p
        self.handle.LicenseExpirationDate.restype = c_char_p
        self.handle.LicenseInfo.restype = c_char_p
        self.handle.LicenseIsRoaming.restype = c_bool
        self.handle.LicenseIsValid.restype = c_bool
        self.handle.LicenseStartRoaming.argtypes = (c_int,)
        self.handle.LicenseStartRoaming.restype = c_bool
        self.handle.LicenseStopRoaming.argtypes = (c_bool,)
        self.handle.LicenseStopRoaming.restype = c_bool
        self.handle.ReleaseLicense.restype = c_bool
        self.handle.Start.argtypes = (c_char_p,)

    def load_linux(self):

        def _syslibpath():
            ret = []
            try:
                log.debug('acquiring system library search path using ldconfig')
                cmd = 'ldconfig -v -N'
                proc = Popen(cmd, shell=True,
                             executable=os.environ.get('SHELL', '/bin/bash'),
                             env=os.environ, stdout=PIPE, stderr=PIPE)
                ptrn = re.compile(r'^\t')
                for line in proc.communicate()[0][:-1].decode().split('\n'):
                    if not ptrn.match(line):
                        d = line.split(':')[0]
                        if path.exists(d) and path.isdir(d):
                            ret.append(d)
            except:
                log.debug('diagnostic command failed: ' + cmd)
            return ret

        def _missinglibs(lib):
            ret = []
            try:
                log.debug('looking for missing libs using ldd')
                cmd = 'ldd ' + lib
                proc = Popen(cmd, shell=True,
                             executable=os.environ.get('SHELL', '/bin/bash'),
                             env=os.environ, stdout=PIPE, stderr=PIPE)
                out, err = proc.communicate()
                if 'command not found' not in err.decode():
                    if len(out.decode().split('\n')) < 3:
                        log.debug(out.decode())
                    for line in out.decode().split('\n'):
                        if line.endswith('not found'):
                            ret.append(line.split()[0])
            except:
                log.debug('diagnostic command failed: ' + cmd)
            return ret

        def _find_library(libnames):
            libpath = os.environ.get('LD_LIBRARY_PATH', None)
            for libname in libnames:
                ret = None
                if libpath is not None:
                    ret = find_file([libname], libpath)
                if ret is None:
                    ret = find_file([libname], _syslibpath())
                if ret is not None:
                    return ret

        def _dl_abspath(libname):
            """Returns the absolute path of the loaded dynamic library"""
            log.debug('using libc to get path to tecutilbatch library')

            class dl_phdr_info(ctypes.Structure):
                _fields_ = [
                    ('padding0', c_void_p),  # ignore it
                    ('dlpi_name', c_char_p)]
            callback_t = ctypes.CFUNCTYPE(c_int, POINTER(dl_phdr_info),
                                          POINTER(c_size_t), c_char_p)
            _dl_abspath.lib_abspath = None

            def callback(info, size, data):
                if data in info.contents.dlpi_name:
                    _dl_abspath.lib_abspath = \
                        info.contents.dlpi_name.decode()
                return 0

            libc = ctypes.CDLL(None)
            libc.dl_iterate_phdr.argtypes = [callback_t, c_char_p]
            libc.dl_iterate_phdr.restype = c_int
            libc.dl_iterate_phdr(callback_t(callback), libname.encode())
            return _dl_abspath.lib_abspath

        libfmt = 'lib{name}.so'
        libbatch = libfmt.format(name='tecutilbatch')
        libchecked = libfmt.format(name='tecutilchecked')
        libnames = [libbatch, libchecked]

        cdllexcept = {}
        try:
            self.handle = ctypes.cdll.LoadLibrary(libbatch)
            self.tecutil_handle = ctypes.cdll.LoadLibrary(libchecked)
            if self.handle is None or self.tecutil_handle is None:
                raise OSError
            else:
                self.libbatch_path = _dl_abspath(libbatch)
                return
        except (OSError, TypeError) as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            info = [str(x) for x in [e, exc_type,
                    '{}:{}'.format(fname, exc_tb.tb_lineno)]]
            cdllexcept[libbatch] = '\n'.join(info)

        if self.handle is None:
            # fall-back to tecinterprocess
            try:
                libinterproc = libfmt.format(name='tecinterprocess')
                self.handle = ctypes.cdll.LoadLibrary(libinterproc)
                self.tecutil_handle = self.handle
                if self.handle is None:
                    raise OSError
                else:
                    self.libbatch_path = _dl_abspath(libinterproc)
                    return
            except (OSError, TypeError) as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                info = [str(x) for x in [e, exc_type,
                        '{}:{}'.format(fname, exc_tb.tb_lineno)]]
                cdllexcept[libinterproc] = '\n'.join(info)

        msg = dedent('''\
            The Tecplot batch library or one of its dependencies could not be
            found. This is usually the result of not setting the environment
            path LD_LIBRARY_PATH to the directory containing the tecplot
            executables.

            LD_LIBRARY_PATH={libpath}

            Library file name(s):
                {libnames}
        ''').format(libpath=os.environ.get('LD_LIBRARY_PATH', None),
                    libnames='\n    '.join(libnames))

        self.libbatch_path = _find_library([libbatch])
        if self.libbatch_path is None:
            raise TecplotLibraryNotFoundError(msg)

        msg += dedent('''
        Found batch library file:
            {foundlib}

        Your Tecplot 360 EX may be out of date. Please install the latest
        version of 360 EX which can be obtained here:
            http://www.tecplot.com/downloads
        ''').format(foundlib=self.libbatch_path)

        missinglibs = _missinglibs(self.libbatch_path)
        if len(missinglibs):
            msg += dedent('''
                Missing libraries:
                    {missinglibs}
            ''').format(missinglibs='\n    '.join(missinglibs))

        lib = path.basename(self.libbatch_path)
        msg += dedent('''
            Python ctypes exception caught while trying to load library:
                {cdllexcept}
        ''').format(cdllexcept='\n    '.join(cdllexcept[lib].split('\n')))

        raise TecplotLibraryNotLoadedError(msg)

    def load_darwin(self):

        def _missinglibs(lib):
            ret = []
            try:
                log.debug('looking for missing libs using otool')
                cmd = 'otool -L ' + lib
                proc = Popen(cmd, shell=True,
                             executable=os.environ.get('SHELL', '/bin/bash'),
                             env=os.environ, stdout=PIPE, stderr=PIPE)
                out, err = proc.communicate()
                if 'command not found' not in err.decode():
                    for line in out.decode().split('\n'):
                        if line.endswith('not found'):
                            ret.append(line.split()[0])
            except:
                log.debug('diagnostic command failed: ' + cmd)
            return ret

        def _find_library(libnames):
            for libname in libnames:
                ret = find_library(libname)
                if ret is not None:
                    return ret

        libfmt = 'lib{name}.so'
        libbatch = libfmt.format(name='tecutilbatch')
        libchecked = libfmt.format(name='tecutilchecked')
        libnames = [libbatch, libchecked]

        cdllexcept = {}
        self.libbatch_path = _find_library([libbatch])
        try:
            self.handle = ctypes.cdll.LoadLibrary(libbatch)
            self.tecutil_handle = ctypes.cdll.LoadLibrary(libchecked)
            if self.handle is None or self.tecutil_handle is None:
                raise OSError
            else:
                return
        except (OSError, TypeError) as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            info = [str(x) for x in [e, exc_type, fname, exc_tb.tb_lineno]]
            cdllexcept[libbatch] = '\n'.join(info)

        if self.handle is None:
            # fall-back to tecinterprocess
            try:
                libinterproc = libfmt.format(name='tecinterprocess')
                self.libbatch_path = _find_library([libinterproc])
                self.handle = ctypes.cdll.LoadLibrary(libinterproc)
                self.tecutil_handle = self.handle
                if self.handle is None:
                    raise OSError
                else:
                    return
            except (OSError, TypeError) as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                info = [str(x) for x in [e, exc_type,
                        '{}:{}'.format(fname, exc_tb.tb_lineno)]]
                cdllexcept[libinterproc] = '\n'.join(info)

        msg = dedent('''\
            The Tecplot batch library or one of its dependencies could not be
            found. This is usually the result of not setting the environment
            path DYLD_LIBRARY_PATH to the directory containing the tecplot
            executables.

            DYLD_LIBRARY_PATH={libpath}

            Batch library file name(s):
                {libnames}
        ''').format(libpath=os.environ.get('DYLD_LIBRARY_PATH', None),
                    libnames='\n    '.join(libnames))

        if self.libbatch_path is None:
            raise TecplotLibraryNotFoundError(msg)

        msg += dedent('''
        Found batch library file:
            {foundlib}

        Your Tecplot 360 EX may be out of date. Please install the latest
        version of 360 EX which can be obtained here:
            http://www.tecplot.com/downloads
        ''').format(foundlib=self.libbatch_path)

        missinglibs = _missinglibs(self.libbatch_path)
        if len(missinglibs):
            msg += dedent('''
                Missing libraries:
                    {missinglibs}
            ''').format(missinglibs='\n    '.join(missinglibs))

        lib = path.basename(self.libbatch_path)
        msg += dedent('''
            Python ctypes exception caught while trying to load library:
                {cdllexcept}
        ''').format(cdllexcept='\n    '.join(cdllexcept[lib].split('\n')))

        raise TecplotLibraryNotLoadedError(msg)

    def load_windows(self):
        # We need to search for (debug) tecutilbatchd.dll first,
        # otherwise we might find a (release) tecutilbatch.dll
        # before finding tecutilbatchd.dll

        cdllexcept = {}
        for libfmt in ['{name}d.dll', '{name}.dll']:
            libbatch = libfmt.format(name='tecutilbatch')
            libchecked = libfmt.format(name='tecutilchecked')
            libnames = [libbatch, libchecked]

            self.libbatch_path = find_file(libnames, os.environ['PATH'])
            if self.libbatch_path is not None:
                try:
                    # Temporarily place 360EX first in the path so that we can
                    # be sure the right Qt dlls are loaded.
                    save_path = os.environ['PATH']
                    try:
                        # Prepend the parent of the tecutilbatch lib to the
                        # PATH variable so it will be found first when SDK is
                        # loaded.
                        libdir = os.path.dirname(self.libbatch_path)
                        os.environ['PATH'] = libdir + ';' + os.environ['PATH']
                        self.handle = ctypes.cdll.LoadLibrary(libbatch)
                        self.tecutil_handle = ctypes.cdll.LoadLibrary(
                            libchecked)
                    finally:
                        # Restore the original path as soon
                        # as tecplot is loaded.
                        os.environ['PATH'] = save_path
                    if self.handle is None or self.tecutil_handle is None:
                        raise OSError
                    else:
                        return
                except OSError as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    info = [str(x) for x in [e, exc_type, fname,
                                             exc_tb.tb_lineno]]
                    cdllexcept[libbatch] = '\n'.join(info)

        if self.handle is None:
            # fall-back to tecinterprocess
            for libfmt in ['{name}d.dll', '{name}.dll']:
                libinterproc = libfmt.format(name='tecinterprocess')

                self.libbatch_path = find_file([libinterproc],
                                               os.environ['PATH'])
                if self.libbatch_path is not None:
                    try:
                        # Temporarily place 360EX first in the path so that we
                        # can be sure the right Qt dlls are loaded.
                        save_path = os.environ['PATH']
                        try:
                            # Prepend the parent of the tecutilbatch lib to the
                            # PATH variable so it will be found first when SDK
                            # is loaded.
                            libdir = os.path.dirname(self.libbatch_path)
                            os.environ['PATH'] = '{};{}'.format(
                                libdir, os.environ['PATH'])
                            self.handle = ctypes.cdll.LoadLibrary(libinterproc)
                            self.tecutil_handle = self.handle
                        finally:
                            # Restore the original path as soon
                            # as tecplot is loaded.
                            os.environ['PATH'] = save_path
                        if self.handle is None:
                            raise OSError
                        else:
                            return
                    except OSError as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        co_fname = exc_tb.tb_frame.f_code.co_filename
                        fname = path.split(co_fname)[1]
                        info = [str(x) for x in [e, exc_type, fname,
                                                 exc_tb.tb_lineno]]
                        cdllexcept[libinterproc] = '\n'.join(info)

        msg = dedent('''\
            The Tecplot batch library or one of its dependencies could not be
            found. This is usually the result of not setting the environment
            path PATH to the directory containing the tecplot executables.
            Alternatively, your Tecplot 360 EX may be out of date. Please
            install the latest version of 360 EX which can be obtained here:
                http://www.tecplot.com/downloads

            PATH={libpath}

            Batch library file names:
                {libnames}

            Found batch library file:
                {foundlib}
        ''').format(libpath=os.environ.get('PATH', None),
                    libnames='\n    '.join(libnames),
                    foundlib=self.libbatch_path)

        if self.libbatch_path is None:
            raise TecplotLibraryNotFoundError(msg)
        else:
            info = '\n    '.join(cdllexcept[libbatch].split('\n'))
            # Error 127 == Missing dll symbol.
            if 'Error 127' in info:
                info += ('\n***NOTE: If your script uses PyQt, ' +
                         'you must import tecplot before importing PyQt.\n')
            msg += dedent('''
                Python ctypes exception caught while trying to load library:
                    {cdllexcept}
            ''').format(cdllexcept=info)

        raise TecplotLibraryNotLoadedError(msg)

    def start(self):
        if self.started:
            return

        if self.handle is None or self.libbatch_path is None:
            if self._load_library_error is not None:
                Err, msg = self._load_library_error
                raise Err(msg)
            else:
                raise TecplotLibraryNotLoadedError

        if self.stopped:
            msg = 'PyTecplot cannot be restarted after it has been stopped.'
            raise TecplotLibraryNotLoadedError(msg)

        log.debug('Attempting to start Tecplot engine')
        msg = 'tecutilbatch path: {0} [{1}]'
        log.debug(msg.format(self.libbatch_path,
                  time.ctime(os.stat(self.libbatch_path).st_mtime)))

        log.debug('SDK home: "{}"'.format(self.tecsdkhome))

        with captured_output(log.debug):
            result = None
            try:
                result = ManagerStartReturnCode(
                    self.handle.Start(self.tecsdkhome.encode()))
            except Exception:
                raise TecplotInitializationError(
                    'Error initializing Tecplot engine. Your Tecplot 360 '
                    'installation may be out of date.')

        errmsg = {
            ManagerStartReturnCode.HomeDirectoryNotSpecified:
                'Missing home directory',
            ManagerStartReturnCode.LicenseFileNotFound: 'Missing license',
            ManagerStartReturnCode.LicenseIsInvalid: dedent('''\
            Your license could not be validated.
            For network licenses, check if all user tokens are in use.
            For single user licenses, your license file may be invalid.
            Contact support@tecplot.com for further assistance.'''),
            ManagerStartReturnCode.LicenseExpired: dedent('''\
            Your license has expired. Please contact sales@tecplot.com
            for further assistance.'''),
            ManagerStartReturnCode.InternalInitializationError: dedent('''
            Internal initialization error. The most common cause of
            an internal initialization error is that the "batch.log" file could
            not be created because the current Tecplot 360 working directory
            is not writable. Check disk space or permissions.'''),
            ManagerStartReturnCode.EngineUninitialized:
                'Engine initialization failed',
            ManagerStartReturnCode.LicenseFileContainsPermanent: dedent('''\
            A license file was found, but it is a permanent license. At this
            time only time limited licenses are supported.''')}

        # Many error codes are license related, but not all of the them.
        # We don't want to imply that there was a license error if the problem
        # is not license related. For example, if batch.log is not writable,
        # the return code will be "InternalInitializationError".
        # In that case it would be misleading to throw a license error.

        # Therefore, we are careful to throw a license error only
        # if the error code is license related, and
        # otherwise throw a TecplotSystemError.
        if result in [ManagerStartReturnCode.LicenseExpired,
                      ManagerStartReturnCode.LicenseIsInvalid,
                      ManagerStartReturnCode.LicenseFileNotFound,
                      ManagerStartReturnCode.LicenseFileContainsPermanent]:
            raise TecplotLicenseError(errmsg[result])  # License related

        elif result != ManagerStartReturnCode.Ok:
            raise TecplotSystemError(errmsg[result])  # Anything else

        log.info('Tecplot engine started - license acquired')
        info = self.handle.LicenseInfo().decode()
        log.info('License information:\n  ' + info.replace('\n', '\n  '))
        self.started = True

        expire = self.license_expiration
        if isinstance(expire, date):
            days_left = (expire - date.today()).days
            if days_left < 31:
                if self.license_is_roaming:
                    warning_msg = '''
                        Your roaming license will expire in **{} days**.
                    '''
                else:
                    warning_msg = '''
                        Your Tecplot software maintenance subscription
                        (TecPLUS) will expire in **{} days**, after which you
                        will no longer be able to use PyTecplot. Contact
                        sales@tecplot.com to renew your TecPLUS subscription.
                    '''
                warning_msg = dedent(warning_msg).format(days_left)
                warn(warning_msg)

        if self.update_last_message():
            # at this point, the engine has started successfully,
            # but there was an error message.
            # Perhaps an addon did not load correctly.
            lvl = self.last_message.level
            msg = self.last_message.message
            if msg:
                if lvl > logging.WARNING:  # downgrade message to warning
                    lvl = logging.WARNING
                log.log(lvl, msg)

    def stop(self):
        if self.stopped:
            return
        with captured_output(log.debug):
            if self.started:
                self.handle.Stop()
        self.started = False
        self.stopped = True
        log.info('Tecplot engine stopped - license released')

        if __debug__:
            fmt = '{: >8d} {}'
            call_data = (('TecUtil', self._tecutil_call_count),
                         ('Get style', self._style_call_count['GET']),
                         ('Set style', self._style_call_count['SET']))
            for call_type, calls in call_data:
                if calls:
                    data = calls.most_common()
                    msg = '\n'.join(fmt.format(n, f) for f, n in data)
                    log.debug(call_type + ' call counts:\n' + msg)

    @property
    def license_is_valid(self):
        return (self.started and self.handle.LicenseIsValid()) or False

    def acquire_license(self):
        if self.connected:
            msg = dedent('''\
                PyTecplot is connected to a running
                instance of Tecplot 360.
                Disconnect before attempting to proceed in batch-mode.''')
            raise TecplotLogicError(msg)
        self.start()
        if not self.license_is_valid:
            if not self.handle.AcquireLicense():
                raise TecplotLicenseError('Could not acquire a valid license.')

    def release_license(self):
        if self.license_is_valid:
            self.handle.ReleaseLicense()

    @property
    def license_expiration(self):
        self.acquire_license()
        expiration_date = self.handle.LicenseExpirationDate().decode()
        try:
            y,m,d = [int(x) for x in expiration_date.split('-')]
            return date(year=y, month=m, day=d)
        except:
            return expiration_date

    def start_roaming(self, days):
        self.acquire_license()
        if not self.handle.LicenseStartRoaming(int(days)):
            msg = getattr(self.update_last_message(), 'message', None)
            raise TecplotLicenseError(msg)
        expiration_date = self.license_expiration
        if isinstance(expiration_date, date):
            days_left = (expiration_date - date.today()).days
            msg = dedent('''
                You have successfully checked out a roaming license of
                Tecplot. This will be valid for {} days until
                midnight of {}.'''.format(days_left, expiration_date))
            log.critical(msg)

    @property
    def license_is_roaming(self):
        self.acquire_license()
        return self.handle.LicenseIsRoaming()

    def stop_roaming(self, force=False):
        try:
            self.acquire_license()
            if not self.handle.LicenseStopRoaming(False):
                raise TecplotLicenseError
            msg = 'Your Tecplot roaming license has been checked in.'
            log.critical('\n' + msg)
        except TecplotError:
            if force:
                if not self.handle.LicenseStopRoaming(force):
                    raise TecplotLicenseError
                msg = 'The local Tecplot roaming license has been cleared.'
                log.critical('\n' + msg)
            else:
                try:
                    msg = getattr(self.update_last_message(), 'message', '')
                except:
                    msg = ''
                msg += dedent(r'''
                    You may try this command to
                    clear the local roaming license:
                      tecplot.session.stop_roaming(force=True)''')
                raise TecplotLicenseError(msg)

    @property
    def last_message(self):
        return self._last_message

    def clear_last_message(self):
        self._last_message = None

    def log_last_message(self):
        if self.last_message:
            if self.last_message.message:
                log.log(self.last_message.level, self.last_message.message)

    def update_last_message(self):
        def _cleanup_msg(msg):
            msg = msg.decode('utf-8').splitlines()
            return os.linesep.join([s for s in msg if s.strip()])
        self.acquire_license()
        last_message = None
        msg = self.handle.GetTUAssertErrorMessage()
        if msg:
            last_message = TecUtilConnector.Message(
                level=logging.CRITICAL,
                message=_cleanup_msg(msg))
            self.handle.ClearErrorMessage()
        elif __debug__:
            log_level = {
                MessageBoxType.Error: logging.ERROR,
                MessageBoxType.Warning: logging.WARNING,
                MessageBoxType.Information: logging.INFO}
            msg_ptr = self.tecutil_handle.tecUtilLastErrorMessage()
            msg = cast(msg_ptr, c_char_p).value
            self.tecutil_handle.tecUtilStringDealloc(byref(msg_ptr))
            if msg:
                # get message type/level
                mbox_val = self.tecutil_handle.tecUtilLastErrorMessageType()
                mbox_type = MessageBoxType(mbox_val)
                last_message = TecUtilConnector.Message(
                    level=log_level.get(mbox_type, logging.WARNING),
                    message=_cleanup_msg(msg))
                # clean up
                self.tecutil_handle.tecUtilParentLockStart(False)
                try:
                    self.tecutil_handle.tecUtilLastErrorMessageClear()
                finally:
                    self.tecutil_handle.tecUtilParentLockFinish()
        if last_message:
            self._last_message = last_message
        return last_message

    @property
    def sdk_version_info(self):
        if not hasattr(self, '_sdk_version_info'):
            try:
                if self.connected:
                    self._sdk_version_info = SDKVersion(
                        self.client.TecplotGetMajorVersion(),
                        self.client.TecplotGetMinorVersion(),
                        self.client.TecplotGetMajorRevision(),
                        self.client.TecplotGetMinorRevision())
                else:
                    self._sdk_version_info = SDKVersion(
                        self.tecutil_handle.tecUtilTecplotGetMajorVersion(),
                        self.tecutil_handle.tecUtilTecplotGetMinorVersion(),
                        self.tecutil_handle.tecUtilTecplotGetMajorRevision(),
                        self.tecutil_handle.tecUtilTecplotGetMinorRevision())
            except AttributeError:
                self._sdk_version_info = SDKVersion(0, 0, 0, 0)
        return self._sdk_version_info

    @property
    def sdk_version(self):
        version_info = self.sdk_version_info
        if version_info == SDKVersion(0, 0, 0, 0):
            return 'unknown'
        else:
            return '{}.{}-{}-{}'.format(*version_info)

    def update_sdk_version(self):
        import tecplot
        del self._sdk_version_info
        tecplot.version.sdk_version_info = self.sdk_version_info
        tecplot.version.sdk_version = self.sdk_version
        tecplot.sdk_version_info = tecplot.version.sdk_version_info
        tecplot.sdk_version = tecplot.version.sdk_version

    def macro_record_start(self, filename):
        self.start()
        if filename is not None:
            filename = filename.encode('utf-8')
        return self.handle.MacroRecordStart(filename)

    def macro_record_end(self):
        self.handle.MacroRecordEnd()

    def translate_macro_to_python(self, command):
        self.start()
        name_proxy = command.encode('utf-8') if command is not None else command

        self.handle.TranslateMacroToPython.restype = POINTER(c_char)
        result_ptr = self.handle.TranslateMacroToPython(name_proxy)
        tmp_result = cast(result_ptr, c_char_p)
        try:
            result = tmp_result.value.decode('utf-8')
        except:
            result = None
        self.tecutil_handle.tecUtilStringDealloc(byref(result_ptr))

        return result

    def translate_macro_with_raw_data_to_python(self, command):
        self.start()
        name_proxy = command.encode('utf-8') if command is not None else command

        self.handle.TranslateMacroWithRawDataToPython.restype = POINTER(c_char)
        result_ptr = self.handle.TranslateMacroWithRawDataToPython(name_proxy)
        tmp_result = cast(result_ptr, c_char_p)
        try:
            result = tmp_result.value.decode('utf-8')
        except:
            result = None
        self.tecutil_handle.tecUtilStringDealloc(byref(result_ptr))
        return result

_tecutil_connector = TecUtilConnector()
_tecutil = TecUtil(_tecutil_connector)
