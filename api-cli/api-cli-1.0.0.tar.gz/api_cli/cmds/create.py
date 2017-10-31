#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli/cmds
* file   : create.py
* time   : 2017/10/27
'''
#--------------------#
import click
#----------#
from ..acts import create as ct
from ..utils import base
#--------------------#

#--------------------#
@click.command()
@click.argument('name', nargs=1)
def create(name):
    '''create api-frame project.'''
    ct.create(name)
#--------------------#

#--------------------#
cli = create
#--------------------#
