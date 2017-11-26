import click
import requests
import texttable

from collections import namedtuple

from typing import List, Dict

Row = namedtuple('Row', ['name', 'current_version', 'latest_version'])


class UpToDate():
    def __init__(self, file_path: str = None) -> None:
        self.scanner = RequirementsScanner(file_path)
        self.pypi = PyPI()
        self.printer = TablePrinter()

    def check(self) -> None:
        dependences = self.scanner.get_dependences()
        versions = self.pypi.get_versions(dependences.keys())
        rows = self._prepare_rows(dependences, versions)
        table = self.printer.draw(rows)

        click.echo(table)

    def _prepare_rows(
        self,
        dependences: Dict[str, str],
        latest_versions: Dict[str, str]
    ) -> List[Row]:
        return [
            Row(
                name=name,
                current_version=current_version,
                latest_version=latest_versions[name]
            )
            for name, current_version in dependences.items()
            if current_version != latest_versions[name]
        ]


class RequirementsScanner():
    DEFAULT_FILE_PATH = 'requirements.txt'

    def __init__(self, file_path: str = None) -> None:
        if not file_path:
            file_path = self.DEFAULT_FILE_PATH

        self.file_path = file_path

    def get_dependences(self) -> Dict[str, str]:
        dependences = {}

        with open(self.file_path, 'r') as f:
            for line in f.readlines():
                if self._is_supported(line):
                    name, version = line.strip().split('==')
                    dependences[name] = version

        return dependences

    def _is_supported(self, line: str) -> bool:
        is_supported = True

        if '==' not in line:
            is_supported = False
        if '[' in line and ']' in line:
            is_supported = False

        if not is_supported:
            click.secho('SKIPPED: {}'.format(line), fg='yellow')

        return is_supported


class PyPI():
    URL_PATTERN = 'https://pypi.python.org/pypi/{}/json'

    def get_versions(self, dependences: List[str]) -> Dict[str, str]:
        versions = {}

        for dependence in dependences:
            url = self.URL_PATTERN.format(dependence)
            response = requests.get(url)
            data = response.json()
            latest_version = data['info']['version']
            versions[dependence] = latest_version

        return versions


class TablePrinter():
    def __init__(self) -> None:
        self.table = texttable.Texttable()
        self.table.set_cols_align(["l", "c", "c"])
        self.table.set_cols_valign(["t", "m", "m"])
        self.table.set_cols_dtype(['t', 't', 't'])

    def draw(self, rows: List[Row]) -> str:
        if len(rows) == 0:
            return click.style('Everything is up to date', fg='green')

        headers = ['Name', 'Current version', 'Latest_version']
        table_rows = [
            [row.name, row.current_version, row.latest_version]
            for row in rows
        ]
        table_rows.insert(0, headers)
        self.table.add_rows(table_rows)

        return self.table.draw()
