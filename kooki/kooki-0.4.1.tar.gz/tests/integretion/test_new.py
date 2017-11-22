import unittest, tempfile, os, argparse

from kooki.commands.new import NewCommand
from kooki.commands.bake import BakeCommand

from kooki.tools.output import Output

Output.set_output_policy(False)

new = NewCommand()
bake = BakeCommand()

class TestSimpleNewAndBake(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.new_args = argparse.Namespace()
        cls.new_args.name = ''
        cls.new_args.content = []
        cls.new_args.template = ''
        cls.new_args.recipe = ''
        cls.new_args.jars = []
        cls.new_args.metadata = []
        cls.new_args.content = []

        cls.bake_args = argparse.Namespace()
        cls.bake_args.config_file = 'kooki.yaml'
        cls.bake_args.documents = []

    def test_new_command(self):

        tempdir = tempfile.mkdtemp()
        os.chdir(tempdir)

        new.callback(TestSimpleNewAndBake.new_args)

        listdir = os.listdir()
        self.assertIn('metadata.yaml', listdir)
        self.assertIn('kooki.yaml', listdir)
        self.assertIn('content.md', listdir)

        bake.callback(TestSimpleNewAndBake.bake_args)
        listdir = os.listdir()
