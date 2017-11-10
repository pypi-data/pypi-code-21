import click, os
import flextime
from flextime.interface import List, Add, Show

@click.group()
@click.option('--datafile', '-f', default='tasks.yml')
@click.pass_context
def cli(ctx, datafile):
    ctx.obj = {'tasktree': flextime.TaskTree(datafile)}

@cli.command()
@click.argument('sort_keys', nargs=-1)
@click.pass_obj
def list(obj, sort_keys):
    """Display a sorted list of tasks."""
    List(obj['tasktree'], sort_keys).run()

@cli.command()
@click.argument('path', nargs=-1)
@click.option('-m', '--merge-files', multiple=True)
@click.pass_obj
def add(obj, path, merge_files):
    """Add to an existing tree. Guess path in tree if arguments provided."""
    Add(obj['tasktree'], path, merge_files).run()

@cli.command()
@click.argument('schedule_file', default='schedule.yml')
@click.pass_obj
def show(obj, schedule_file):
    """Attempt to optimally schedule tasks against blocks of time configured in a schedule file."""
    Show(obj['tasktree'], schedule_file).run()
