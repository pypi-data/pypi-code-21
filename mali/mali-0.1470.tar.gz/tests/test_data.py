# coding=utf-8
import fudge
import httpretty

from mali import cli
from .base import BaseCliTest
from click.testing import CliRunner
from fudge.inspector import arg
from contextlib import closing


class TestData(BaseCliTest):
    user_org = "user_org_" + BaseCliTest.some_random_shit()
    email_domain = "domain_%s@%s" % (BaseCliTest.some_random_shit(), BaseCliTest.some_random_shit())

    @httpretty.activate
    # @fudge.patch('mali_commands.commons.handle_api')
    def test_add_no_volume(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "add", '-f', './'], catch_exceptions=True)
        self.assertNotEquals(result.exit_code, 0)

    @httpretty.activate
    # @fudge.patch('mali_commands.commons.handle_api')
    def test_add_commit_no_message(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "add", 'dassdasda', '-f', './', '--commit'], catch_exceptions=True)
        self.assertNotEquals(result.exit_code, 0)

    @httpretty.activate
    def test_add_files_invalid_volume_id(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["data", "add", 'dassdasda', '-f', './', '--commit'], catch_exceptions=True)
        self.assertNotEquals(result.exit_code, 0)

    @httpretty.activate
    @fudge.patch('mali_commands.data._run_add_batches')
    @fudge.patch('mali_commands.data.with_repo')
    def test_add_run_add_batches_call(self, _run_add_batches, with_repo):
        files_path = './'
        runner = CliRunner()
        volume_id = self.some_random_shit_number_int63()
        fo = fudge.patch('mali_commands.data.with_repo')
        _run_add_batches.expects_call().with_matching_args((files_path,), arg.any()).returns(None).times_called(1)
        with_repo.expects_call().with_matching_args(arg.any(), volume_id).returns(fo).times_called(1)
        result = runner.invoke(cli, ["data", "add", str(volume_id), '-f', files_path], catch_exceptions=False)
        self.assertEquals(result.exit_code, 0)

    @httpretty.activate
    def test_enumerate_paths(self):
        import os
        import tempfile
        file_count = 100

        def make_temp_files(count):
            for i in range(count):
                f = tempfile.NamedTemporaryFile(suffix='.txt', prefix='test_enumerate_paths__', delete=False)
                f.write(bytearray("Hello World!\n{}\n".format(i), 'utf8'))
                f.close()
                yield f.name

        tempfiles = list(make_temp_files(file_count))
        from mali_commands.data import enumerate_paths
        found_files = 0
        for path in enumerate_paths(tempfiles):
            self.assertIn(path, tempfiles)
            found_files += 1
        self.assertEqual(found_files, file_count)

    @httpretty.activate
    def test_enumerate_404_paths(self):
        import os
        import tempfile
        file_count = 100

        def make_temp_files(count):
            for i in range(count):
                f = tempfile.NamedTemporaryFile(suffix='.txt', prefix='test_enumerate_paths__', delete=True)
                # f.write(bytearray("Hello World!\n{}\n".format(i)))
                f.close()
                yield f.name

        tempfiles = list(make_temp_files(file_count))
        from mali_commands.data import enumerate_paths
        found_files = 0
        with self.assertRaises(SystemExit):
            for path in enumerate_paths(tempfiles):
                self.assertIn(path, tempfiles)
                found_files += 1

    @httpretty.activate
    @fudge.patch('mali_commands.data.enumerate_paths')
    # @fudge.patch('mali_commands.data.get_batch_of_files_from_paths')
    @fudge.patch('mali_commands.legit.dulwich.porcelain.add')
    def test_add_run_add_batches_call(self, enumerate_paths, add):
        from mali_commands.data import _run_add_batches

        files_path = ('./',)
        total_files = 1000
        repo = self.get_obj(data_volume_config=self.get_obj(embedded=True))
        enumerate_paths.expects_call().with_matching_args(files_path).returns(list(range(total_files)))

        # get_batch_of_files_from_paths.expects_call().with_matching_args(total_files, 100).returns(list(range(100)))
        closure_dict = {'LastBatch': False}

        def is_valid(x):
            closure_dict['max_value'] = x[-1]
            if len(x) == 10:
                return True
            elif not closure_dict['LastBatch']:
                closure_dict['LastBatch'] = True
                return True
            return False

        add.expects_call().with_matching_args(
            repo,
            arg.passes_test(is_valid),
            # arg.any(),
            True
        ).returns({})
        _run_add_batches(files_path, repo)
        self.assertEqual(total_files - 1, closure_dict['max_value'])
