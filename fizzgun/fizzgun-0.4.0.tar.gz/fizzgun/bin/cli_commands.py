import os

from fizzgun.application.dependencies import NoOpStdoutWriter
from fizzgun.application.service_contexts import (CmdRunFizzgunContext, CmdBubblesContext, CmdGenerateConfigContext)
from fizzgun.bubbles.bubble_arsenal import BubbleArsenal
from fizzgun.config import Config
from fizzgun.impl.fizzgun_runner import FizzgunRunner
from fizzgun.util import fizzgun_path


__all__ = ['CmdRunFizzgun', 'CmdBubbles', 'CmdGenerateConfig']


class CmdRunFizzgun(object):

    def __init__(self, context: CmdRunFizzgunContext = None):
        self._ctx = context or CmdRunFizzgunContext()

    def run(self, options):
        config = Config(options.config, self._ctx.file_system)
        FizzgunRunner(self._ctx, config).run()


class CmdGenerateConfig(object):
    def __init__(self, context: CmdGenerateConfigContext = None):
        self._ctx = context or CmdGenerateConfigContext()

    def run(self, options):
        file_name = options.filename or 'fizzgun.yaml'
        dir_name = os.path.dirname(file_name)
        if dir_name:
            self._ctx.file_system.create_directory(dir_name)

        if options.defaults:
            source = fizzgun_path('data', 'config_defaults.yaml')
        else:
            source = fizzgun_path('data', 'config_template.yaml')

        self._ctx.file_system.copy_file(source, file_name)

        self._ctx.stdout_writer.write("File generated at: %s" % os.path.abspath(file_name))


class CmdBubbles(object):
    def __init__(self, context: CmdBubblesContext = None):
        self._ctx = context or CmdBubblesContext()

    def run(self, options):
        config = Config(options.config, self._ctx.file_system)
        arsenal = BubbleArsenal(self._ctx.module_importer, self._ctx.id_generator,
                                self._ctx.random_generator, NoOpStdoutWriter())
        arsenal.load_from_config(config.bubbles)

        stdout = self._ctx.stdout_writer

        for bubble in arsenal.bubbles():
            stdout.write("Name:", bubble.name)

            stdout.write("Description:", bubble.description)

            tags = "\n".join("  * %s" % t for t in getattr(bubble, 'TAGS', []))
            stdout.write("Tags:\n%s" % tags)

            expectations = "\n".join("  * %s" % e for e in str(bubble.expectations).split("\n"))
            stdout.write("Expectations:\n%s" % expectations + "\n")
