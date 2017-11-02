from fabric.operations import prompt
from fabric.tasks import Task

from eryx_deploy.utils.interactive_console import InteractiveConsole


class MakeReleaseTask(Task):
    """
    NOTE: Untested. Use at your own risk!
    """

    name = 'make_release'

    def __init__(self, local_vcs):
        self._local_vcs = local_vcs
        super(MakeReleaseTask, self).__init__()

    def run(self):
        ready_for_release = InteractiveConsole.yes_or_no(
            "Are you currently in 'dev' branch with everything merged and pulled (clean tree!), "
            "ready to make a release?",
            default=False)

        if not ready_for_release:
            InteractiveConsole.abort("Prepare everything and try again!")

        self._local_vcs.fetch()

        InteractiveConsole.show_info("Latest git tag: ")
        self._local_vcs.get_latest_tag()

        version = prompt('Version: ', validate='^\d{1,3}[.]\d{1,2}[.]\d{1,2}')

        self._local_vcs.merge_dev_into_master()

        self._local_vcs.tag_version(version)

        self._local_vcs.push(include_tags=True)

        self._local_vcs.checkout_dev()
