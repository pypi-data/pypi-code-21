from typing import Optional, List
from buildlib.cmds import git
from cmdinter import CmdFuncResult


class GitSequenceSettings(dict):
    version: str
    should_bump_any: Optional[bool]
    should_add_all: Optional[bool]
    should_commit: Optional[bool]
    commit_msg: Optional[str]
    should_tag: Optional[bool]
    should_push_git: Optional[bool]
    branch: Optional[str]


def get_sequence_settings_from_user(
    version: str,
    should_tag_default: Optional[bool] = None,
    should_bump_any: Optional[bool] = None,
) -> GitSequenceSettings:
    """
    @should_tag_default: If True: tag default will be 'y' if False: 'n'
    @should_bump_any: If True, user will be asked if she wants to run any git
    at all
    """
    s = GitSequenceSettings()
    s.version = version

    s.should_bump_any = should_bump_any or git.prompt.should_run_any(
        default='y'
    )

    if s.should_bump_any is not False:
        # Ask user to run any git commands.
        s.should_bump_any: bool = git.prompt.confirm_status('y') \
                                  and git.prompt.confirm_diff('y')

    # Git routine
    if s.should_bump_any:
        # Ask user to run 'git add -A.
        s.should_add_all: bool = git.prompt.should_add_all(
            default='y'
        )

        # Ask user to run commit.
        s.should_commit: bool = git.prompt.should_commit(
            default='y'
        )

        # Get commit msg from user.
        if s.should_commit:
            s.commit_msg: str = git.prompt.commit_msg()

        # Ask user to run 'tag'.
        s.should_tag: bool = git.prompt.should_tag(
            default='n' if should_tag_default is False else 'y'
        )

        # Ask user to push.
        s.should_push_git: bool = git.prompt.should_push(
            default='y'
        )

        # Ask user for branch.
        if any([
            s.should_tag,
            s.should_push_git
        ]):
            s.branch: str = git.prompt.branch()

    return s


def bump_sequence(
    s: GitSequenceSettings
) -> List[CmdFuncResult]:
    """"""
    results = []

    # If any git commands should be run.
    if s.should_bump_any:
        # Run 'add -A'
        if s.should_add_all:
            results.append(
                git.add_all()
            )

        # Run 'commit -m'
        if s.should_commit:
            results.append(
                git.commit(s.commit_msg)
            )

        # Run 'tag'
        if s.should_tag:
            results.append(
                git.tag(s.version, s.branch)
            )

        # Run 'push'
        if s.should_push_git:
            results.append(
                git.push(s.branch)
            )

    return results
