from os import environ, makedirs, path
import subprocess
import time
from util import merge, TMP_DIR, STDERR_LOGGER, STDOUT_LOGGER, check_cmd
import shutil


################################
# Device Runner
################################
class DeviceRunner(object):
    def __init__(self, device):
        self.device = device
        self.latest_report_dir = None

    def check(self, name):
        if not check_cmd(name):
            self.call(['brew', 'install', name])

    # cmd is a string array
    def call(self, cmd, env=None):
        if STDOUT_LOGGER.is_used:
            # if custom logger is used, use it too
            main_proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            tee_proc = subprocess.Popen(['tee', '-a', STDOUT_LOGGER.file_path], stdin=main_proc.stdout,
                                        stdout=STDOUT_LOGGER, stderr=STDERR_LOGGER)
            tee_proc.wait()
            tee_proc.communicate()
        else:
            subprocess.call(cmd, env=env)

    def prepare_env(self, *envs):
        base = environ.copy()
        for env in envs:
            base = merge(base, env)
        return base

    def install(self, build):
        self.inner_install(build, True)

    def uninstall(self, build):
        self.inner_install(build, False)

    def inner_install(self, build, install=True):
        for tool in self.device.get_cli_tools():
            self.check(tool)

        cmds = self.device.get_install_cmds(build) if install else self.device.get_uninstall_cmds(build)

        env = self.prepare_env(
                self.device.get_env(),
                self.device.get_build_env(build)
        )

        for cmd in cmds:
            self.call(cmd, env)

    def open_console(self, build):
        cmd = self.device.get_console_cmd(build)
        env = self.prepare_env(
                self.device.get_env(),
                self.device.get_build_env(build)
        )
        self.call(cmd, env)

    def run_test(self, test, build, version_names_getter, report=False):
        timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
        tmp = TMP_DIR
        tmp_out = self.get_current_report_dir(parent=tmp, timestamp=timestamp)
        real_out = self.get_device_reports_dir(parent=test.output_dir)

        # prepare command
        base_cmd = self.device.get_run_cmd(build)
        test_cmd = TestCmdBuilder.build_cmd(test, tmp_out, report)
        version_tags = VersionCmdBuilder.build_cmd(self.device, build, version_names_getter)
        cmd = base_cmd + test_cmd + version_tags

        # prepare env
        env = self.prepare_env(
                self.device.get_env(),
                self.device.get_build_env(build),
                test.get_env(),
                {
                    "SCREENSHOT_PATH": tmp_out + '/'  # has to end with '/'
                }
        )

        # show commands
        print '--------------------------------------------------------------------------'
        print '| Commands: '
        print '|'
        print '|', ' '.join(cmd)
        print '|'
        print '| NOTE: output files will be moved to:', real_out
        print '|'
        print '--------------------------------------------------------------------------'

        # run command
        self.call(cmd, env)

        # move files if necessary
        if tmp != test.output_dir:
            shutil.move(tmp_out, real_out)

        self.latest_report_dir = self.get_current_report_dir(parent=test.output_dir, timestamp=timestamp)

    def get_reports_dir(self, parent):
        dir = path.join(parent, 'reports/')
        if not path.exists(dir):
            makedirs(dir)
        return path.abspath(dir)

    def get_device_reports_dir(self, parent):
        dir = path.join(self.get_reports_dir(parent), '%s-%s/' % (self.device.os, self.device.name))
        if not path.exists(dir):
            makedirs(dir)
        return path.abspath(dir)

    def get_current_report_dir(self, parent, timestamp):
        dir = path.join(self.get_device_reports_dir(parent), timestamp)
        if not path.exists(dir):
            makedirs(dir)
        return dir


################################
# Version Command Builder
################################
class VersionCmdBuilder(object):
    MIN_PREFIX = '-min-v'
    MAX_PREFIX = '-max-v'

    @classmethod
    def build_cmd(cls, device, build, version_names_getter):
        if not build.version:
            return []

        sorted_versions = sorted(version_names_getter())
        index = sorted_versions.index(build.version)
        before = sorted_versions[:index]
        after = sorted_versions[index + 1:]

        # use negation via '~' in order to support tests without min/max tags
        min_cmd = ['~@' + device.get_os() + cls.MIN_PREFIX + tag for tag in after]
        max_cmd = ['~@' + device.get_os() + cls.MAX_PREFIX + tag for tag in before]

        cmd = []
        for tag in min_cmd + max_cmd:
            cmd += ['--tags', tag]

        return cmd


################################
# Test Command Builder
################################
class TestCmdBuilder(object):
    @classmethod
    def build_cmd(cls, test, output_dir_path, report):
        command = test.run.split(' ')

        if report:
            report_file = path.join(output_dir_path, 'report.html')
            command.append('--format')
            command.append('html')
            command.append('--out')
            command.append(report_file)
            command.append('--format')
            command.append('pretty')

        return command
