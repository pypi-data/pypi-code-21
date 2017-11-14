#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli
* file   : main.py
* time   : 2017/10/27
'''
#--------------------#
from . import MyCLI
#----------#
from cmds import config
from cmds import create
from cmds import tools
from cmds import version
#--------------------#

#--------------------#
cli = MyCLI(help='Tools for create api-frame project.')
#--------------------#

#--------------------#
cli.add_cmd('config', config.cli)
cli.add_cmd('create', create.cli)
cli.add_cmd('tool', tools.cli)
cli.add_cmd('version', version.cli)
#--------------------#
