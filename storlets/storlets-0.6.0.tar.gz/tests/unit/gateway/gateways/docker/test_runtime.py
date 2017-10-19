# Copyright (c) 2010-2015 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
import os
import unittest
import tempfile
import errno
from contextlib import contextmanager
from six import StringIO
from stat import ST_MODE

from storlets.gateway.common.exceptions import StorletRuntimeException, \
    StorletTimeout
from storlets.gateway.gateways.docker.gateway import DockerStorletRequest
from storlets.gateway.gateways.docker.runtime import RunTimeSandbox, \
    RunTimePaths, StorletInvocationProtocol
from tests.unit import FakeLogger, with_tempdir
from tests.unit.gateway.gateways import FakeFileManager


@contextmanager
def _mock_sbus(send_status=0):
    with mock.patch('storlets.gateway.gateways.docker.runtime.'
                    'SBus.send') as fake_send:
        fake_send.return_value = send_status
        yield


@contextmanager
def _mock_os_pipe(bufs):
    class FakeFd(object):
        def __init__(self, rbuf=''):
            self.rbuf = rbuf
            self.closed = False

        def read(self, size):
            size = min(len(self.rbuf), size)
            ret = self.rbuf[:size]
            self.rbuf = self.rbuf[size:]
            return ret

        def close(self):
            if self.closed:
                raise OSError(errno.EBADF, os.strerror(errno.EBADF))
            self.closed = True

    def fake_os_read(fd, size):
        return fd.read(size)

    def fake_os_close(fd):
        fd.close()

    pipes = [(FakeFd(buf), FakeFd()) for buf in bufs]
    pipe_generator = iter(pipes)

    def mock_os_pipe():
        try:
            return next(pipe_generator)
        except StopIteration:
            raise AssertionError('pipe called more than expected')

    with mock.patch('storlets.gateway.gateways.docker.runtime.os.pipe',
                    mock_os_pipe), \
        mock.patch('storlets.gateway.gateways.docker.runtime.os.read',
                   fake_os_read) as fake_os_read,\
        mock.patch('storlets.gateway.gateways.docker.runtime.os.close',
                   fake_os_close) as fake_os_close:
        yield pipes


class TestRuntimePaths(unittest.TestCase):

    def setUp(self):
        self.scope = '0123456789abc'
        self._initialize()

    def _initialize(self):
        # TODO(takashi): take these values from config file
        base_dir = '/home/docker_device'
        self.script_dir = os.path.join(base_dir, 'scripts')
        self.pipes_dir = os.path.join(base_dir, 'pipes', 'scopes')
        self.storlets_dir = os.path.join(base_dir, 'storlets', 'scopes')
        self.log_dir = os.path.join(base_dir, 'logs', 'scopes')
        self.cache_dir = os.path.join(base_dir, 'cache', 'scopes')

        self.conf = {}
        self.storlet_id = 'org.openstack.storlet.mystorlet'
        self.paths = RunTimePaths(self.scope, self.conf)

    def tearDown(self):
        pass

    def test_host_pipe_prefix(self):
        self.assertEqual(
            self.paths.host_pipe_prefix(),
            os.path.join(self.pipes_dir, self.scope))

    def test_create_host_pipe_prefix(self):
        pipedir = self.paths.host_pipe_prefix()

        # When the directory exists
        with mock.patch('os.path.exists', return_value=True), \
                mock.patch('os.makedirs') as m, \
                mock.patch('os.chmod') as c:
            self.paths.create_host_pipe_prefix()
            self.assertEqual(0, m.call_count)
            cargs, ckwargs = c.call_args
            # Make sure about the target directory
            self.assertEqual(cargs[0], pipedir)

        # When the directory does not exist
        with mock.patch('os.path.exists', return_value=False), \
                mock.patch('os.makedirs') as m, \
                mock.patch('os.chmod') as c:
            self.paths.create_host_pipe_prefix(),
            self.assertEqual(1, m.call_count)
            # Make sure about the target directory
            margs, mkwargs = m.call_args
            self.assertEqual(margs[0], pipedir)
            cargs, ckwargs = c.call_args
            self.assertEqual(cargs[0], pipedir)

    def test_host_factory_pipe(self):
        self.assertEqual(
            self.paths.host_factory_pipe(),
            os.path.join(self.pipes_dir, self.scope, 'factory_pipe'))

    def test_host_storlet_pipe(self):
        self.assertEqual(
            self.paths.host_storlet_pipe(self.storlet_id),
            os.path.join(self.pipes_dir, self.scope, self.storlet_id))

    def test_sbox_storlet_pipe(self):
        self.assertEqual(
            self.paths.sbox_storlet_pipe(self.storlet_id),
            os.path.join('/mnt/channels', self.storlet_id))

    def test_sbox_storlet_exec(self):
        self.assertEqual(
            self.paths.sbox_storlet_exec(self.storlet_id),
            os.path.join('/home/swift', self.storlet_id))

    def test_host_storlet_prefix(self):
        self.assertEqual(
            self.paths.host_storlet_prefix(),
            os.path.join(self.storlets_dir, self.scope))

    def test_host_storlet(self):
        self.assertEqual(
            self.paths.host_storlet(self.storlet_id),
            os.path.join(self.storlets_dir, self.scope,
                         self.storlet_id))

    def test_slog_path(self):
        with mock.patch('os.path.exists', return_value=True), \
            mock.patch('os.makedirs') as m:
            self.assertEqual(
                self.paths.slog_path(self.storlet_id),
                os.path.join(self.log_dir, self.scope,
                             self.storlet_id))
            self.assertEqual(0, m.call_count)

        with mock.patch('os.path.exists', return_value=False), \
            mock.patch('os.makedirs') as m:
            self.assertEqual(
                self.paths.slog_path(self.storlet_id),
                os.path.join(self.log_dir, self.scope,
                             self.storlet_id))
            self.assertEqual(1, m.call_count)

    def test_get_host_storlet_cache_dir(self):
        self.assertEqual(
            self.paths.get_host_storlet_cache_dir(),
            os.path.join(self.cache_dir, self.scope, 'storlet'))

    def test_get_host_dependency_cache_dir(self):
        self.assertEqual(
            self.paths.get_host_dependency_cache_dir(),
            os.path.join(self.cache_dir, self.scope, 'dependency'))

    def test_runtime_paths_default(self):
        # CHECK: docs  says we need 4 dirs for communicate
        # ====================================================================
        # |1| host_factory_pipe_path    | <pipes_dir>/<scope>/factory_pipe   |
        # ====================================================================
        # |2| host_storlet_pipe_path    | <pipes_dir>/<scope>/<storlet_id>   |
        # ====================================================================
        # |3| sandbox_factory_pipe_path | /mnt/channels/factory_pipe         |
        # ====================================================================
        # |4| sandbox_storlet_pipe_path | /mnt/channels/<storlet_id>         |
        # ====================================================================
        #
        # With this test,  the scope value is "account" and the storlet_id is
        # "Storlet-1.0.jar" (app name?)
        # ok, let's check for these values

        runtime_paths = RunTimePaths('account', {})
        storlet_id = 'Storlet-1.0.jar'

        # For pipe
        self.assertEqual('/home/docker_device/pipes/scopes/account',
                         runtime_paths.host_pipe_prefix())

        # 1. host_factory_pipe_path <pipes_dir>/<scope>/factory_pipe
        self.assertEqual(
            '/home/docker_device/pipes/scopes/account/factory_pipe',
            runtime_paths.host_factory_pipe())
        # 2. host_storlet_pipe_path <pipes_dir>/<scope>/<storlet_id>
        self.assertEqual(
            '/home/docker_device/pipes/scopes/account/Storlet-1.0.jar',
            runtime_paths.host_storlet_pipe(storlet_id))
        # 3. Yes, right now, we don't have the path for #3 in Python
        # 4. sandbox_storlet_pipe_path | /mnt/channels/<storlet_id>
        self.assertEqual('/mnt/channels/Storlet-1.0.jar',
                         runtime_paths.sbox_storlet_pipe(storlet_id))

        # This looks like for jar load?
        self.assertEqual('/home/docker_device/storlets/scopes/account',
                         runtime_paths.host_storlet_prefix())
        self.assertEqual(
            '/home/docker_device/storlets/scopes/account/Storlet-1.0.jar',
            runtime_paths.host_storlet(storlet_id))
        # And this one is a mount poit in sand box?
        self.assertEqual('/home/swift/Storlet-1.0.jar',
                         runtime_paths.sbox_storlet_exec(storlet_id))

    @with_tempdir
    def test_create_host_pipe_prefix_with_real_dir(self, temp_dir):
        runtime_paths = RunTimePaths('account', {'host_root': temp_dir})
        runtime_paths.create_host_pipe_prefix()
        path = runtime_paths.host_pipe_prefix()
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))
        permission = oct(os.stat(path)[ST_MODE])[-3:]
        # TODO(kota_): make sure if this is really acceptable
        self.assertEqual('777', permission)


class TestRuntimePathsTempauth(TestRuntimePaths):
    def setUp(self):
        self.scope = 'test'
        self._initialize()


class TestRunTimeSandbox(unittest.TestCase):
    def setUp(self):
        self.logger = FakeLogger()
        # TODO(takashi): take these values from config file
        self.conf = {'docker_repo': 'localhost:5001'}
        self.scope = '0123456789abc'
        self.sbox = RunTimeSandbox(self.scope, self.conf, self.logger)

    def tearDown(self):
        pass

    def test_parse_sandbox_factory_answer(self):
        status, msg = self.sbox._parse_sandbox_factory_answer('True:message')
        self.assertTrue(status)
        self.assertEqual('message', msg)

        status, msg = self.sbox._parse_sandbox_factory_answer('False:message')
        self.assertFalse(status)
        self.assertEqual('message', msg)

        with self.assertRaises(StorletRuntimeException):
            self.sbox._parse_sandbox_factory_answer('Foo')

    def _check_all_pipese_closed(self, pipes):
        for _pipe in pipes:
            self.assertTrue(_pipe[0].closed)
            self.assertTrue(_pipe[1].closed)

    def test_ping(self):
        with _mock_os_pipe(['True:OK']) as pipes, _mock_sbus(0):
            self.assertEqual(1, self.sbox.ping())
            self._check_all_pipese_closed(pipes)

        with _mock_os_pipe(['False:ERROR']) as pipes, _mock_sbus(-1):
            self.assertEqual(-1, self.sbox.ping())
            self._check_all_pipese_closed(pipes)

        with _mock_os_pipe(['Foo']) as pipes, _mock_sbus(0):
            with self.assertRaises(StorletRuntimeException):
                self.sbox.ping()
            self._check_all_pipese_closed(pipes)

    def test_wait(self):
        with _mock_os_pipe(['True:OK']) as pipes, _mock_sbus(0), \
            mock.patch('storlets.gateway.gateways.docker.runtime.'
                       'time.sleep') as _s:
            self.sbox.wait()
            self.assertEqual(0, _s.call_count)
            self._check_all_pipese_closed(pipes)

        with _mock_os_pipe(['False:ERROR', 'True:OK']) as pipes, \
            _mock_sbus(0), \
            mock.patch('storlets.gateway.gateways.docker.runtime.'
                       'time.sleep') as _s:
            self.sbox.wait()
            self.assertEqual(1, _s.call_count)
            self._check_all_pipese_closed(pipes)

        with _mock_os_pipe(['Foo']) as pipes, _mock_sbus(0), \
            mock.patch('storlets.gateway.gateways.docker.runtime.'
                       'time.sleep') as _s:
            with self.assertRaises(StorletRuntimeException):
                self.sbox.wait()
            self._check_all_pipese_closed(pipes)

        # TODO(takashi): should test timeout case

    def test_restart(self):
        with mock.patch('storlets.gateway.gateways.docker.runtime.'
                        'RunTimePaths.create_host_pipe_prefix'), \
            mock.patch('storlets.gateway.gateways.docker.runtime.'
                       'subprocess.call'):
            _wait = self.sbox.wait

            def dummy_wait_success(*args, **kwargs):
                return 1

            self.sbox.wait = dummy_wait_success
            self.sbox.restart()
            self.sbox.wait = _wait

        with mock.patch('storlets.gateway.gateways.docker.runtime.'
                        'RunTimePaths.create_host_pipe_prefix'), \
            mock.patch('storlets.gateway.gateways.docker.runtime.'
                       'subprocess.call'):
            _wait = self.sbox.wait

            def dummy_wait_failure(*args, **kwargs):
                raise StorletRuntimeException()

            self.sbox.wait = dummy_wait_failure
            with self.assertRaises(StorletRuntimeException):
                self.sbox.restart()
            self.sbox.wait = _wait

    def test_get_storlet_classpath(self):
        storlet_id = 'Storlet.jar'
        storlet_main = 'org.openstack.storlet.Storlet'
        dependencies = ['dep1', 'dep2']
        self.assertEqual(
            '/home/swift/org.openstack.storlet.Storlet/Storlet.jar:'
            '/home/swift/org.openstack.storlet.Storlet/dep1:'
            '/home/swift/org.openstack.storlet.Storlet/dep2',
            self.sbox._get_storlet_classpath(storlet_main, storlet_id,
                                             dependencies),)


class TestStorletInvocationProtocol(unittest.TestCase):
    def setUp(self):
        self.pipe_path = tempfile.mktemp()
        self.log_file = tempfile.mktemp()
        self.logger = FakeLogger()
        storlet_id = 'Storlet-1.0.jar'
        options = {'storlet_main': 'org.openstack.storlet.Storlet',
                   'storlet_dependency': 'dep1,dep2',
                   'storlet_language': 'java',
                   'file_manager': FakeFileManager('storlet', 'dep')}
        storlet_request = DockerStorletRequest(
            storlet_id, {}, {}, iter(StringIO()), options=options)
        self.protocol = StorletInvocationProtocol(
            storlet_request, self.pipe_path, self.log_file, 1, self.logger)

    def tearDown(self):
        for path in [self.pipe_path, self.log_file]:
            try:
                os.unlink(path)
            except OSError:
                pass

    def test_invocation_protocol(self):
        # os.pipe will be called 4 times
        pipe_called = 4

        with _mock_sbus(0), _mock_os_pipe([''] * pipe_called) as pipes:
            with mock.patch.object(
                    self.protocol, '_wait_for_read_with_timeout'):
                self.protocol._invoke()

            self.assertEqual(pipe_called, len(pipes))
            pipes = iter(pipes)

            # data write is not directly closed
            # data read is closed
            input_data_read_fd, input_data_write_fd = next(pipes)
            self.assertTrue(input_data_read_fd.closed)
            self.assertFalse(input_data_write_fd.closed)

            # data write is closed but data read is still open
            data_read_fd, data_write_fd = next(pipes)
            self.assertFalse(data_read_fd.closed)
            self.assertTrue(data_write_fd.closed)

            # both execution str fds are closed
            execution_read_fd, execution_write_fd = next(pipes)
            self.assertTrue(execution_read_fd.closed)
            self.assertTrue(execution_write_fd.closed)

            # metadata write fd is closed, metadata read fd is still open.
            metadata_read_fd, metadata_write_fd = next(pipes)
            self.assertFalse(metadata_read_fd.closed)
            self.assertTrue(metadata_write_fd.closed)

            # sanity
            self.assertRaises(StopIteration, next, pipes)

    def test_invocation_protocol_remote_fds(self):
        # In default, we have 5 fds in remote_fds
        storlet_id = 'Storlet-1.0.jar'
        options = {'storlet_main': 'org.openstack.storlet.Storlet',
                   'storlet_dependency': 'dep1,dep2',
                   'storlet_language': 'java',
                   'file_manager': FakeFileManager('storlet', 'dep')}
        storlet_request = DockerStorletRequest(
            storlet_id, {}, {}, iter(StringIO()), options=options)
        protocol = StorletInvocationProtocol(
            storlet_request, self.pipe_path, self.log_file, 1, self.logger)
        self.assertEqual(5, len(protocol.remote_fds))

        # extra_resources expands the remote_fds
        storlet_request = DockerStorletRequest(
            storlet_id, {}, {}, iter(StringIO()), options=options)
        protocol = StorletInvocationProtocol(
            storlet_request, self.pipe_path, self.log_file, 1, self.logger,
            extra_sources=[storlet_request])
        self.assertEqual(6, len(protocol.remote_fds))

        # 2 more extra_resources expands the remote_fds
        storlet_request = DockerStorletRequest(
            storlet_id, {}, {}, iter(StringIO()), options=options)
        protocol = StorletInvocationProtocol(
            storlet_request, self.pipe_path, self.log_file, 1, self.logger,
            extra_sources=[storlet_request] * 3)
        self.assertEqual(8, len(protocol.remote_fds))

    def test_open_writer_with_invalid_fd(self):
        invalid_fds = (
            (None, TypeError), (-1, ValueError), ('blah', TypeError))

        for invalid_fd, expected_error in invalid_fds:
            with self.assertRaises(expected_error):
                with self.protocol._open_writer(invalid_fd):
                    pass

    def _test_writer_with_exception(self, exception_cls):
        pipes = [os.pipe()]

        def raise_in_the_context():
            with self.protocol._open_writer(pipes[0][1]):
                raise exception_cls()
        try:
            # writer context doesn't suppress any exception
            self.assertRaises(exception_cls, raise_in_the_context)

            # since _open_writer closes the write fd, the os.close will fail as
            # BadFileDescriptor
            with self.assertRaises(OSError) as os_error:
                os.close(pipes[0][1])
            self.assertEqual(9, os_error.exception.errno)

        finally:
            for fd in pipes[0]:
                try:
                    os.close(fd)
                except OSError:
                    pass

    def test_writer_raise_while_in_writer_context(self):
        # basic storlet timeout
        self._test_writer_with_exception(StorletTimeout)
        # unexpected IOError
        self._test_writer_with_exception(IOError)
        # else
        self._test_writer_with_exception(Exception)


if __name__ == '__main__':
    unittest.main()
