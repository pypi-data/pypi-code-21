#coding:utf-8
'''
* coder  : Dzlua
* email  : 505544956@qq.com
* module : api-cli
* path   : api_cli
* file   : __init__.py
* time   : 2017/10/27
'''
#--------------------#
import click
from utils import base
#--------------------#

#--------------------#
class MyCLI(click.MultiCommand):
    def __init__(self, cmds=[], plugin_folder=None, *args, **kwargs):
        click.MultiCommand.__init__(self, *args, **kwargs)
        #
        self.set_cmds(cmds)
        #
        if plugin_folder:
            pls = self._get_plugins(plugin_folder)
            self.add_cmds(pls)
    def _get_plugins(self, plugin_folder):
        cmds = []
        for filename in base.listdir(plugin_folder):
            if not filename.endswith('.py'):
                continue
            cmd = filename[:-3]
            #
            ns = base.read_py(filename)
            cli = ns['cli']
            #
            cmds.append([cmd, cli])
        return cmds
    def _parser_cmds(self):
        cmds = []
        for v in self._cmds:
            cmds.append(v[0])
        return cmds
    def _parser_cli(self, name):
        for v in self._cmds:
            if v[0] == name:
                return v[1]
    #----------#
    def list_commands(self, ctx):
        return self._parser_cmds()
    def get_command(self, ctx, name):
        return self._parser_cli(name)
    #----------#
    def set_cmds(self, cmds):
        '''it will clear old cmds
        : [[cmd1, cli1],[cmd2, cli2]]'''
        self._cmds = cmds
    def add_cmds(self, cmds):
        '''[[cmd1, cli1],[cmd2, cli2]]'''
        for cmd in cmds:
            self._cmds.append(cmd)
        self._cmds.sort()
    def add_cmd(self, cmd, cli):
        self._cmds.append([cmd, cli])
        self._cmds.sort()
#--------------------#