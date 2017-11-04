# -*- coding: utf-8 -*-
import os
import re
import invoke

from .executables import exe
from .utils import fmt


default_command_policy = dict(
    negative_bool='omit',   # omit False boolean parameters (or 'prefix')
    list_join=',',
)


class Command(object):
    def __init__(self, name, argspec="",
                 requirements=(),
                 policy=default_command_policy,
                 **optdefs):
        self._args = (name, argspec, requirements, policy, optdefs)
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return
        name, argspec, requirements, policy, optdefs = self._args
        # handle any required params attached to the command, i.e. if the
        # command is specified as foo = Command('foo -v', ...)
        exename, reqparams = (name + ' ').split(' ', 1)
        # make sure all requirements are present
        exe.require(*requirements)
        if os.path.isfile(exename):         # if path to executable is given
            self.cmd = exename              # then use it
        else:
            self.cmd = exe.find(exename)    # else search path
        # fetch names of all argspec params
        self.params = [p[1:-1] for p in re.findall(r'\{[^}]*\}', argspec)]
        self.required_params = reqparams.strip()
        self.argspec = argspec
        self.policy = policy
        self.optdefs = optdefs
        self._initialized = True

    def _kw_to_opts(self, kw):
        res = ""
        for k, v in kw.items():
            # print 'k,v,res:', k, v, `res`
            if k in self.params:  # skip conversion of parameters to argspec
                continue

            res += ' '
            flag = ('-' if len(k) == 1 else '--') + k.replace('_', '-')

            if isinstance(v, bool):
                if v:
                    res += flag
                else:
                    if self.policy['negative_bool'] == 'prefix':
                        res += '--no' + flag

            elif isinstance(v, (list, tuple)) and v:
                res += flag + '=' + self.policy['list_join'].join(str(item) for item in v)

            elif isinstance(v, basestring):
                res += flag + '="%s"' % v

            else:
                res += flag + '=' + str(v)

        return res

    def __call__(self, ctx=None, *args, **kwargs):
        self._initialize()
        if ctx is not None and not isinstance(ctx, invoke.Context):
            # we've been passed a real argument in position 0
            args = (ctx,) + args
            ctx = None

        kwargs['opts'] = self._kw_to_opts(kwargs)
        posargs = ' '.join(args)
        if 'pos' in self.params:
            kwargs['pos'] = posargs
        fparams = fmt(self.argspec, kwargs)
        if 'pos' not in self.params:
            # if placement of positional args is not specified, then put at end
            fparams += " " + posargs
        if ctx is None:
            ctx = invoke.Context()

        cmd = '"%s"' % self.cmd if ' ' in self.cmd else self.cmd
        cmd += ' ' + self.required_params + fparams
        ctx.run(cmd)
        return cmd


tree = Command('tree -I ".git|*.pyc|*.swp|dist|*.egg-info|_static|_build|_templates"')
