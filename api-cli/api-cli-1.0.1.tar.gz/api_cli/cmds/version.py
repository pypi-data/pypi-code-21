#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/cmds
* file   : version.py
* time   : 2017/10/27
'''
#--------------------#
import click
#----------#
from ..acts import config
#--------------------#

#--------------------#
@click.command()
def version():
    '''show current api-frame version.'''
    click.echo(config.version)
#--------------------#

#--------------------#
cli = version
#--------------------#
