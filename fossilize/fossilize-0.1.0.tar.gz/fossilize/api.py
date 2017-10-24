#!/usr/bin/env python3

import datetime, shlex, subprocess
from pathlib import Path
from types import SimpleNamespace

def fossilize(command, output_path=None):
    slug = pick_slug(command)
    header = make_header(command)
    formatted_header = format_header(header)
    body = run_command(header.command, header.repo_dir)
    output_path = resolve_path(output_path or '$.txt', slug)

    write_file(output_path, formatted_header + '\n' + body)

def pick_slug(command):
    return Path(command[0]).stem

def make_header(command):
    header = SimpleNamespace()
    header.path = Path(command[0])

    if not header.path.exists():
        print(f"Error: '{header.path}' doesn't exist.")
        raise SystemExit

    # Figure out where the script is located relative to the root of its 
    # repository.  Complain if it's not in a repository.

    header.repo_dir = run_command(
            'git rev-parse --show-toplevel',
            cwd=header.path.resolve().parent,
            error=f"'{header.path}' not in a git repository.")

    header.relpath = header.path.resolve().relative_to(header.repo_dir)
    header.command = [f'./{header.relpath}'] + command[1:]
    header.command_str = ' '.join([shlex.quote(x) for x in header.command])

    # Complain if the script has any uncommitted changes.

    uncommitted_files = run_command(
            'git ls-files --modified --deleted --others --exclude-standard',
            cwd=header.repo_dir)

    if str(header.relpath) in uncommitted_files:
        print(f"Error: '{header.path}' has uncommitted changes.")
        print()
        print(run_command('git status', cwd=header.repo_dir))
        raise SystemExit

    # Add the URL of the repository, the current commit hash, and today's date 
    # to the header.

    header.repo_url = run_command(
            'git config --get remote.origin.url',
            cwd=header.repo_dir,
            error='ok') or header.repo_dir

    header.commit_hash = run_command(
            f'git log -n 1 --pretty=format:%H -- {shlex.quote(str(header.relpath))}',
            cwd=header.repo_dir,
            error="No commits found.")

    header.date = datetime.date.today()
    header.date_str = '{0:%B} {0.day}, {0.year}'.format(header.date)

    return header

def format_header(header):
    return f"""\
cmd: {header.command_str}
repo: {header.repo_url}
commit: {header.commit_hash}
date: {header.date_str}
"""
def run_command(command, cwd=None, error=None):
    if isinstance(command, str):
        command = shlex.split(command)

    # Don't try to execute text files.
    if len(command) == 1 and command[0].endswith('txt'):
        with open(command[0]) as file:
            return file.read()

    try:
        io = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE)
        return io.stdout.decode().strip()
    except subprocess.CalledProcessError:
        if error is None:
            raise
        elif error == 'ok':
            pass
        else:
            print('Error: ' + error)
            raise SystemExit

def resolve_path(path, slug, date=None):
    path = Path(path)
    date_cmd = f'{date or datetime.date.today():%Y%m%d}_{slug}'
    return path.parent / path.name.replace('$', date_cmd)

def write_file(path, content):
    path = Path(path)

    if path.exists():
        overwrite = input(f"'{path}' exists.  Overwrite it? [N/y] ")
        if overwrite.lower() != 'y':
            print('Aborting.')
            raise SystemExit

    with path.open('w') as file:
        file.write(content)

    print(f"Command recorded to: {path}")




