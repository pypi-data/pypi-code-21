#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import FlushError
import delegator
import git
from .models import engine, Repo
from multiprocessing import Process, Queue
from .lolcat import LolCat
import random


class GitManager(object):
    def __init__(self):
        self.db = sessionmaker(bind=engine)()
        self.longest_name = max([0] + [len(repos.name) for repos in self.repos])

    @property
    def repos(self):
        return self.db.query(Repo)

    @property
    def num_repos(self):
        return self.repos.count()

    @staticmethod
    def _get_name(repo_path):
        return os.path.basename(os.path.normpath(repo_path)).upper()

    @staticmethod
    def _get_path(directory):
        return os.path.realpath(os.path.join(os.getcwd(), directory))

    @classmethod
    def _get_path_and_name(cls, p):
        path = cls._get_path(p)
        return path, cls._get_name(path)

    @staticmethod
    def _get_branch(repo_path):
        r = git.Repo(repo_path)
        try:
            branch = r.active_branch.name
        except ValueError:
            branch = 'unknown'

        diffs = len(r.index.diff(None))
        return branch, diffs

    @staticmethod
    def _pull_repo(repo_path):
        return delegator.run('git -C {0} pull'.format(repo_path), block=False)

    @staticmethod
    def _list_branches(repo_path):
        return delegator.run('git -C {0} branch'.format(repo_path), block=False)

    @staticmethod
    def _checkout_branch(repo_path, branch='master'):
        return delegator.run('git -C {0} checkout {1}'.format(repo_path, branch), block=False)

    @staticmethod
    def _get_results(output_queue, num_repos):
        results = []
        while True:
            string = output_queue.get()
            results.append(string)
            if len(results) == num_repos:
                break
        return sorted(results)

    @staticmethod
    def _print(s):
        l = LolCat()

        class Options:
            freq = 0.1
            spread = 3.0
            animate = False
            seed = 0
            duration = 12
            speed = 20
            force = False
            os = random.randint(0, 256)
            charset_py2 = 'utf-8'

        l.cat(s, Options)

    def _get_repo(self, repo_path):
        return self.repos.filter(Repo.path == repo_path)

    def _add_repo(self, repo_path, name):
        repo = Repo(name=name, path=repo_path)
        self.db.add(repo)
        try:
            self.db.commit()
            self._longest_name = 0
            return True
        except FlushError:
            self.db.rollback()
            return False

    def _delete_repo(self, repo_path):
        result = self._get_repo(repo_path).delete()
        self.db.commit()
        self._longest_name = 0
        return result

    def _format_branch(self, repo, output_queue):
        branch, diffs = self._get_branch(repo.path)
        text = '{name}{branch}{status}'.format(name=repo.name.ljust(self.longest_name + 10),
                                               branch=branch.ljust(20),
                                               status='⦿' * diffs)
        output_queue.put(text)

    def _call_function(self, f, *args, **kwargs):
        processes = [(f(repo.path, *args, **kwargs), repo.name) for repo in self.repos]
        output = []
        for index, (p, name) in enumerate(processes):
            p.block()
            output.append(name)
            output.append(p.out)
            output.append('')
        self._print(output)

    def register(self, directory):
        repo_path, name = self._get_path_and_name(directory)

        if not os.path.exists(os.path.join(directory, '.git')):
            self._print(['{repo_path} is not a git repository!'.format(repo_path=repo_path)])
            return

        if self._add_repo(repo_path, name):
            self._print(['Added {name} ({repo_path}) to Git Manager'.format(name=name, repo_path=repo_path)])
        else:
            self._print([('{name} ({repo_path}) has not been added '
                          'because it is already registered!').format(name=name, repo_path=repo_path)])

    def deregister(self, directory):
        repo_path, name = self._get_path_and_name(directory)

        if self._delete_repo(repo_path):
            self._print(['Removed {name} ({repo_path}) from Git Manager'.format(name=name, repo_path=repo_path)])
        else:
            self._print([('{name} ({repo_path}) has not been removed '
                          'because it is not registered!').format(name=name, repo_path=repo_path)])

    def status_check(self):
        num_repos = self.num_repos
        output_queue = Queue()

        processes = [Process(target=self._format_branch, kwargs=dict(repo=repo, output_queue=output_queue))
                     for repo in self.repos]

        for process in processes:
            process.start()
        for process in processes:
            process.join()

        self._print(self._get_results(output_queue, num_repos))

    def pull_all(self):
        self._call_function(self._pull_repo)

    def list_branches(self):
        self._call_function(self._list_branches)

    def checkout_master(self):
        self._call_function(self._checkout_branch, branch='master')
