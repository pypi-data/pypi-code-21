# This file is part of tako
# Copyright (c) 2015-2017 Adam Hartz <hartz@mit.edu> and contributors
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# tako is a fork of xonsh (http://xon.sh)
# xonsh is Copyright (c) 2015-2016 the xonsh developers and is licensed under
# the 2-Clause BSD license.

# -*- coding: utf-8 -*-
"""The tako shell"""
import os
import builtins

from collections import defaultdict

from takoshell.tools import display_error_message
from takoshell.execer import Execer
from takoshell.plugins import PluginEnv
from takoshell.environ import takorc_context
from takoshell.settings import Settings


class Shell(object):
    """Main tako shell.

    Initializes execution environment.
    """

    def __init__(self, ctx=None, config=None, headless=False, **kwargs):
        """
        Parameters
        ----------
        ctx : Mapping, optional
            The execution context for the shell (e.g. the globals namespace).
            If none, this is computed by loading the rc files. If not None,
            this no additional context is computed and this is used
            directly.
        config : str, optional
            Path to configuration file.
        """
        self.login = kwargs.get('login', True)
        self.headless = headless
        self.kwargs = kwargs
        builtins.__tako_shell__ = self
        self._init_environ(ctx,
                           kwargs.get('scriptcache', True),
                           kwargs.get('cacheall', False))
        if not self.headless:
            self._init_plugins(ctx)

    def __getattr__(self, attr):
        """Delegates calls to appropriate shell instance."""
        return getattr(self.shell, attr)

    def _init_environ(self, ctx, scriptcache, cacheall):
        self.ctx = {} if ctx is None else ctx
        self.execer = Execer(login=self.login, tako_ctx=self.ctx)
        self.execer.scriptcache = scriptcache
        self.execer.cacheall = cacheall
        if self.login:
            # load run control files
            self.ctx.update(takorc_context(rcfile='/etc/takorc', absolute=True, execer=self.execer, initial=self.ctx))
            self.ctx.update(takorc_context(rcfile='preload.tako', execer=self.execer, initial=self.ctx))
        self.ctx['__name__'] = '__main__'
        try:
            shell_type = builtins.__tako_env__.get('TAKO_SETTINGS').shell_type
        except:
            shell_type = 'readline'
        if (not self.headless) and shell_type == 'readline':
            from takoshell.readline_shell import ReadlineShell as shell_class
        else:
            from takoshell.base_shell import BaseShell as shell_class
        self.shell = shell_class(execer=self.execer,
                                 ctx=self.ctx, **self.kwargs)

    def _init_plugins(self, ctx):
        env = builtins.__tako_env__
        settings = env['TAKO_SETTINGS']
        plugin_dir = os.path.join(settings.config_dir, 'plugins')
        if not os.path.isdir(plugin_dir):
            return
        all_plugins = os.listdir(plugin_dir)
        for p in all_plugins:
            if not p.endswith('.tako'):
                continue
            name = p.rsplit('.', 1)[0]
            full_path = os.path.join(plugin_dir, p)
            if not os.path.isfile(full_path):
                continue
            env_contents = {'PLUGIN_SETTINGS': Settings({'ALIASES': {}, 'HOOKS': defaultdict(list)})}
            try:
                new_env = PluginEnv(env_contents, parent=ctx)
                self.execer.exec(open(full_path).read(), glbs=new_env)
                settings.plugins[name.upper()] = new_env['PLUGIN_SETTINGS']
            except:
                print('Error loading plugin %s' % name)
                display_error_message()
