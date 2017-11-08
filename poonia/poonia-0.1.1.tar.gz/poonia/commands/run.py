import click
import glob, os, sys

fs_encoding = sys.getfilesystemencoding()

@click.command(help='Run a command for files matching a pattern')
@click.argument('pattern', nargs=1)
@click.argument('command', nargs=-1, required=True)
def run(pattern, command):
    e = lambda x: '"%s"' % x if ' ' in x else x
    for fn in glob.glob(pattern):
        cmd = ' '.join(e(x) if x != '{}' else e(fn) for x in command)
        click.secho(cmd, bg='green', fg='white', bold=True, err=True)
        os.system(cmd.encode(fs_encoding))

@click.command(help='Run a command / expand a pattern')
@click.argument('pattern', nargs=1)
@click.argument('command', nargs=-1, required=True)
def rune(pattern, command):
    e = lambda x: '"%s"' % x if ' ' in x else x
    fns = ' '.join(e(x) for x in glob.glob(pattern))
    cmd = ' '.join(e(x) if x != '{}' else fns for x in command)
    click.secho(cmd, bg='green', fg='white', bold=True, err=True)
    os.system(cmd.encode(fs_encoding))
