from processy import run, CompletedProcess
from cmdinter import CmdFuncResult, Status
from typing import Optional
from buildlib.cmds.git import prompt


def add_all() -> CmdFuncResult:
    """"""
    title = 'Git Add All.'

    p: CompletedProcess = run(cmd=['git', 'add', '--all'])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )


def commit(
    msg: str
) -> CmdFuncResult:
    """"""
    title = 'Git Commit.'

    p: CompletedProcess = run(cmd=['git', 'commit', '-m', msg])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )


def tag(
    version: str,
    branch: str,
) -> CmdFuncResult:
    """"""
    title = 'Git Tag.'

    p: CompletedProcess = run(cmd=['git', 'tag', version, branch])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )


def push(branch: str) -> CmdFuncResult:
    """"""
    title = 'Git Push.'

    p: CompletedProcess = run(cmd=['git', 'push', 'origin', branch, '--tags'])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )


def get_default_branch() -> CmdFuncResult:
    """"""
    title = 'Get Default Branch.'

    branch: Optional[str] = None
    returncode: int = 0

    p1 = run(
        cmd=['git', 'show-branch', '--list'],
        return_stdout=True
    )

    if p1.stdout.find('No revs') == -1 and p1.returncode == 0:
        p2 = run(
            cmd=['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            return_stdout=True
        )

        branch: str = p2.stdout.replace('\n', '')
        returncode: int = p2.returncode

    if returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=returncode,
        summary=status + title,
        returnvalue=branch,
    )


def status() -> CmdFuncResult:
    """"""
    title = 'Git Status.'

    p: CompletedProcess = run(cmd=['git', 'status'])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )


def diff() -> CmdFuncResult:
    """"""
    title = 'Git Diff.'

    p: CompletedProcess = run(cmd=['git', 'diff'])

    if p.returncode == 0:
        status: str = Status.ok

    else:
        status: str = Status.error

    return CmdFuncResult(
        returncode=p.returncode,
        summary=status + title,
        returnvalue=None
    )
