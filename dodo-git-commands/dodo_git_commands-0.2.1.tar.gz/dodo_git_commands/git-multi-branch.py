# noqa
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import bordered
import os
from plumbum.cmd import git
from plumbum import local


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        parser.add_argument('--checkout')
        parser.add_argument('--prune', action='store_true')

    def handle_imp(self, checkout, prune, **kwargs):  # noqa
        src_dir = self.get_config('/ROOT/src_dir')
        for repo in (os.listdir(src_dir) + ['.']):
            repo_dir = os.path.join(src_dir, repo)
            if os.path.exists(os.path.join(repo_dir, '.git')):
                with local.cwd(repo_dir):
                    if prune:
                        print(git('remote', 'prune', 'origin'))

                    print(bordered(repo))
                    if checkout:
                        try:
                            git('checkout', checkout)
                        except:
                            print('Could not checkout to %s' % checkout)
                            pass
                    print(git('rev-parse', '--abbrev-ref', 'HEAD'))
