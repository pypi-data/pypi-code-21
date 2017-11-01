import datetime
import pathlib
import re
import hug
import os

PWD = pathlib.Path(__file__).parent.resolve()
PROJ_PATH = PWD.parent.resolve()
VERSION_FILE = PWD.joinpath('__init__.py').resolve()
SCRIPT_FILE = PWD.joinpath('scripts.sh').resolve()
SERVER_PROJECT_PATH = pathlib.Path(os.path.expanduser('~/daq_server'))


def run(cmd, echo=True, dry_run=False):
    if echo:
        print(cmd)

    if not dry_run:
        os.system(cmd)


@hug.cli()
def configure():
    backup()
    # make sure server is installed
    if not SERVER_PROJECT_PATH.is_dir():
        cmd = 'cd ~ && git clone git@github.com:brakettech/daq_server.git'
        run(cmd)

    # make sure db file exists
    if not SERVER_PROJECT_PATH.joinpath('db.sqlite3').is_file():
        cmd = f'cd {SERVER_PROJECT_PATH.as_posix()} && python manage.py migrate'
        run(cmd)

    # make sure daqroot simlink exists
    if not os.path.isdir('/daqroot'):
        print('\n\nWarning: You haven\'t created a /daqroot directory.\n\n')


@hug.cli()
def backup():
    db_dump_path = SERVER_PROJECT_PATH.joinpath('dbdumps')
    if not db_dump_path.is_dir():
        run(f'mkdir {db_dump_path}')

    dump_file = datetime.datetime.now().strftime(
        '%Y-%m-%dT%H-%M-%S-%f') + '.json.gz'
    dump_file = db_dump_path.joinpath(dump_file)
    cmd = (
        f'cd {SERVER_PROJECT_PATH} && '
        f'python manage.py dumpdata | gzip >{dump_file}'
    )
    run(cmd)


@hug.cli()
def version():
    with open(VERSION_FILE) as in_file:
        version_file_contents = in_file.read()
    version_match = re.search(r"""^__version__ = ['"]([^'"]*)['"]""",
                              version_file_contents, re.M)
    if version_match:
        print('braket-daq=={}'.format(version_match.group(1)))


@hug.cli()
def infect():
    commands = [
        'rm ~/.bashrc',
        f'cat {SCRIPT_FILE} ~/dot_files/.bashrc  > ~/.bashrc',
    ]
    for cmd in commands:
        run(cmd)

    print('\n\n')
    print('Run this command to complete infection:  . ~/.bashrc')
    print()
