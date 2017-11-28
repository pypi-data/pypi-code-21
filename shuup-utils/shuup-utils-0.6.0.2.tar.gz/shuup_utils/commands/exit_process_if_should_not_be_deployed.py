import os
import sys
import subprocess


def main():
    last_commit_message = _get_git_last_commit_message()
    is_not_tagged_commit = 'add tag' not in last_commit_message
    if is_not_tagged_commit:
        sys.exit('This build should not be deployed. Exiting the CI process.')


def _get_git_last_commit_message() -> str:
    os.chdir(os.environ['CI_PROJECT_DIR'])
    msg_raw = subprocess.check_output(
        ['git', 'log', '-1', '--oneline'],
        universal_newlines=True,
    )
    return str(msg_raw)


if __name__ == '__main__':
    main()
