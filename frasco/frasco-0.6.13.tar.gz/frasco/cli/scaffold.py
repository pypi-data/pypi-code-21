import click
from flask import current_app
from flask.cli import with_appcontext
from .run import procfile_processes
import os
import random


def gen_secret_key():
    return ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])


@click.command("init")
@click.argument('path', default='.')
def init_command(path):
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(os.path.join(path, 'views')):
        os.mkdir(os.path.join(path, 'views'))
    secret_key = gen_secret_key()
    with open(os.path.join(path, 'app.yml'), 'w') as f:
        f.write("secret_key: \"%s\"\n" % secret_key)
    with open(os.path.join(path, 'app-dev.yml'), 'w') as f:
        f.write("debug: true\n")
    with open(os.path.join(path, 'views/index.html'), 'w') as f:
        f.write("---\nurl: /\n---\n{% use_layout %}\nHello world from Frasco")


@click.group("gen")
def gen_command():
    """Helpers to generate useful files"""


@gen_command.command('secret-key')
def gen_secret_key_cmd():
    click.echo(gen_secret_key())


@gen_command.command("app.py")
def gen_apppy():
    """Generates an app.py file
    """
    with open("app.py", "w") as f:
        f.write(("from frasco import DeclarativeFrasco\n\n\n"
                 "app = DeclarativeFrasco(__name__)"))


@gen_command.command("procfile")
@click.option("--wsgi", default=None,
    help="Name of the file containing the application")
@click.option("--dev/--no-dev", default=False,
    help="Whether to generate a Procfile for the dev environment")
@with_appcontext
@click.pass_context
def gen_procfile(ctx, wsgi, dev):
    """Generates Procfiles which can be used with honcho or foreman.
    """
    if wsgi is None:
        if os.path.exists("wsgi.py"):
            wsgi = "wsgi.py"
        elif os.path.exists("app.py"):
            wsgi = "app.py"
        else:
            wsgi = "app.py"
            ctx.invoke(gen_apppy)

    def write_procfile(filename, server_process, debug):
        processes = [server_process] + current_app.processes
        procfile = []
        for name, cmd in procfile_processes(processes, debug).iteritems():
            procfile.append("%s: %s" % (name, cmd))
        with open(filename, "w") as f:
            f.write("\n".join(procfile))

    write_procfile("Procfile", ("web", ["gunicorn", wsgi]), False)
    if dev:
        write_procfile("Procfile.dev", ("web", ["frasco", "serve"]), True)