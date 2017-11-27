import subprocess
import re
import os

import autest.api as api
import autest.common.ospath as ospath
import autest.common.version as verlib
import autest.common.is_a as is_a
import autest.common.win32 as win32

import pip

import hosts.output as host


def HasPythonPackage(self, package, msg):
    def checkPackage():
        for pkg in pip.get_installed_distributions():
            if package == pkg.project_name:
                return True

        return False

    return self.Condition(
        checkPackage,
        msg,
        True
    )


def IsElevated(self, msg, pass_value=0):    # default pass value of 0 == os.geteuid (which for root is 0)
    if os.name == 'nt':
        return self.Condition(
            lambda: win32.user_is_admin(),
            msg,
            pass_value
        )
    elif os.name == 'posix':
        return self.Condition(
            lambda: os.geteuid(),
            msg,
            pass_value
        )
    else:
        raise OSError("OS not identified. Can't check for elevated privilege.")


def RunCommand(self, command, msg, pass_value=0, env=None, shell=False):
    return self.Condition(
        lambda: subprocess.call(command, shell=shell),
        msg,
        pass_value
    )


def CheckOutput(self, command, check_func, msg, pass_value=True, neg_msg=None, shell=False):
    def check_logic():
        try:
            output = subprocess.check_output(
                command, universal_newlines=True,
                stderr=subprocess.STDOUT,
                shell=shell
            )
        except subprocess.CalledProcessError:
            return False
        return check_func(output)

    return self.Condition(
        check_logic,
        msg,
        pass_value,
        neg_msg
    )


def EnsureVersion(self, command, min_version=None, max_version=None, msg=None, output_parser=None, shell=False):

    has_min = False
    has_max = False

    if min_version:
        has_min = True
    else:
        min_version = "*"

    if max_version:
        has_max = True
    else:
        max_version = "*"

    if not has_min and not has_max:
        host.WriteError(
            "Invalid arguments - min_version or max_version must be set", stack=host.getCurrentStack(1)
        )

    def default(output):
        '''
        reg-expression to get version
        '''
        out = re.search(r'(?P<ver>\d+\.\d+(?:\.\d+)*)', output, re.MULTILINE)
        if out:
            return out.groupdict()['ver']
        return None

    # set output parser
    if not output_parser:
        output_parser = default

    def version_check(output):

        # turn our version to an version object
        ver_rng = verlib.VersionRange(
            "[{min}-{max}]".format(min=min_version, max=max_version))
        # call parser to get version value
        ver = output_parser(output)
        # check that it is not None and it matches the range
        if ver and ver in ver_rng:
            return True
        return False

    if not msg:
        msg = "{command} needs to be"
        if has_min and min_version != "*":
            msg += " >= to version: {min_version}"
        if has_min and has_max:
            msg += " and"
        if has_max and max_version != "*":
            msg += " <= version {max_version}"

    if is_a.List(command):
        cmd = command[0]
    else:
        cmd = command.split()[0]

    return self.CheckOutput(
        command,
        version_check,
        msg.format(command=cmd, min_version=min_version,
                   max_version=max_version),
        shell=False
    )


def HasProgram(self, program, msg, pass_value=True, path=None):
    return self.Condition(lambda: ospath.has_program(program, path), msg, pass_value)


api.ExtendCondition(RunCommand)
api.ExtendCondition(CheckOutput)
api.ExtendCondition(EnsureVersion)
api.ExtendCondition(HasProgram)
api.ExtendCondition(IsElevated)
api.ExtendCondition(HasPythonPackage)
