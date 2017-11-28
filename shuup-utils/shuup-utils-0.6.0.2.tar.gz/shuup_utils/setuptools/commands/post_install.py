from setuptools.command.develop import develop

from shuup_utils.setuptools.commands.build_static import get_default_yarn_dir_path
from shuup_utils.setuptools.commands.build_static import build_static


# noinspection PyAttributeOutsideInit
class PostInstallCommand(develop):
    def initialize_options(self):
        self.yarn_dir_path = get_default_yarn_dir_path(command=self)
    
    def run(self):
        build_static(self.yarn_dir_path)
