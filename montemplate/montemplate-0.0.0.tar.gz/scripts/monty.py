#!/usr/bin/env python3
import os
import posixpath
import sys
from functools import partial
from itertools import filterfalse
from pathlib import PurePath
from typing import (Any,
                    Callable,
                    Iterable,
                    Iterator,
                    Dict,
                    Tuple)

import click
import requests
import yaml

__version__ = '0.0.0'

TRANSLATION_TABLE = frozenset({7, 8, 9, 10, 12, 13, 27}
                              | set(range(0x20, 0x100)) - {0x7f})

urljoin = posixpath.join


def api_method_url(method: str,
                   *,
                   base_url: str,
                   version: str) -> str:
    return urljoin(base_url, version, method)


def load_user(login: str,
              *,
              base_url: str = 'https://hub.docker.com',
              version: str = 'v2',
              users_method_url: Callable[..., str]) -> requests.Response:
    users_url = users_method_url(base_url=base_url,
                                 version=version)
    user_url = urljoin(users_url, login)

    with requests.Session() as session:
        return session.get(user_url)


def load_dockerhub_user(login: str,
                        *,
                        base_url: str = 'https://hub.docker.com',
                        version: str = 'v2') -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    response = load_user(login=login,
                         base_url=base_url,
                         version=version,
                         users_method_url=users_method_url)
    try:
        response.raise_for_status()
    except requests.HTTPError as err:
        err_msg = ('Invalid login: "{login}". '
                   'Not found via API request to "{url}".'
                   .format(login=login,
                           url=response.url))
        raise ValueError(err_msg) from err
    else:
        return response.json()


def load_github_user(login: str,
                     *,
                     base_url='https://api.github.com') -> Dict[str, Any]:
    users_method_url = partial(api_method_url,
                               'users')
    response = load_user(login=login,
                         base_url=base_url,
                         version='',
                         users_method_url=users_method_url)
    user = response.json()
    try:
        err_msg = user['message']
        raise ValueError(err_msg)
    except KeyError:
        return user


@click.command()
@click.option('--version', '-v',
              is_flag=True,
              help='Displays script version information.')
@click.option('--settings-path', '-s',
              default='settings.yml',
              help='Path (absolute or relative) to settings '
                   '(defaults to "settings.yml").')
@click.option('--template-dir', '-t',
              default='template',
              help='Path (absolute or relative) to template project '
                   '(defaults to "template").')
@click.option('--output-dir', '-o',
              default='.',
              help='Path (absolute or relative) to output directory '
                   '(defaults to current working directory).')
@click.option('--overwrite',
              is_flag=True,
              help='Overwrites files if output directory exists.')
def main(version: bool,
         settings_path: str,
         template_dir: str,
         output_dir: str,
         overwrite: bool) -> None:
    if version:
        sys.stdout.write(__version__)
        return

    os.makedirs(output_dir,
                exist_ok=True)

    with open(settings_path) as settings_file:
        settings = yaml.safe_load(settings_file)

    dockerhub_login = settings['dockerhub_login']
    github_login = settings['github_login']
    dockerhub_user = load_dockerhub_user(dockerhub_login)
    github_user = load_github_user(github_login)
    settings.setdefault('full_name',
                        github_user['name'] or dockerhub_user['full_name'])
    replacements = {'__{key}__'.format(key=key): value
                    for key, value in settings.items()}
    non_binary_files_paths = filterfalse(is_binary_file,
                                         files_paths(template_dir))
    paths_pairs = replace_files_paths(non_binary_files_paths,
                                      src=template_dir,
                                      dst=output_dir,
                                      replacements=replacements)
    for file_path, new_file_path in paths_pairs:
        if not overwrite and os.path.exists(new_file_path):
            err_msg = ('Trying to overwrite '
                       'existing file "{path}", '
                       'but no "--overwrite" flag was set.'
                       .format(path=new_file_path))
            raise click.BadOptionUsage(err_msg)
        with open(file_path) as file:
            new_lines = list(replace_lines(file,
                                           replacements=replacements))
        directory_path = os.path.dirname(new_file_path)
        os.makedirs(directory_path,
                    exist_ok=True)
        with open(new_file_path,
                  mode='w') as new_file:
            new_file.writelines(new_lines)


def is_binary_file(path: str) -> bool:
    with open(path, mode='rb') as file:
        return is_binary_string(file.read(1024))


def is_binary_string(bytes_string: bytes,
                     *,
                     translation_table: Iterable[int] = TRANSLATION_TABLE
                     ) -> bool:
    return bool(bytes_string.translate(None, bytearray(translation_table)))


def files_paths(path: str) -> Iterator[str]:
    for root, _, files_names in os.walk(path):
        for file_name in files_names:
            yield os.path.join(root, file_name)


def replace_files_paths(paths: Iterable[str],
                        *,
                        src: str,
                        dst: str,
                        replacements: Dict[str, str]
                        ) -> Iterator[Tuple[str, str]]:
    for path in paths:
        new_path = replace_file_path(path,
                                     src=src,
                                     dst=dst,
                                     replacements=replacements)
        yield path, new_path


def replace_file_path(file_path: str,
                      *,
                      src: str,
                      dst: str,
                      replacements: Dict[str, str]) -> str:
    root, file_name = os.path.split(file_path)
    new_file_name, = replace_path_parts(file_name,
                                        replacements=replacements)
    new_root_parts = PurePath(root.replace(src, dst)).parts
    new_root_parts = replace_path_parts(*new_root_parts,
                                        replacements=replacements)
    new_root = str(PurePath(*new_root_parts))
    return os.path.join(new_root, new_file_name)


def replace_path_parts(*path_parts: str,
                       replacements: Dict[str, str]) -> Iterator[str]:
    for path_part in path_parts:
        yield replacements.get(path_part, path_part)


def replace_lines(lines: Iterable[str],
                  *,
                  replacements: Dict[str, str]) -> Iterator[str]:
    replacements_items = replacements.items()
    for line in lines:
        for key, value in replacements_items:
            line = line.replace(key, value)
        yield line


if __name__ == '__main__':
    main()
