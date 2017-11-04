# -*- coding: utf-8 -*-

import subprocess
from lektor.pluginsystem import Plugin

class MakePlugin(Plugin):
    name = 'make'
    description = u'Run `make lektor` for custom build systems.'

    def on_before_build_all(self, builder, **extra):
        subprocess.Popen(['make', 'lektor']).wait()
