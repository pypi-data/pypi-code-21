import git
import os.path

from src.config.models.gardener_config import GardenerConfig


def git_init(gardener_config: GardenerConfig):
    repo_directory = os.path.join(gardener_config.destination, gardener_config.project_name)
    print("git_init: {0}", repo_directory)
    # Initialize the repository, first commit
    current_repo = git.Repo.init(repo_directory)
    #current_repo.index.add()
    current_repo.index.commit("Initial commit")
    # TODO: Get the remote repo and push if it exists

    return current_repo