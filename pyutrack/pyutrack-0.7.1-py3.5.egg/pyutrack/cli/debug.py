import click
import yaml
from click import get_current_context

from pyutrack import *
from . import cli


@cli.group()
@click.pass_context
@click.option("--interactive", is_flag=True)
def debug(ctx, interactive):
    """
    debug the structure of youtrack resources
    """
    pass

@debug.resultcallback()
def result(result, interactive=False):
    if interactive:
        locals_ = {
            get_current_context().invoked_subcommand: result
        }
        banner="Access the %s object using the '%s' variable" % (
            result.__class__.__name__, get_current_context().invoked_subcommand
        )
        try:
            import bpython
            bpython.embed(locals_=locals_, banner=banner)
        except ImportError:
            import code
            code.interact(local=locals_, banner=banner)
    else:
        get_current_context().obj.render(yaml.dump(result.debug()))


@debug.command()
@click.pass_context
@click.option('--id', default=None)
def issue(ctx, id):
    return Issue(ctx.obj.connection, id=id, hydrate=id is not None)


@debug.command()
@click.pass_context
@click.option('--id', default=None)
def project(ctx, id):
    return Project(ctx.obj.connection, id=id, hydrate=id is not None)


@debug.command()
@click.pass_context
@click.option('--login', default=None)
def user(ctx, login):
    return User(ctx.obj.connection, login=login, hydrate=login is not None)


@debug.command()
@click.pass_context
@click.option('--name', default=None)
def group(ctx, name):
    return Group(ctx.obj.connection, name=name, hydrate=name is not None)

@debug.command()
@click.pass_context
@click.option('--name', default=None)
def role(ctx, name):
    return Role(ctx.obj.connection, name=name, hydrate=name is not None)

@debug.command()
@click.pass_context
@click.option('--name', default=None)
def permission(ctx, name):
    return Permission(ctx.obj.connection, name=name, hydrate=name is not None)
