#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/cmds
* file   : tools.py
* time   : 2017/10/27
'''
#--------------------#
import click
#----------#
from ..utils import base
from ..utils import helper as hp
from ..acts import config as cfg
#--------------------#

#--------------------#
@click.group()
def config():
    '''config api-cli.'''    
#--------------------#

#--------------------#
@config.command()
@click.argument('keys', nargs=-1)
def list(keys):
    '''list api-cli config options.'''
    datas = []
    if keys:
        datas = cfg.get_configs(keys)
    else:
        datas = cfg.get_config_all()
    for k, v in datas.items():
        click.echo(u'%s: %s' % (k,v))
#----------#
@config.command()
@click.argument('keys', nargs=-1)
def delete(keys):
    '''delete api-cli config options.'''
    if keys:
        datas = cfg.get_configs(keys)
        if len(datas) == 0:
            click.echo('No keys!')
            return
        for k, v in datas.items():
            click.echo(u'%s: %s' % (k,v))
        ret = hp.get_input_yes('Are you sure you want to delete these options?')
        if not ret:
            click.echo('Aborted!')
            return
        #
        cfg.del_configs(keys)
        click.echo('Deleted!')
    else:
        click.echo('please input keys.')
#----------#
@config.command()
@click.option('--key',
    prompt='key to config',
    help='the api-cli config key you will edit.')
@click.option('--value',
    prompt='value of key',
    help='value of the key you will edit.')
def edit(key, value):
    '''edit api-cli config file.'''
    cfg.set_config(key, value)
#----------#
@config.command()
@click.option('--yes', is_flag=True, callback=hp.abort_if_false,
    expose_value=False,
    prompt='Are you sure you want to set api-cli config to default ?')
def init():
    '''set api-cli config to default.'''
    click.echo('set config to default ...')
    cfg.set_config_to_default()
    click.echo('Done!')
#--------------------#

#--------------------#
cli = config
#--------------------#
