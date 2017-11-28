# coding: utf-8

"""
    Implements some packer script helpers.

    @packer.command                                                             # packer decorator to add default option
    @click.option('--deploy/--no-deploy', default=True, help='deploy image')    # adds other option
    @click.pass_context                                                         # needed to call the real build command
    def deploy(ctx, **kwargs):
        ctx.invoke(packer.build, packer_dir='./packer', **kwargs)
"""

import os
from functools import update_wrapper
from subprocess import check_call

import click


def copy_param(dest, src):
    if isinstance(src, click.Command):
        params = src.params
    else:
        if not hasattr(src, '__click_params__'):
            src.__click_params__ = []
        params = src.__click_params__

    for param in params:
        if isinstance(dest, click.Command):
            dest.params.append(param)
        else:
            if not hasattr(dest, '__click_params__'):
                dest.__click_params__ = []
            dest.__click_params__.append(param)


def command(f):
    @click.command(f.__doc__)
    @click.option('--debug/--no-debug', default=False)
    @click.option('--trace/--no-trace', default=False)
    @click.option('-o', '--only', type=click.Choice(['aws', 'docker']), help='use only one builder')
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        return ctx.invoke(f, *args, **kwargs)

    copy_param(new_func, f)

    return update_wrapper(new_func, f)


@command
@click.argument('packer_dir', type=click.Path(exists=True))
def build(packer_dir='./packer', **kwargs):
    """Build image from packer"""

    env = {'PACKER_LOG': '1'} if kwargs['debug'] else {}

    cmd = ["packer", "build", f"-var-file={packer_dir}/vars.json", "-color=false"]
    if kwargs['only']:
        cmd.append(f"-only={kwargs['only']}")
    cmd += [f"{packer_dir}/template.json"]

    if kwargs['trace']:
        click.echo(cmd)
    else:
        check_call(cmd, env=dict(os.environ, **env))
