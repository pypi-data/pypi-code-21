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
from ..acts import tools as tl
from ..acts import config as cfg
#--------------------#

#--------------------#
@click.group()
def tools():
    '''api-cli tools'''
#--------------------#

#--------------------#
def check_header_type(ext, t):
    if t:
        return t
    tps = cfg.get_header_types()
    for tp in tps:
        if '.' + tp == ext:
            return tp
    return None

#--------------------#

#--------------------#
@tools.command()
@click.option('--type', '-t', default=None,
    type=click.Choice(cfg.get_header_types()),
    help='the templete type to use.')
@click.argument('files', nargs=-1, type=click.Path())
def addfile(files, type):
    '''add files'''
    if not files:
        click.echo('please input files. ex: > addfile a/b.py c.py')
        return
    errs = []
    print('files: %s, writing...' % len(files))
    for f in files:
        t = check_header_type(base.file_ext(f)[1], type)
        bok = False
        if t:
            bok = base.create_file(f, tl.addfile_get_content(f, t))
        else:
            bok = base.create_file(f)
        click.echo(u'%s %s -> %s' % (bok,t,f))
    print('files: %s, errors: %s' % (len(files), len(errs)) )
    if len(errs) == 0:
        print('Done!')
#--------------------#

#--------------------#
cli = tools
#--------------------#
