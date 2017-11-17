"""
Module that is responsible for syncing the data files across the storage modules. Initial version of this assumes that
git is the storage module, but there is not a reason why another storage implementation cannot be used in the future.

Current implementation assumes that git is initialized in the project directory, and has a remote named origin.
"""
import git

from autology import topics
from autology.configuration import get_configuration_root, add_default_configuration, get_configuration

# The current repository that all of the files will be stored/modified in.
_repo = None


def register_plugin():
    """Initializes the git module for the directory that the configuration file is currently being stored in."""
    topics.Application.INITIALIZE.subscribe(_initialization)

    add_default_configuration('git', {
        'enabled': False,
        'remote': 'origin',
        'refspec': 'master',
    })


def _initialization():
    """Initialize storage engine by querying configuration, and then file system."""
    global _repo

    configuration = get_configuration()

    if not configuration.git.enabled:
        return

    # If creating the git repository fails, then initialize a new repository
    try:
        _repo = git.Repo(str(get_configuration_root()))
    except git.InvalidGitRepositoryError:
        _repo = git.Repo.init(str(get_configuration_root()))

    try:
        # Add the subscriptions for working with local storage
        topics.Storage.FILE_ADDED.subscribe(_file_added)
        topics.Storage.FINISHED_MODIFICATIONS.subscribe(_finished_changes)

        # Test status of remote accessibility
        if configuration.git.remote:
            origin_remote = _repo.remote(name=configuration.git.remote)
            origin_remote.fetch()

            # And then add subscriptions for handling remotes
            topics.Storage.PULL_CHANGES.subscribe(_pull_changes)
            topics.Storage.PUSH_CHANGES.subscribe(_push_changes)

    except (git.GitCommandError, ValueError):
        # Command error is raised when the remote is not accessible and attribute error is raised when the remote is not
        # defined.
        pass


def _file_added(file):
    """Add file to the repository"""
    _repo.index.add([str(file)])


def _finished_changes(message):
    """Commit the changes to the repository."""
    _repo.index.commit(message)


def _pull_changes():
    """Pull changes from the repository and do a merge"""
    configuration = get_configuration()
    _repo.remotes[configuration.git.remote].pull(configuration.git.refspec)


def _push_changes():
    """Push changes to the repository."""
    configuration = get_configuration()
    _repo.remotes[configuration.git.remote].push(configuration.git.refspec)
