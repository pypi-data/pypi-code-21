import prmt
from headlines import h3
from buildlib.cmds import git
from cmdinter import run_cmd


def commit_msg(
    margin: tuple = (0, 1),
    editor: bool = True
) -> str:
    return prmt.string(
        question='Enter COMMIT message:\n',
        margin=margin,
        force_val=True,
        editor=editor
    )


def branch(
    margin: tuple = (0, 1)
) -> str:
    return prmt.string(
        question='Enter BRANCH name:\n',
        default=run_cmd(silent=True)(git.get_default_branch).returnvalue,
        margin=margin
    )


def confirm_status(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    print(h3('Git Status'))
    git.status()

    return prmt.confirm(
        question='GIT STATUS ok?\n',
        default=default,
        margin=margin
    )


def confirm_diff(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    print(h3('Git Diff'))
    git.diff()

    return prmt.confirm(
        question='GIT DIFF ok?\n',
        default=default,
        margin=margin,
    )


def should_run_any(
    default: str = '',
    margin: tuple = (1, 0)
) -> bool:
    """"""
    return prmt.confirm(
        question='Run ANY GIT COMMANDS?\n',
        default=default,
        margin=margin,
    )


def should_add_all(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Run GIT ADD ALL ("git add --all")?\n',
        default=default,
        margin=margin
    )


def should_commit(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Run GIT COMMIT?\n',
        default=default,
        margin=margin
    )


def should_tag(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='Run GIT TAG?\n',
        default=default,
        margin=margin
    )


def should_push(
    default: str = '',
    margin: tuple = (1, 1),
) -> bool:
    """"""
    return prmt.confirm(
        question='GIT PUSH to GITHUB?\n',
        default=default,
        margin=margin
    )
