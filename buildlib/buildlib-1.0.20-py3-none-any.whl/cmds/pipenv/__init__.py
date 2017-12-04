from processy import run, CompletedProcess
from cmdinter import CmdFuncResult, Status


def install(
    dev: bool = False
) -> CmdFuncResult:
    """
    Install packages from Pipfile.
    """
    title = 'Install Dev Packages.'

    dev_flag = ['--dev'] if dev else []
    p: CompletedProcess = run(['pipenv', 'install'] + dev_flag)

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )


def create_env(
    version: str
) -> CmdFuncResult:
    """
    Create a fresh python environment.
    @version: E.g.: '3.6'
    """
    title = 'Install Dev Packages.'
    p: CompletedProcess = run(['pipenv', f'--python {version}'])

    if p.returncode == 0:
        status: str = Status.ok
    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        returnvalue=None,
        summary=f'{status} {title}',
    )
