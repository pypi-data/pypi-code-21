# -*- coding: utf8 -*-
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
    def test_add_run_add_batches_call_2(self, _run_add_batches, with_repo):
        files_path = './'
        runner = CliRunner()
        volume_id = self.some_random_shit_number_int63()
        fo = fudge.patch('mali_commands.data.with_repo')
        _run_add_batches.expects_call().returns(None).times_called(1)
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
    @fudge.patch('mali_commands.legit.dulwich.porcelain.add')
    @fudge.patch('mali_commands.data.enumerate_paths')
    def test_add_run_add_batches_call(self, add, enumerate_paths):
        from mali_commands.data import _run_add_batches

        total_files = 1000
        paths = ('.,', )

        data_volume_config = fudge.Fake().has_attr(embedded=True)
        repo = fudge.Fake().has_attr(data_volume_config=data_volume_config)
        files = [str(l) for l in range(total_files)]
        bar = fudge.Fake().has_attr(total=total_files)

        enumerate_paths.expects_call().with_args(paths).returns(files)

        # get_batch_of_files_from_paths.expects_call().with_matching_args(total_files, 100).returns(list(range(100)))

        def is_valid(x):
            return len(x) == 250

        add.expects_call().with_matching_args(
            repo,
            arg.passes_test(is_valid),
            # arg.any(),
            True
        ).returns({})

        _run_add_batches(bar, repo, paths, total_files)
