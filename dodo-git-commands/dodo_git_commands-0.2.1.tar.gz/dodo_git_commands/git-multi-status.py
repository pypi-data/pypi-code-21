# noqa
from dodo_commands.system_commands import DodoCommand
from dodo_commands.framework.util import bordered
import os
from plumbum.cmd import git
from plumbum import local


class Command(DodoCommand):  # noqa
    help = ""

    def add_arguments_imp(self, parser):  # noqa
        pass

    def handle_imp(self, **kwargs):  # noqa
        src_dir = self.get_config('/ROOT/src_dir')
        for repo in (os.listdir(src_dir) + ['.']):
            repo_dir = os.path.join(src_dir, repo)
            if os.path.exists(os.path.join(repo_dir, '.git')):
                with local.cwd(repo_dir):
                    status = git('status')
                    files_to_commit = (
                        'nothing to commit, working directory clean' not in status
                    )
                    diverged = (
                        'Your branch is up-to-date with' not in status
                    )

                    if files_to_commit or diverged:
                        print(bordered(repo))
                        print(git('rev-parse', '--abbrev-ref', 'HEAD')[:-1])
                        if files_to_commit:
                            print("Files to commit")
                        if diverged:
                            print("Branch has diverged")
                        print(
                            "cd %s; %s&\n" % (
                                repo_dir,
                                'git gui' if files_to_commit else 'gitk'
                            )
                        )
