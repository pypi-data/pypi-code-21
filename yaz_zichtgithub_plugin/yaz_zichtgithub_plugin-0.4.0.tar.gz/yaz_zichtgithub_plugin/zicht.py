import os
import re
import github
import github.GithubObject
import json
import yaz
import tabulate

from .version import __version__
from .spreadsheet import VersionMatrixSheet
from .github import Github
from .log import logger, set_verbose

__all__ = ["DependencyMatrix", "GithubScanner", "GithubFinder"]


class DependencyMatrix(yaz.BasePlugin):
    json_key_file = None
    sheet_key = None

    def __init__(self):
        if not (self.json_key_file and self.sheet_key):
            raise RuntimeError(
                "The json_key_file and sheet_key must be specified, please add a DependencyMatrix plugin override in your user directory")

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

        return {"npm {}".format(name): dependency["version"].strip() for name, dependency in
                data['dependencies'].items()}


class ZichtRepository:
    def __init__(self, repository: github.Repository.Repository):
        self._repository = repository

    @property
    def is_zicht_repository(self):
        return "zicht" == self._repository.owner.login

    @property
    def identity(self):
        return "{repo.owner.login}/{repo.name}".format(repo=self._repository)

    @property
    def name(self):
        return self._repository.name

    @property
    def _description(self):
        description = str(self._repository.description)
        match = re.match(r"^(?P<type>library|website|utility)\s+-\s+(?P<description>.+)$", description, re.IGNORECASE)
        if match:
            return match.group("type").capitalize(), match.group("description")
        return "", ""

    @property
    def type(self):
        return self._description[0]

    @property
    def description(self):
        return self._description[1]

    @property
    def maintainers(self):
        try:
            readme = self._repository.get_readme().decoded_content.decode("utf-8")
        except github.UnknownObjectException:
            readme = ""

        maintainers = []
        it = iter(readme.splitlines())
        for line in it:
            if re.match(r"^#\s*maintainer", line, re.IGNORECASE):
                for line in it:
                    if re.match(r"^#", line):
                        break
                    match = re.match(r"^[\s*-]*(?P<maintainer>.+?)\s*(?P<mail><.*>)$", line)
                    if match:
                        maintainers.append(match.group("maintainer"))
                break

        return maintainers

    @property
    def errors(self):
        errors = []
        if not self.type:
            errors.append("type")
        if not self.description:
            errors.append("description")
        if not self.maintainers and self.type == "library":
            errors.append("maintainter")
        return errors

    @staticmethod
    def get_table_header():
        return ["type", "name", "description", "maintainers", "errors"]

    def get_table_row(self):
        return [self.type, self.name, self.description, ", ".join(sorted(self.maintainers)), ", ".join(self.errors)]

    def __str__(self):
        return self.identity


class GithubScanner(yaz.BasePlugin):
    @yaz.dependency
    def set_github(self, github: Github):
        self.github = github.get_service()

    @yaz.task
    def scan(self, limit: int = 666, verbose: bool = False):
        set_verbose(verbose)

        table = []
        for repo in [ZichtRepository(repo) for repo in self.github.get_user().get_repos()[:limit]]:
            logger.info("Scanning %s", repo.name)
            table.append(repo.get_table_row())
        return tabulate.tabulate(table, headers=ZichtRepository.get_table_header())


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
