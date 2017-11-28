import os
import sys
import subprocess


def main():
    is_should_be_deployed()


def is_should_be_deployed() -> bool:
    os.chdir(os.environ['CI_PROJECT_DIR'])
    last_commit_message = subprocess.check_output(
        ['git', 'log', '-1', '--oneline'],
        universal_newlines=True,
    )
    is_tagged_commit = 'Added tag' in last_commit_message
    if is_tagged_commit:
        print('This build should be deployed.')
        return True
    else:
        sys.exit('This build should not be deployed. Exiting the CI process.')


if __name__ == '__main__':
    main()
