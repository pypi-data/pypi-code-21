#!/usr/bin/env python

from util import Color, exit_error, get
from device_os import OS
import os


################################
# Device Manager
################################
class DeviceManager(object):
    def __init__(self, conf, os_list):
        if not conf:
            conf = {}

        self.devices = {}
        for os in os_list:
            self.load_devices(conf, os=os)

    # private
    def load_devices(self, conf, os):
        for name, info in conf.get(os, {}).iteritems():
            if os == OS.Android:
                id = get(info, 'id', None)
                port = get(info, 'port', None)
                if id and not port:
                    exit_error("Device '%s' is missing parameter 'port' (it is required if 'id' is specified)" % name)

                self.devices[name] = AndroidDevice(name, id, port)
            elif os == OS.iOS:
                # change uuid to id (to ensure compatibility with older versions)
                if 'uuid' in info:
                    info['id'] = info['uuid']
                    del info['uuid']

                self.validate_device(name, info, 'id')
                self.validate_device(name, info, 'ip')

                self.devices[name] = IosDevice(name, info['id'], info['ip'])

    # private
    def validate_device(self, name, params, param_name):
        if param_name not in params.keys():
            exit_error("Device '%s' is missing parameter '%s'" % (name, param_name))

    # public
    def get_device(self, name):
        device = self.devices.get(name, None)
        if device:
            return device
        else:
            exit_error("Device '%s' was not found" % name)


################################
# Base Device
################################
class BaseDevice(object):
    DEVICE_NAME = 'CAPY_DEVICE_NAME'

    def __init__(self, os, name, env={}):
        self.os = os
        self.name = name
        self.env = env
        self.env[self.DEVICE_NAME] = name

    def get_os(self):
        return self.os

    def get_env(self):
        return self.env

    def get_cli_tools(self):
        return []  # implement

    def get_install_cmds(self, build):
        return []  # implement

    def get_uninstall_cmds(self, build):
        return []  # implement

    def get_console_cmd(self, build):
        return []  # implement

    def get_run_cmd(self, build):
        return []  # implement

    def get_build_env(self, build):
        return {}  # implement

    def show(self, line_start=''):
        return line_start + Color.LIGHT_GREEN + '%s ' % self.name + Color.YELLOW + '(%s)' % self.os + Color.ENDC


################################
# iOS Device
################################
class IosDevice(BaseDevice):
    CLI_TOOL = 'ideviceinstaller'
    ID_ENV_NAME = 'DEVICE_TARGET'
    IP_ENV_NAME = 'DEVICE_ENDPOINT'

    def __init__(self, name, id, ip):
        env = {
            self.ID_ENV_NAME: id,
            self.IP_ENV_NAME: 'http://%s:37265' % ip
        }
        super(IosDevice, self).__init__(OS.iOS, name, env)

    def get_console_cmd(self, build):
        return ['bundle', 'exec', 'calabash-ios', 'console', '-p', 'ios']

    def get_run_cmd(self, build):
        return ['bundle', 'exec', 'cucumber', '-p', 'ios']

    def get_build_env(self, build):
        return {
            "BUNDLE_ID": build.app_id,
            "CODE_SIGN_IDENTITY": build.csid
        }

    def get_cli_tools(self):
        return [self.CLI_TOOL]

    def get_install_cmds(self, build):
        return [
            [self.CLI_TOOL, '-u', self.env[self.ID_ENV_NAME], '-i', build.get_path()]
        ]

    def get_uninstall_cmds(self, build):
        cmds = [
            [self.CLI_TOOL, '-u', self.env[self.ID_ENV_NAME], '-U', build.app_id]
        ]
        if build.csid:
            cmds.append([self.CLI_TOOL, '-u', self.env[self.ID_ENV_NAME], '-U', 'com.apple.test.DeviceAgent-Runner'])

        return cmds

    def show(self, line_start=''):
        s = super(IosDevice, self).show(line_start=line_start)
        s += '\n' + line_start + Color.YELLOW
        s += '  - ID: ' + Color.ENDC + '%s' % self.env[self.ID_ENV_NAME]
        s += Color.ENDC
        s += '\n' + line_start + Color.YELLOW
        s += '  - IP: ' + Color.ENDC + '%s' % self.env[self.IP_ENV_NAME]
        s += Color.ENDC
        return s


################################
# Android Device
################################
class AndroidDevice(BaseDevice):
    CLI_TOOL = 'adb'
    ID_ENV_NAME = 'ADB_DEVICE_ARG'
    PORT_ENV_NAME = 'TEST_SERVER_PORT'

    def __init__(self, name, id=None, port=None):
        env = {}
        if id:
            env[self.ID_ENV_NAME] = str(id)
        if port:
            env[self.PORT_ENV_NAME] = str(port)  # make sure it's a string
        super(AndroidDevice, self).__init__(OS.Android, name, env)

    def get_console_cmd(self, build):
        return ['bundle', 'exec', 'calabash-android', 'console', build.get_path(), '-p', 'android']

    def get_run_cmd(self, build):
        return ['bundle', 'exec', 'calabash-android', 'run', build.get_path(), '-p', 'android']

    def get_cli_tools(self):
        return [self.CLI_TOOL]

    def get_install_cmds(self, build):
        cmds = []

        # rebuild test-server
        cmds.append(['bundle', 'exec', 'calabash-android', 'build', build.get_path()])

        # install app
        install_cmd = [self.CLI_TOOL]
        if self.PORT_ENV_NAME in self.env:
            install_cmd.append('-s')
            install_cmd.append(self.env[self.ID_ENV_NAME])
        install_cmd.append('install')

        android_version = self._get_device_android_version()
        if android_version < 23:
            install_cmd.append('-r')
        else:
            # since 6.0 (API 23) you need '-g' in order to grant runtime permissions
            install_cmd.append('-g')
            install_cmd.append('-r')

        install_cmd.append(build.get_path())
        cmds.append(install_cmd)

        return cmds

    def _get_device_android_version(self):
        if self.PORT_ENV_NAME in self.env:
            cmd = "{a} -s {n} shell getprop ro.build.version.sdk".format(a=self.CLI_TOOL, n=self.env[self.ID_ENV_NAME])
        else:
            cmd = "{a} shell getprop ro.build.version.sdk".format(a=self.CLI_TOOL)

        version_str = os.popen(cmd).read()
        return int(version_str)

    def get_uninstall_cmds(self, build):
        if self.PORT_ENV_NAME in self.env:
            return [
                [self.CLI_TOOL, '-s', self.env[self.ID_ENV_NAME], 'uninstall', build.app_id]
            ]
        else:
            return [
                [self.CLI_TOOL, 'uninstall', build.app_id]
            ]

    def show(self, line_start=''):
        s = super(AndroidDevice, self).show(line_start=line_start)
        if self.ID_ENV_NAME in self.env:
            s += '\n' + line_start + Color.YELLOW
            s += '  - ID: ' + Color.ENDC + '%s' % self.env[self.ID_ENV_NAME]
            s += Color.ENDC
        if self.PORT_ENV_NAME in self.env:
            s += '\n' + line_start + Color.YELLOW
            s += '  - PORT: ' + Color.ENDC + '%s' % self.env[self.PORT_ENV_NAME]
            s += Color.ENDC
        return s
