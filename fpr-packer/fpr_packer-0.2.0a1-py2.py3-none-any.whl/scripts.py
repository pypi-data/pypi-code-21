import json
import os
from subprocess import check_call, check_output, STDOUT
import click
from importlib import import_module
from importlib.util import find_spec
import sys

from pathlib import Path


@click.command('FPR images builder')
@click.argument('packer_dir', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, help='log packer build')
@click.option('-t', '--trace', is_flag=True, help='echo packer command (don\'t execute it)')
@click.option('-o', '--only', type=click.Choice(['aws', 'docker']), help='use only one builder')
def packer_build(packer_dir=None, *, debug=None, trace=None, only=None):
    env = {}
    home_dir = Path(os.getcwd())
    if packer_dir is None:
        packer_dir = home_dir / "packer"

    if debug:
        env['PACKER_LOG'] = '1'

    cmd = ["packer", "build", f"-var-file={packer_dir}/vars.json"]
    if only:
        cmd.append(f"-only={only}")
    cmd += [f"{packer_dir}/template.json"]

    if trace:
        click.echo(cmd)
    else:
        check_call(cmd, env=dict(os.environ, **env))


@click.command('FPR images installer')
@click.argument('packer_dir', type=click.Path(exists=True))
def packer_install(packer_dir=None):
    print(packer_dir)
    print(Path(os.getcwd()))
    loader = find_spec(packer_dir)
    print(loader)
    print(sys.meta_path)
    # for finder in sys.meta_path:
    #     print(finder.find_spec('test'))
    mod = import_module(f"packer")
    print(dir(mod))
