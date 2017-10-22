
import requests
import os
from subprocess import call, check_call, CalledProcessError
import sys
import argparse
import shutil

error = "\033[1;31m ERROR \033[0m"
done = "\033[40;38;5;82m DONE \033[0m"


class BitbucketUtils:

    def __init__(self):
        self.verify_user()
        self.get_uuid()

    def get_uuid(self):
        resp = requests.get(
            'https://api.bitbucket.org/2.0/users/{}'.format(
                self.bit_user),
            auth=(self.bit_user, self.bit_pass),
            data={"scm": "git", "is_private": "true",
                  "fork_policy": "no_public_forks"}
        )
        if resp.status_code != 200:
            print("{}: {}".format(error, resp.json()['error']['message']))
            sys.exit()

        self.uuid = resp.json()['uuid']

    def verify_user(self):
        self.bit_user = os.environ['BITBUCKET_NAME']
        self.bit_pass = os.environ['BITBUCKET_PASS']
        if not (self.bit_user or self.bit_pass):
            print(
                """
                Missing BITBUCKET_NAME or BITBUCKET_PASS
                Pleas assign bitbucket username and bitbucket password to
                enviroment variables
                """
            )
            sys.exit(1)

    @staticmethod
    def query_yes_no(question, default="no"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:

            choice = input(question + prompt).lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    def delete_repo(self):

        self.repo_name = input(
            "Repo name:(Default will use the current folder name) ")

        if not self.repo_name:
            self.repo_name = os.path.basename(os.getcwd())

        if not self.repo_name:
            sys.exit("{} Repo name cannot be empty.. ".format(error))

        resp = requests.get(
            "https://api.bitbucket.org/2.0/repositories/{}/{}".format(
                self.uuid, self.repo_name), auth=(self.bit_user, self.bit_pass))

        if resp.status_code != 200:
            print("{}: {}".format(error, resp.json()['error']['message']))
            sys.exit()

        if not BitbucketUtils.query_yes_no("\033[1;31m Are you sure? This cannot be undone. \033[0m"):
            print("Canceled..")
            sys.exit()

        # folder has to contains .git
        if not os.path.exists('.git'):
            sys.exit("{} This project has not been initialized".format(error))

        # remove request to bitbucket
        resp = requests.delete("https://api.bitbucket.org/2.0/repositories/{}/{}".format(
            self.uuid, self.repo_name), auth=(self.bit_user, self.bit_pass))

        # 204 means successfully deleted
        if resp.status_code != 204:
            print("{}: {}".format(error, resp.json()['error']['message']))
            sys.exit()

        shutil.rmtree('.git')

        print("{} Deleted {} in Bitbucket".format(done, self.repo_name))

    def create_repo(self,  private=True):
        """
            git init, create repo and push the code to that repo.abs()
        """

        # get app name they want to create in bitbucket
        self.app_name = input(
            "App name:(Default will use the current folder name) ")
        if not self.app_name:
            self.app_name = os.path.basename(os.getcwd())

        print("Repo name = {}".format(self.app_name))

        # if .git already exists then exit out
        if os.path.exists('.git'):
            sys.exit("This folder has already been git initialized.")

        # try/except to exits out if user has not git command.
        try:
            check_call(['git', 'init'])
            print('initialzing git...')
            check_call(['git', 'add', '-A'])
            check_call(['git', 'commit', '-m', '"Initial Commit"'])
        except CalledProcessError as err:
            print("{} error occurs : {}".format(error, err.output))
            sys.exit()

        # post a request to create a repo
        private_str = "true" if private else "false"
        private_fork = "no_public_forks" if private else "allow_forks"
        resp = requests.post(
            'https://api.bitbucket.org/2.0/repositories/{}/{}'.format(
                self.uuid, self.app_name),
            auth=(self.bit_user, self.bit_pass),
            data={"scm": "git", "is_private": private_str,
                  "fork_policy": private_fork}
        )

        if resp.status_code != 200:
            print("{}: {}".format(error, resp.json()['error']['message']))
            sys.exit()

        # get remote address
        url = resp.json()['links']['clone'][1]['href']

        # git add remotr and push the code
        try:
            check_call(['ssh-add', '/Users/bealox/.ssh/bealox_Bitbucket'])
            check_call(['git', 'remote', 'add', 'origin', url])
            check_call(['git', 'push', '-u', 'origin', 'master'])
        except CalledProcessError as err:
            print("{} Commandline error : {}".format(error, err.output))
            sys.exit()

        print("{} Created {} in Bitbucket".format(done, self.app_name))


b_utils = BitbucketUtils()


def create_repo(args):
    b_utils.create_repo(args.private)


def delete_repo(args):
    b_utils.delete_repo()


# run
def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    parser_foo = subparsers.add_parser(
        'create', help="create a repo in Bitbucket")
    parser_foo.add_argument('-p', '--private', type=bool, default=True,
                            help="set to private, default is true")
    parser_foo.set_defaults(func=create_repo)

    parser_foo = subparsers.add_parser(
        'delete', help="delete a repo in Bitbucket")
    parser_foo.set_defaults(func=delete_repo)

    args = parser.parse_args()
    if len(vars(args)) > 0:
        args.func(args)
    else:
        parser.print_help()
