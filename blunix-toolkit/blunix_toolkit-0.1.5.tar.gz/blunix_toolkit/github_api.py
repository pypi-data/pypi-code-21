import sys
import ssl

from github import Github

from blunix_toolkit import config

C = config.get()

user = C['github']['user']
pw = C['github']['pass']
org = C['github']['org']
g = Github(user, pw)
user = g.get_user()


def get_repos():
    while True:
        try:
            return user.get_repos()
        except (Exception, ):
            sys.stderr.write("Retrying...\n")
            sys.stderr.flush()


def get_repo_full_name(repo):
    while True:
        try:
            return repo.full_name
        except (Exception, ):
            sys.stderr.write("Retrying...\n")
            sys.stderr.flush()
