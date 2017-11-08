import logging
import os
import shutil
import json
from filecmp import dircmp

from click.testing import CliRunner

from tests.base import BaseCliTest, global_some_random_shit
from mali import cli
from mali_commands.utilities.os_utils import create_dir, remove_dir


MALI_INTEGRATION_SERVER_ENV = os.environ.get('MALI_INTEGRATION_SERVER_ENV', 'staging').lower()
MALI_CONFIG_PREFIX = 'test-%s' % MALI_INTEGRATION_SERVER_ENV
MALI_CONFIG_FILENAME = '%s-missinglink.cfg' % MALI_CONFIG_PREFIX

IGNORED_FILES = [
    '.DS_Store',
    'test-staging-missinglink.cfg',
    'test-prod-missinglink.cfg',
]


def create_file(filename, content=None):
    dirname = os.path.dirname(filename)

    create_dir(dirname)

    content = content or global_some_random_shit(size=1024 * 4)
    with open(filename, 'w') as f:
        f.write(content)


class BaseTest(BaseCliTest):
    def setUp(self):
        super(BaseTest, self).setUp()
        self.runner = CliRunner()

        # We create `./temp` for creating temporary files. It will be deleted on `tearDown`.
        # Under `./temp`, there are:
        # - `data` which contains data files used for committing
        # - `clone` which can be use to clone the data volume
        # At the beginning of each test, the current directory is at `./temp/data`.
        self.test_root_dir = os.getcwd()
        self.temp_dir = os.path.join(self.test_root_dir, 'temp')
        self.data_dir = os.path.join(self.temp_dir, 'data')
        self.clone_dir = os.path.join(self.temp_dir, 'cloned')

        # All data management tests should run at the relative dir `./temp`
        create_dir(self.data_dir)
        shutil.copy(MALI_CONFIG_FILENAME, os.path.join(self.data_dir, MALI_CONFIG_FILENAME))
        os.chdir(self.data_dir)

    def tearDown(self):
        super(BaseTest, self).tearDown()

        os.chdir(self.test_root_dir)
        remove_dir(self.temp_dir)

    def populate_data(self, filenames):
        for filename in filenames:
            path = os.path.join(filename)
            create_file(path)

    def create_data_volume(self, display_name='TestVolume', org='me', data_path=''):
        logging.info("Creating data volume with display name = '%s', org = '%s', data_path = '%s' ..." % (display_name, org, data_path))

        result = self._run_command([
            'data', 'create',
            '--displayName', display_name,
            '--org', org,
            '--dataPath', data_path
        ])
        return json.loads(result.output)['id']

    def add_file(self, volume_id, filenames):
        logging.info('In volume %s, adding files: %s ...', volume_id, filenames)

        return self._run_command([
            'data', 'add', volume_id,
            '--files', ' '.join(filenames),
        ])

    def add_metadata(self, volume_id, filenames, metadata):
        logging.info('In volume %s, adding metadata %s to files: %s ...', volume_id, metadata, filenames)

        return self._run_command([
            'data', 'metadata', 'add', volume_id,
            '--files', ' '.join(filenames),
            '--data', json.dumps(metadata)
        ])

    def commit(self, volume_id, message=''):
        logging.info('In volume %s, committing: %s ...', volume_id, message)

        result = self._run_command([
            'data', 'commit', volume_id,
            '--message', message
        ])
        return json.loads(result.output)['commit_id']

    def clone(self, volume_id, dest, query):
        print("Cloning volume %s, with query '%s' ..." % (volume_id, query))

        return self._run_command([
            'data', 'clone', volume_id,
            '--dest', dest,
            '--query', query
        ])

    def _run_command(self, command_args, should_assert=True):
        mali_test_args = [
            '--outputFormat', 'json',
            '--configPrefix', MALI_CONFIG_PREFIX
        ]
        args = mali_test_args + command_args
        result = self.runner.invoke(cli, args, catch_exceptions=False)

        logging.info('Command run: %s', ' '.join(['mali'] + args))
        logging.info('Command status: %d, output: %s', result.exit_code, result.output)

        if should_assert:
            self.assertEqual(result.exit_code, 0, 'run command %s failed' % command_args)

        return result

    def assertEqualDir(self, dir1, dir2):
        dir_diff = dircmp(dir1, dir2, ignore=IGNORED_FILES)
        self._assertEqualDirRecursively(dir_diff)

    def _assertEqualDirRecursively(self, dir_diff):
        if dir_diff.left_only:
            dir_diff.left_only.sort()
            msg = 'Only in %s: %s' % (dir_diff.left, dir_diff.left_only)
            self._raiseDirDiffException(dir_diff, msg)

        if dir_diff.right_only:
            dir_diff.right_only.sort()
            msg = 'Only in %s: %s' % (dir_diff.right, dir_diff.right_only)
            self._raiseDirDiffException(dir_diff, msg)

        if dir_diff.diff_files:
            dir_diff.diff_files.sort()
            msg = 'Differing files: %s' % dir_diff.diff_files
            self._raiseDirDiffException(dir_diff, msg)

        if dir_diff.common_funny:
            dir_diff.common_funny.sort()
            msg = 'Common funny cases: %s' % dir_diff.common_funny
            self._raiseDirDiffException(dir_diff, msg)

        if dir_diff.funny_files:
            dir_diff.funny_files.sort()
            msg = 'Trouble with common files: %s' % dir_diff.funny_files
            self._raiseDirDiffException(dir_diff, msg)

        for subdir, subdir_diff in dir_diff.subdirs.items():
            self._assertEqualDirRecursively(subdir_diff)

    def _raiseDirDiffException(self, dir_diff, msg):
        msg = "Diffing '%s' and '%s'...\n%s" % (dir_diff.left, dir_diff.right, msg)
        raise self.failureException(msg)
