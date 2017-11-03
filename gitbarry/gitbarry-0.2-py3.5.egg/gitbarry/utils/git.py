import os
import sys
import sh


def assert_is_git_repo():
    try:
        assert os.path.isdir('.git')
        assert os.path.isfile('.git/HEAD')
    except AssertionError:
        print("This is not git repository")
        sys.exit(2)


def get_current_branch() -> str:
    current_branch = sh.git('rev-parse', '--abbrev-ref', 'HEAD')
    print(current_branch)
    return current_branch.strip()


def get_local_branches() -> list:
    branches = []
    branches_raw = sh.git("for-each-ref", "--format='%(refname)'", "refs/heads/")
    for branch_name_long in branches_raw.split('\n'):
        if branch_name_long:
            branches.append(branch_name_long.replace('refs/heads/', '').replace("'", ""))
    return branches


def ensure_branch_not_exists(branch_name: str):
    if branch_name in get_local_branches():
        print("branch %s already exists!" % branch_name)
        sys.exit(4)


def ensure_branch_exists(branch_name):
    if branch_name not in get_local_branches():
        print("branch %s not exists!" % branch_name)
        sys.exit(4)


def create_new_branch(branch_name: str, push_to_origin=True):
    ensure_branch_not_exists(branch_name)
    print("Creating new branch %s" % branch_name)
    sh.git("checkout", '-b', branch_name)
    if push_to_origin:
        sh.git("push", "-u", "origin", branch_name)
        print("Local branch pushed to origin")


def swith_to_branch(branch_name: str):
    print("Switching to %s" % branch_name)
    ensure_branch_exists(branch_name)
    sh.git('checkout', branch_name)
    try:
        assert get_current_branch() == branch_name
    except:
        print("Cant checkout branch. %s not %s" % (get_current_branch(), branch_name))


def merge(from_branch):
    print("Fetching changes from %s" % from_branch)
    ensure_branch_exists(from_branch)
    output = sh.git("merge", from_branch)
    print(output)


def delete_branch(branch_name):
    ensure_branch_exists(branch_name)
    output = sh.git("branch", '-D', branch_name)
    print(output)
