"""module with wrappers for dyntools

"""
import os
import sys

if sys.version_info[0] < 3:
    if os.name == 'posix' :
        from subprocess32 import Popen, PIPE, TimeoutExpired
    else:
        from subprocess import Popen, PIPE
        TimeoutExpired = Exception
else:
    from subprocess import Popen, PIPE, TimeoutExpired



class LagrantoException(RuntimeError):
    """Raise this when a lagranto call fails"""


def run_cmd(cmd, workingdir='.', netcdf_format='CF', cmd_header=None,
            prefix=''):
    """Run cmd in a shell with particular environment

     Run shell commands while pre-appending a `cmd_header`.
     The default `cmd_header` is :

     .. code-block:: bash

        . /etc/profile.d/modules.sh
        module purge
        module load dyn_tools
        export NETCDF_FORMAT={netcdf_format}

    where `netcdf_format` is by default set to CF.

    Parameters
    ----------
    cmd: string,
        command to run in a shell
    workingdir:
        directory where the command should be run
    netcdf_format: string
        format of netcdf to use (CF or IVE);
        (historical reason, ETH Zurich)
    cmd_header: string
        string to run before the `cmd`;
        see the description for more details
    prefix: string
        string to pre-append to the cmd

    Returns
    -------
    string
        the output of the command in the shell (stdout stream)

    """
    script = """
    cd '{workingdir}'
    {prefix} {cmd}
    """
    if cmd_header is None:
        script = """ . /etc/profile.d/modules.sh
        module purge
        module load dyn_tools
        export NETCDF_FORMAT={netcdf_format}
        """ + script
    else:
        script = cmd_header + script

    script = script.format(workingdir=workingdir, cmd=cmd,
                           netcdf_format=netcdf_format, prefix=prefix)
    p = Popen('bash', stdout=PIPE, stderr=PIPE, stdin=PIPE,
              universal_newlines=True)
    try:
        output, error = p.communicate(input=script)
    except TimeoutExpired:
        p.kill()
        output, error = p.communicate()
    if error or ('ERROR' in output) or ('Error' in output)\
            or ('Cannot' in output) or ('Problem' in output):
        # noinspection PyTypeChecker
        raise LagrantoException(script + output + error)
    return output
