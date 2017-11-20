# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.zestreleaser.customupload.upload
import mock
import tempfile
import unittest


class UploadTest(unittest.TestCase):

    context = {
        'tagdir': '/tmp/tha.example-0.1dev',
        'tag_already_exists': False,
        'version': '0.1dev',
        'workingdir': '/tmp/tha.example-svn',
        'name': 'tha.example',
    }

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    def test_no_destination_should_be_noop(self, ask, choose):
        choose.return_value = None
        gocept.zestreleaser.customupload.upload.upload(self.context)
        self.assertFalse(ask.called)

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('os.system')
    def test_no_confirmation_should_exit(self, system, ask, choose):
        choose.return_value = 'server'
        ask.return_value = False
        gocept.zestreleaser.customupload.upload.upload(self.context)
        self.assertTrue(ask.called)
        self.assertFalse(system.called)

    @mock.patch('gocept.zestreleaser.customupload.upload.choose_destination')
    @mock.patch('zest.releaser.utils.ask')
    @mock.patch('os.system')
    @mock.patch('glob.glob')
    def test_call_scp(self, glob, system, ask, choose):
        choose.return_value = 'server:'
        ask.return_value = True
        glob.return_value = [
            '/tmp/tha.example-0.1dev/dist/tha.example-0.1dev.tar.gz']
        gocept.zestreleaser.customupload.upload.upload(self.context)
        system.assert_called_with(
            'scp -P 22 /tmp/tha.example-0.1dev/dist/tha.example-0.1dev.tar.gz '
            'server:')


class ProtocollSeparatorTest(unittest.TestCase):

    def get_call(self, destination):
        return gocept.zestreleaser.customupload.upload.get_calls(
            ['/path/to/source1', '/path/to/source2'], destination)

    def test_no_protocol_should_use_scp(self):
        self.assertEqual(
            [['scp', '-P 22', '/path/to/source1', '/path/to/source2',
              'localhost:/apath']],
            self.get_call('localhost:/apath'))

    def test_scp_should_use_scp(self):
        self.assertEqual(
            [['scp', '-P 22', '/path/to/source1', '/path/to/source2',
              'localhost:apath']],
            self.get_call('scp://localhost/apath'))

    def test_scp_should_allow_absolute_path(self):
        self.assertEqual(
            [['scp', '-P 22', '/path/to/source1', '/path/to/source2',
              'localhost:/apath']],
            self.get_call('scp://localhost//apath'))

    def test_scp_with_different_port(self):
        self.assertEqual(
            [['scp', '-P 7569', '/path/to/source1', '/path/to/source2',
              'localhost:/apath']],
            self.get_call('scp://localhost:7569//apath'))

    def test_http_should_use_curl_and_put(self):
        self.assertEqual(
            [['curl', '-X', 'PUT', '--data-binary', '@/path/to/source1',
              'http://localhost/apath/source1'],
             ['curl', '-X', 'PUT', '--data-binary', '@/path/to/source2',
              'http://localhost/apath/source2']],
            self.get_call('http://localhost/apath'))

    def test_https_should_use_curl_and_put(self):
        self.assertEqual(
            [['curl', '-X', 'PUT', '--data-binary', '@/path/to/source1',
              'https://localhost/apath/source1'],
             ['curl', '-X', 'PUT', '--data-binary', '@/path/to/source2',
              'https://localhost/apath/source2']],
            self.get_call('https://localhost/apath'))

    def test_http_should_honour_trailing_slash(self):
        self.assertEqual(
            [['curl', '-X', 'PUT', '--data-binary', '@/path/to/source1',
              'http://localhost/apath/source1'],
             ['curl', '-X', 'PUT', '--data-binary', '@/path/to/source2',
              'http://localhost/apath/source2']],
            self.get_call('http://localhost/apath/'))

    def test_https_should_add_additional_options_to_curl(self):
        self.assertEqual(
            [['curl', '--insecure', '-X', 'PUT', '--data-binary',
              '@/path/to/source1', 'http://localhost/apath/source1'],
             ['curl', '--insecure', '-X', 'PUT', '--data-binary',
              '@/path/to/source2', 'http://localhost/apath/source2']],
            self.get_call('--insecure http://localhost/apath/'))

    def test_sftp(self):
        self.assertEqual(
            [['echo', '"put /path/to/source1"', '|', 'sftp', '-P 22',
              '-b', '-', 'user@localhost://apath'],
             ['echo', '"put /path/to/source2"', '|', 'sftp', '-P 22',
              '-b', '-', 'user@localhost://apath']],
            self.get_call('sftp://user@localhost//apath'))

    def test_sftp_with_different_port(self):
        self.assertEqual(
            [['echo', '"put /path/to/source1"', '|', 'sftp', '-P 7596',
              '-b', '-', 'user@localhost://apath'],
             ['echo', '"put /path/to/source2"', '|', 'sftp', '-P 7596',
              '-b', '-', 'user@localhost://apath']],
            self.get_call('sftp://user@localhost:7596//apath'))


class ConfigTest(unittest.TestCase):

    @mock.patch('os.path.expanduser')
    def test_returns_configparser(self, expanduser):
        tmpfile = tempfile.NamedTemporaryFile()
        expanduser.return_value = tmpfile.name
        tmpfile.write(u"""
[gocept.zestreleaser.customupload]
my.package = my.dest
other.package = other.dest
""".encode('ascii'))
        tmpfile.flush()
        config = gocept.zestreleaser.customupload.upload.read_configuration(
            'mock')
        self.assertEqual('my.dest', config.get(
            'gocept.zestreleaser.customupload', 'my.package'))

    def test_file_not_present_silently_ignores_it(self):
        config = gocept.zestreleaser.customupload.upload.read_configuration(
            'doesnotexist')
        self.assertEqual([], config.sections())
