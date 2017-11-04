import os
from subprocess import check_call, check_output, STDOUT
import click
from importlib.util import spec_from_file_location, module_from_spec

from pathlib import Path


@click.command('FPR images builder')
@click.argument('packer_dir', type=click.Path(exists=True))
@click.option('-d', '--debug', is_flag=True, help='log packer build')
@click.option('-t', '--trace', is_flag=True, help='echo packer command (don\'t execute it)')
@click.option('-o', '--only', type=click.Choice(['aws', 'docker']), help='use only one builder')
def packer_build(packer_dir=None, *, debug=None, trace=None, only=None):
    env = {'PACKER_LOG': '1'} if debug else {}

    if packer_dir is None:
        home_dir = Path(os.getcwd())
        packer_dir = home_dir / "packer"

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
    spec = spec_from_file_location('packer_install', f"{packer_dir}/install.py")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    module.install()
