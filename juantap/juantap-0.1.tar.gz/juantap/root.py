import os
import stat
import click
import requests
import sh

from . import CFG

LGSM_DL_URL = "https://raw.githubusercontent.com/mathiassmichno/LinuxGSM/master/linuxgsm.sh"


@click.group()
@click.option('--dir', 'root_dir', type=click.Path(), default=CFG['system']['RootServerDir'], help="Path to root server directory")
@click.pass_context
def root(ctx, root_dir):
    """
    Control root server from here
    """
    if root_dir != CFG['system']['RootServerDir']:
        CFG['system']['RootServerDir'] = root_dir


@root.command()
@click.option('--install', is_flag=True, help='Install Linux Game Server Manager')
@click.confirmation_option(help='Are you sure you want to set up a rootserver?')
@click.pass_context
def setup(ctx, install):
    """
    Setup root server, see --help for more
    """
    root_dir = CFG['system']['RootServerDir']
    click.confirm('Set up root server in "{}"?'.format(root_dir), abort=True)
    os.makedirs(root_dir, exist_ok=True)
    os.chdir(root_dir)
    lgsm_script_fname = 'linuxgsm.sh'
    click.echo('Downloading Linux Game Server Manager Script')
    lgsm_script_file = requests.get(LGSM_DL_URL, stream=True)
    with open(lgsm_script_fname, 'wb') as f:
        for chunk in lgsm_script_file.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    st = os.stat(lgsm_script_fname)
    os.chmod(lgsm_script_fname, st.st_mode | stat.S_IEXEC)
    lgsm_script = sh.Command('./' + lgsm_script_fname)
    lgsm_script('csgoserver')
    if install:
        click.echo('Installing CS:GO in root server')
        csgoserver_script = sh.Command('./csgoserver')
        csgoserver_script('auto-install')


@root.command('config')
@click.option('-e', is_flag=True, help='open config in editor')
@click.option('-c', is_flag=True, help='copy common stuff to cfg')
@click.pass_context
def root_config(ctx, e, c):
    server_cfg_dir = os.path.join(CFG['system']['RootServerDir'], 'lgsm/config-lgsm/csgoserver')
    if c:
        with open(os.path.join(server_cfg_dir, '_default.cfg'), 'r') as default_cfg:
            with open(os.path.join(server_cfg_dir, 'common.cfg'), 'w') as common_cfg:
                for line in default_cfg:
                    if "## Server Start Command" in line:
                        break
                    common_cfg.write(line)
    if e:
        click.edit(filename=os.path.join(server_cfg_dir, 'common.cfg'))
    if not e and not c:
        click.echo(ctx.get_help())
