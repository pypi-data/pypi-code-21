import os
import re
import github
import github.GithubObject
import json
import yaz

from .version import __version__
from .spreadsheet import VersionMatrixSheet
from .github import Github
from .log import logger, set_verbose

__all__ = ["DependencyMatrix", "GithubFinder"]


class DependencyMatrix(yaz.BasePlugin):
    json_key_file = None
    sheet_key = None

    def __init__(self):
        if not (self.json_key_file and self.sheet_key):
            raise RuntimeError("The json_key_file and sheet_key must be specified, please add a DependencyMatrix plugin override in your user directory")

    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def version(self, verbose: bool = False):
        set_verbose(verbose)
        return __version__

    @yaz.task
    def update_repo(self, user: str, name: str, verbose: bool = False):
        set_verbose(verbose)

        sheet = VersionMatrixSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            repo = self.github.get_user(user).get_repo(name)
            dependencies = {}
            dependencies.update(self.get_composer_dependencies(repo))
            dependencies.update(self.get_npm_dependencies(repo))
            if dependencies:
                sheet.set_dependencies(repo, dependencies)
        finally:
            sheet.unset_updating()

    @yaz.task
    def update_all(self, limit: int = 666, verbose: bool = False):
        set_verbose(verbose)

        sheet = VersionMatrixSheet(os.path.expanduser(self.json_key_file), self.sheet_key)
        sheet.set_updating()
        try:
            for repo in self.github.get_user().get_repos()[:limit]:
                dependencies = {}
                dependencies.update(self.get_composer_dependencies(repo))
                dependencies.update(self.get_npm_dependencies(repo))
                if dependencies:
                    sheet.set_dependencies(repo, dependencies)
        finally:
            sheet.unset_updating()

    def get_composer_dependencies(self, repo, ref=github.GithubObject.NotSet):
        try:
            file = repo.get_file_contents('/composer.lock', ref)
        except github.GithubException:
            return {}
        data = json.loads(file.decoded_content.decode())

        return {"composer {}".format(package['name']): package['version'].strip() for package in data['packages']}

    def get_npm_dependencies(self, repo, ref=github.GithubObject.NotSet):
        try:
            file = repo.get_file_contents('/package-lock.json', ref)
        except github.GithubException:
            try:
                file = repo.get_file_contents('/javascript/package-lock.json', ref)
            except github.GithubException:
                return {}
        data = json.loads(file.decoded_content.decode())

        if "dependencies" not in data:
            return {}

        return {"npm {}".format(name): dependency["version"].strip() for name, dependency in data['dependencies'].items()}

class GithubFinder(yaz.BasePlugin):
    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def search(self, pattern: str, filename: str = "/README.md", verbose: bool = False):
        set_verbose(verbose)
        exp = re.compile(pattern)

        for repo in self.github.get_user().get_repos():
            try:
                file = repo.get_file_contents(filename)
            except github.GithubException:
                logger.debug("%s: no file found", repo.name)
                continue

            content = file.decoded_content.decode()
            if exp.search(content):
                print(repo.name)
            else:
                logger.debug("%s: no match found", repo.name)

