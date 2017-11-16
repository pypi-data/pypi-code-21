from __future__ import unicode_literals

import datetime
import logging
import os
import sys
import platform
import unittest
import warnings

from os import path
from six import string_types
from tempfile import NamedTemporaryFile
from unittest.mock import patch, Mock, PropertyMock
from warnings import catch_warnings

import tecplot as tp
from tecplot.exception import *
from tecplot.tecutil.tecutil_connector import TecUtilConnector, find_file
from tecplot.tecutil.tecutil import TecUtil
from tecplot.tecutil import _tecutil_connector, _tecutil, ArgList, lock
import platform

from test import patch_tecutil, skip_if_connected

from ..sample_data import sample_data, loaded_sample_data

class MockInterprocessCDLL:
    @property
    def Start(self):
        class StartObj(object):
            def __init__(self):
                self.restype = None
                self.argtypes = None

            def __call__(self, sdkhome):
                return 2
        return StartObj()

    def Stop(self):
        return None

    @property
    def LicenseInfo(self):
        class LicenseInfoObj(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseInfoObj()

    @property
    def GetTUAssertErrorMessage(self):
        class GetTUAssertErrorMessageObj(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return GetTUAssertErrorMessageObj()

    '''
    @property
    def AcquireLicense(self):
        class AcquireLicense(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return AcquireLicense()

    @property
    def LicenseExpirationDate(self):
        class LicenseExpirationDate(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseExpirationDate()

    @property
    def LicenseIsRoaming(self):
        class LicenseIsRoaming(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseIsRoaming()

    @property
    def LicenseIsValid(self):
        class LicenseIsValid(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseIsValid()

    @property
    def LicenseStartRoaming(self):
        class LicenseStartRoaming(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseStartRoaming()

    @property
    def LicenseStopRoaming(self):
        class LicenseStopRoaming(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return LicenseStopRoaming()

    @property
    def ReleaseLicense(self):
        class ReleaseLicense(object):
            def __init__(self):
                self.restype = None
            def __call__(self):
                return ''
        return ReleaseLicense()
    '''

class TestTecUtilConnector(unittest.TestCase):

    def setUp(self):
        warnings.simplefilter('always')
        self.noexit = patch('sys.exit')
        self.noexit.start()

    def tearDown(self):
        self.noexit.stop()

    def test___init__(self):
        _tecutil_connector = TecUtilConnector()
        self.assertIsInstance(_tecutil_connector, TecUtilConnector)

    def test_pyqt_message(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            with patch('logging.Logger.info') as log:
                sys.modules['PyQt4'] = None
                _tip = TecUtilConnector()
                del sys.modules['PyQt4']
                self.assertEqual(log.call_count, 1)
                self.assertRegex(str(log.call_args_list[0]), r'.*PyQt.*')

    def test_find_file(self):
        with NamedTemporaryFile() as ftmp:
            self.assertEqual(path.abspath(ftmp.name),
                             find_file([path.basename(ftmp.name)],
                                       [path.dirname(ftmp.name)]))

    def test_tecsdkhome(self):
        oldhome = os.environ.get('TECSDKHOME', None)

        with patch.object(TecUtilConnector, '__init__',
                          Mock(return_value=None)):
            tip = TecUtilConnector()
            tip.client = None
            tip.libbatch_path = 'test/test/test'
        os.environ['TECSDKHOME'] = '/non/existant/path'
        self.assertEqual(tip.tecsdkhome, 'test')

        del tip._tecsdkhome
        tip.libbatch_path = None
        self.assertEqual(tip.tecsdkhome, '')

        tip._tecsdkhome = 'test'
        self.assertEqual(tip.tecsdkhome, 'test')

        del tip._tecsdkhome
        # homeenv = 'HOMEPATH' if platform.system() == 'Windows' else 'HOME'
        if platform.system() == 'Windows':
            homedir = path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'])
        else:
            homedir = os.environ['HOME']
        os.environ['TECSDKHOME'] = homedir
        self.assertEqual(tip.tecsdkhome, homedir)

        if oldhome is None:
            del os.environ['TECSDKHOME']
        else:
            os.environ['TECSDKHOME'] = oldhome

    def test_not_64bit_python(self):
        with patch('ctypes.sizeof', Mock(return_value=0)):
            self.assertRaises(TecplotLibraryNotLoadedError, TecUtilConnector)

    def test_unknown_platform(self):
        with patch('platform.system', Mock(return_value='')):
            conn = TecUtilConnector()
            self.assertRaises(TecplotLibraryNotFoundError, conn.start)

    def test_other_known_platforms(self):
        if platform.system() == 'Windows':
            with patch('platform.system', Mock(side_effect=('Linux',
                                                            'Darwin'))):
                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)
        elif platform.system() == 'Linux':
            with patch('platform.system', Mock(side_effect=('Windows',))):
                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)
        elif platform.system() == 'Darwin':
            with patch('platform.system', Mock(side_effect=('Windows',))):
                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)

    def test_load_library_failure(self):
        with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
            conn = TecUtilConnector()
            self.assertRaises((TecplotLibraryNotFoundError,
                               TecplotLibraryNotLoadedError), conn.start)

    def test_load_failures(self):

        if platform.system() in ['Linux', 'Darwin']:
            libpathenv = 'DYLD_LIBRARY_PATH' \
                         if platform.system() == 'Darwin' \
                         else 'LD_LIBRARY_PATH'
            ldlibpath = os.environ.get(libpathenv, None)
            if ldlibpath is not None:
                del os.environ[libpathenv]

            # Test: load_linux._syslibpath
            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecutil_connector.Popen',
                           Mock(side_effect=Exception)):
                    conn = TecUtilConnector()
                    self.assertRaises(TecplotLibraryNotFoundError, conn.start)

                class MockPopen(Mock):
                    def communicate(self):
                        out = b'/non/existant/path\n'
                        err = b'\n'
                        return out, err

                with patch('tecplot.tecutil.tecutil_connector.Popen',
                           MockPopen()):
                    conn = TecUtilConnector()
                    self.assertRaises(TecplotLibraryNotFoundError, conn.start)

            def _findlib(libnames, libpath):
                if libpath is None:
                    return None
                for lib in libnames:
                    for d in libpath.split(os.pathsep):
                        fpath = os.path.join(d, lib)
                        if os.path.exists(fpath):
                            return fpath

            with patch('ctypes.cdll.LoadLibrary', Mock(side_effect=OSError)):
                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)

                foundlib = _findlib(['libtecutil_connector.so'], ldlibpath)
                if foundlib is not None:
                    os.environ[libpathenv] = os.path.dirname(foundlib)

                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)

                envpath = os.environ.get('PATH', None)
                os.environ['PATH'] = '.'
                conn = TecUtilConnector()
                self.assertRaises(TecplotLibraryNotFoundError, conn.start)
                if envpath is not None:
                    os.environ['PATH'] = envpath

            if ldlibpath is not None:
                os.environ[libpathenv] = ldlibpath

            with patch('ctypes.cdll.LoadLibrary',
                       Mock(side_effect=(None, Exception))):
                conn = TecUtilConnector()
                self.assertRaises(Exception, conn.start)

            # Test: load_linux._missinglibs
            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecutil_connector.Popen',
                           Mock(side_effect=Exception)):
                    conn = TecUtilConnector()
                    self.assertRaises((TecplotLibraryNotFoundError,
                                       TecplotLibraryNotLoadedError),
                                      conn.start)

            class MockPopen(Mock):
                def communicate(self):
                    out = b'    libexception.so => not found\n'
                    err = b'\n'
                    return out, err

            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecutil_connector.Popen',
                           MockPopen()):
                    conn = TecUtilConnector()
                    self.assertRaises((TecplotLibraryNotFoundError,
                                       TecplotLibraryNotLoadedError),
                                      conn.start)

                    conn._load_library_error = None
                    self.assertRaises(TecplotLibraryNotLoadedError, conn.start)

                    conn.handle = True
                    conn.stopped = True
                    self.assertRaises(TecplotLibraryNotLoadedError, conn.start)

            class MockPopen(Mock):
                def communicate(self):
                    out = b'    libexception.so => not found\n'
                    err = b'command not found\n'
                    return out, err

            with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
                with patch('tecplot.tecutil.tecutil_connector.Popen',
                           MockPopen()):
                    conn = TecUtilConnector()
                    self.assertRaises((TecplotLibraryNotFoundError,
                                       TecplotLibraryNotLoadedError),
                                      conn.start)

    def test_start_stop(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = TecUtilConnector()
            self.assertRaises((TecplotLicenseError,
                               TecplotOutOfDateEngineError),
                              _tip.start)
            self.assertEqual(_tip.stop(), None)
            _tip.started = True

        def fn(*a):
            raise Exception
        _tip.handle.Stop = fn

        _tip.stopped = True
        _tip.stop()
        _tip.stopped = False
        self.assertRaises(Exception, _tip.stop)

    def test_license_validation(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = TecUtilConnector()

            with patch.object(_tip, 'start'):
                _tip.started = True
                _tip.handle.LicenseIsValid = lambda *a: True
                self.assertTrue(_tip.license_is_valid)

                _tip.handle.AcquireLicense = lambda *a: True
                _tip.acquire_license()

                _tip.handle.LicenseIsValid = lambda *a: False
                self.assertIsNone(_tip.acquire_license())
                self.assertFalse(_tip.license_is_valid)

                _tip.handle.AcquireLicense = lambda *a: False
                self.assertRaises(TecplotLicenseError, _tip.acquire_license)

                _tip.handle.ReleaseLicense = lambda *a: 1 / 0
                _tip.release_license()

                _tip.handle.LicenseIsValid = lambda *a: True
                self.assertRaises(Exception, _tip.release_license)

    def test_error(self):
        _tecutil_connector.clear_last_message()
        self.assertIsNone(_tecutil_connector.last_message)

        # trigger a TUAssert...
        if _tecutil_connector.connected:
            with self.assertRaises(TecplotSystemError):
                _tecutil_connector.client.StateChangedX(None)
            last_message = _tecutil_connector.client.LastErrorMessage()
        else:
            _tecutil_connector.tecutil_handle.tecUtilStateChangedX(None)
            last_message = _tecutil_connector.update_last_message().message

        # error is there and is a string message
        self.assertIsInstance(last_message, string_types)

        _tecutil_connector.clear_last_message()
        self.assertIsNone(_tecutil_connector.last_message)

        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            _tecutil.StateChangedX(None)

        # message already updated
        if _tecutil_connector.connected:
            last_message = _tecutil_connector.client.LastErrorMessage()
            self.assertEqual(last_message, '')
        else:
            self.assertIsNone(_tecutil_connector.update_last_message())
            self.assertIsInstance(_tecutil_connector.last_message.message,
                                  string_types)
            _tecutil_connector.clear_last_message()

        # check that error is clear
        self.assertIsNone(_tecutil_connector.last_message)

    def test_log(self):
        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            _tip = TecUtilConnector()
            with patch('logging.Logger.log') as log:
                cnt = log.call_count
                _tip._last_message = TecUtilConnector.Message(0, 'test')
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

                _tip._last_message = TecUtilConnector.Message(0, '')
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

                _tip._last_message = None
                _tip.log_last_message()
                self.assertEqual(log.call_count, cnt + 1)

    def test_last_error(self):
        with self.assertRaises(TecplotSystemError):
            tp.macro.execute_command('$!bad macro command')
        if not _tecutil_connector.connected:
            if __debug__:
                self.assertIsNotNone(_tecutil_connector.last_message)
            else:
                self.assertIsNone(_tecutil_connector.last_message)
            _tecutil_connector.clear_last_message()

    @skip_if_connected
    def test_no_sdk(self):
        tip = _tecutil_connector
        if hasattr(tip, '_sdk_version_info'):
            del tip._sdk_version_info
        with patch.object(tip.tecutil_handle, 'tecUtilTecplotGetMajorVersion',
                          side_effect=AttributeError):
            self.assertIsInstance(tp.sdk_version_info,
                                  tp.tecutil.tecutil_connector.SDKVersion)
            self.assertEqual(tip.sdk_version, 'unknown')

    @skip_if_connected
    def test_preamble(self):

        info = tp.tecutil.tecutil_connector.TecUtilConnector.Message(logging.INFO, 'info')
        error = tp.tecutil.tecutil_connector.TecUtilConnector.Message(logging.ERROR, 'error')

        with patch('ctypes.cdll.LoadLibrary',
                   Mock(return_value=MockInterprocessCDLL())):
            tecinter = 'tecplot.tecutil.tecutil_connector.TecUtilConnector.'
            with patch(tecinter+'acquire_license',Mock(side_effect=Exception)):
                with patch(tecinter+'update_last_message', Mock(return_value=info)):
                    with patch(tecinter+'log_last_message', Mock()) as loglast:
                        with self.assertRaises(Exception):
                            _tecutil.LockGetCount()
                        self.assertEqual(loglast.call_count, 1)
                with patch(tecinter+'update_last_message', Mock(return_value=error)):
                    with self.assertRaises(TecplotLogicError):
                        _tecutil.LockGetCount()
            with patch(tecinter+'acquire_license',
                       Mock(side_effect=TecplotInitializationError)):
                with self.assertRaises(TecplotInitializationError):
                    _tecutil.LockGetCount()
            with patch(tecinter+'update_last_message', Mock(return_value=info)):
                with patch(tecinter+'log_last_message', Mock()) as loglast:
                    _tecutil.LockGetCount()
                    if __debug__:
                        self.assertEqual(loglast.call_count, 1)
                    else:
                        self.assertEqual(loglast.call_count, 0)
            with patch(tecinter+'update_last_message', Mock(return_value=error)):
                with self.assertRaises(TecplotLogicError):
                    _tecutil.LockGetCount()
            with patch(tecinter+'update_last_message', Mock(return_value=None)):
                _tecutil.LockGetCount()

    @skip_if_connected
    def test_license_expiration(self):
        tip = _tecutil_connector
        with patch.object(tip.handle, 'LicenseExpirationDate',
                          Mock(return_value=b'2020-12-31')):
            self.assertEqual(tip.license_expiration,
                             datetime.date(year=2020,month=12,day=31))
        with patch.object(tip.handle, 'LicenseExpirationDate',
                          Mock(return_value=b'permanent')):
            self.assertIsInstance(tip.license_expiration, string_types)

        try:
            expire_soon = datetime.date.today() + datetime.timedelta(days=5)
            expire_soon_bytes = expire_soon.strftime('%Y-%m-%d').encode()
            expire_later = datetime.date.today() + datetime.timedelta(days=180)
            expire_later_bytes = expire_later.strftime('%Y-%m-%d').encode()
            with patch.object(tip.handle, 'Start', Mock(return_value=0)):
                with patch.object(tip.handle, 'LicenseExpirationDate',
                        PropertyMock(return_value=expire_soon_bytes)):
                    with catch_warnings(record=True) as w:
                        tip.started = False
                        tip.start()
                        msg = str(w[-1].message)
                        self.assertRegex(msg, r'^((?!roaming).)*')
                        self.assertRegex(msg, r'TecPLUS')
                        self.assertRegex(msg, r'\*\*5 days\*\*')
                    with patch.object(tip.handle, 'LicenseIsRoaming',
                            PropertyMock(return_value=True)):
                        with catch_warnings(record=True) as w:
                            tip.started = False
                            tip.start()
                            msg = str(w[-1].message)
                            self.assertRegex(msg, r'roaming')
                            self.assertRegex(msg, r'^((?!TecPlus).)*')
                            self.assertRegex(msg, r'\*\*5 days\*\*')
                with patch.object(tip.handle, 'LicenseExpirationDate',
                        PropertyMock(return_value=expire_later_bytes)):
                    with catch_warnings(record=True) as w:
                        tip.started = False
                        tip.start()
                        self.assertEqual(len(w), 0)
        finally:
            tip.started = True

    @skip_if_connected
    def test_roaming(self):
        expire_date = datetime.date(year=2020,month=12,day=31)
        tip = _tecutil_connector
        tecinter = 'tecplot.tecutil.tecutil_connector.TecUtilConnector.'
        with patch.object(tip, 'acquire_license'):
            with patch(tecinter+'license_expiration',
                       PropertyMock(return_value=expire_date)):
                with patch.object(tip.handle, 'LicenseStartRoaming',
                                  Mock(return_value=True)):
                    tip.start_roaming(5)
                    with patch(tecinter+'license_expiration',
                               PropertyMock(return_value='permanent')):
                        tip.start_roaming(5)
                with patch.object(tip.handle, 'LicenseStartRoaming',
                                  Mock(return_value=False)):
                    self.assertRaises(TecplotLicenseError,
                                      lambda: tip.start_roaming(5))
            with patch.object(tip.handle, 'LicenseStopRoaming',
                              Mock(return_value=True)):
                tip.stop_roaming()
            with patch.object(tip.handle, 'LicenseStopRoaming',
                              Mock(return_value=False)):
                self.assertRaises(TecplotLicenseError, tip.stop_roaming)

        with patch.object(tip, 'acquire_license', Mock(side_effect=TecplotError)):
            with patch.object(tip.handle, 'LicenseStopRoaming', Mock(return_value=False)):
                with self.assertRaises(TecplotLicenseError):
                    tip.stop_roaming(force=True)

            with patch.object(tip.handle, 'LicenseStopRoaming', Mock(return_value=True)):
                with patch('logging.Logger.critical') as log:
                    tip.stop_roaming(force=True)
                    self.assertEqual(log.call_count, 1)
                    self.assertRegex(str(log.call_args_list[0]),
                                     r'.*has been cleared.*')

            with patch.object(tip, 'update_last_message',
                              Mock(side_effect=Exception)):
                with self.assertRaises(TecplotLicenseError):
                    tip.stop_roaming()

    #def test_connections(self):
    #    with patch('ctypes.cdll.LoadLibrary', Mock(return_value=None)):
    #        conn = TecUtilConnector()
    #        self.assertRaises(TecplotNotImplementedError, conn.connect)
    #        self.assertRaises(TecplotNotImplementedError, conn.disconnect)
    #        self.assertFalse(conn.connected)

    #def test_no_bindings(self):
    #    handle_orig = tp.tecutil._tecutil.handle
    #    try:
    #        tp.tecutil._tecutil.handle = None
    #        tp.tecutil.IndexSet._bind_tecutil()
    #        tp.tecutil.StringList._bind_tecutil()
    #    finally:
    #        tp.tecutil._tecutil.handle = handle_orig
    #        tp.tecutil.IndexSet._bind_tecutil()
    #        tp.tecutil.StringList._bind_tecutil()


class TestTecutil(unittest.TestCase):

    #def test_init(self):
    #    _tecutil = TecUtil(_tecutil_connector)
    #    self.assertIsInstance(_tecutil, TecUtil)
    #
    #    # rebind tecutil because the above statements are modifying
    #    # the real _tecutil/_tecutil_connector
    #    tp.tecutil.IndexSet._bind_tecutil()
    #    tp.tecutil.StringList._bind_tecutil()

    def test_exceptions(self):
        with self.assertRaises((TecplotLogicError, TecplotSystemError)):
            _tecutil.StateChangedX(None)  # ctypes OK, TUAsserts

        with self.assertRaises(TypeError):
            _tecutil.AnimateIJKPlanes(None)  # ctypes wrong nargs

        with self.assertRaises((AttributeError, TypeError)):
            _tecutil.FieldLayerIsActive(1)  # ctypes wrong arg type


if __name__ == '__main__':
    from .. import main
    main()
