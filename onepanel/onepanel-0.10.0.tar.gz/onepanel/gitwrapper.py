""" Command line interface for the OnePanel Machine Learning platform

Wrap git commands and provide transparent integration onepanel commands with the git.
"""

import os
import subprocess


class GitWrapper:
    def __init__(self):
        self.HOST = 'git.onepanel.io'

    def get_credential_helper(self):
        """ Retrieve current git credential manager and use it for storing usernames and passwords
        """
        git_cmd = 'git config credential.helper'
        p = subprocess.Popen(git_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p.wait()

        line = p.stdout.readline()
        credential_helper = line.decode().rstrip()
        return credential_helper

    def save_credentials(self, username, password):
        """ Store password in the current git credential storage
        """

        credential_helper = self.get_credential_helper()
        if not credential_helper:
            print('ERROR. Cannot store git username/password.\n')
            print('Git credential helper is not configured')
            return

        # we can call helper by absolute path or from git command
        if not os.path.isabs(credential_helper):
            git_cmd = 'git credential-{} store'.format(credential_helper)
        else:
            git_cmd = credential_helper

        p = subprocess.Popen(git_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        p.stdin.write('protocol=https\n'.encode())
        p.stdin.write('host={}\n'.format(self.HOST).encode())
        p.stdin.write('username={}\n'.format(username).encode())
        p.stdin.write('password={}\n'.format(password).encode())
        p.stdin.close()
        p.wait()

    def init(self, home, account_uid, project_uid):
        git_cmd = 'git init'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

        git_cmd = 'git remote add onepanel https://{}/{}/{}.git'.format(self.HOST, account_uid, project_uid)
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

    def clone(self, home, account_uid, project_uid):
        git_cmd = 'git clone -o onepanel https://{}/{}/{}.git {}'.format(self.HOST, account_uid, project_uid, home)
        p = subprocess.Popen(git_cmd, shell=True)
        p.wait()

        return p.returncode

    def exclude(self, home, files):
        exclude_file = os.path.join(home, '.git/info/exclude')
        with open(exclude_file,'a+') as f:
            for file in files:
                f.write(file + '\n')

    def push(self, home):
        git_cmd = 'git push -u onepanel master'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()

    def pull(self, home):
        git_cmd = 'git pull'
        p = subprocess.Popen(git_cmd, cwd=home, shell=True)
        p.wait()
