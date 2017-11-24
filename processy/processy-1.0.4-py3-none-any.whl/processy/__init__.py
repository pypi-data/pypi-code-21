import sys
import shlex
from typing import Union
import subprocess as sp
from subprocess import CompletedProcess


def _print_and_return_lines_from_popen(p: sp.Popen) -> str:
    out: str = ''
    for c in iter(lambda: p.stdout.readline(1), ''):
        sys.stdout.write(c)
        out += c
    return out


def _return_lines_from_popen(p: sp.Popen) -> str:
    out: str = ''
    for c in iter(lambda: p.stdout.readline(1), ''):
        out += c
    return out


def _print_lines_from_popen(p: sp.Popen) -> None:
    for c in iter(lambda: p.stdout.readline(1), ''):
        sys.stdout.write(c)


def run(
    cmd: Union[list, str],
    verbose: bool = True,
    return_stdout: bool = False,
    raise_err: bool = False,
    **popen_kwargs
) -> CompletedProcess:
    """
    @cmd: The Popen command. If it's a string shlex is used to split it.
    @verbose: Print the output to stdout if True. If False call runs quite.
    @return_stdout: Returns the output from stdout.
    @raise_error: If subprocess return code is not 0.
    """
    out = None
    error = None

    default_kwargs = {
        'universal_newlines': True
    }

    if return_stdout:
        default_kwargs.update({'stdout': sp.PIPE, 'stderr': sp.PIPE})

    elif not return_stdout and not verbose:
        default_kwargs.update({'stdout': sp.DEVNULL})

    if type(cmd) is str:
        cmd = shlex.split(cmd)

    p: sp.Popen = sp.Popen(cmd, **default_kwargs, **popen_kwargs)

    if return_stdout and verbose:
        out = _print_and_return_lines_from_popen(p)
        error = p.communicate()[1]

    elif return_stdout and not verbose:
        out, error = p.communicate()

    elif not return_stdout and verbose:
        error = p.communicate()[1]

    elif not return_stdout and not verbose:
        error = p.communicate()[1]

    returncode: int = p.wait()

    if raise_err and returncode is not 0:
        raise sp.CalledProcessError

    return CompletedProcess(
        args=cmd,
        returncode=returncode,
        stdout=out,
        stderr=str(error),
    )
