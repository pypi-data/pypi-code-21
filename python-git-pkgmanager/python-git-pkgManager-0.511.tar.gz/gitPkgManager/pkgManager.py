"""GitPackageManager module.

This module is interact with github & fetching data directly
to any project without actually install it in the system using pip.

Version:: Alpha: v0.4
"""

from git import Repo
import subprocess
import os


class GitArgsNotAcceptableException(Exception):
    pass


class GitCloningException(Exception):
    pass


class GitPackageManager(object):

    def __init__(self, ssh_repo_url: str,
                 save_path: str,
                 use_branch: str = "master",
                 ssh_key_path: str = "",
                 use_commit: str = "",
                 always_sync: bool = False) -> None:

        repo_name: str = os.path.basename(ssh_repo_url).split(".")[0]
        self.ssh_repo_url = ssh_repo_url
        self.ssh_key_path = ssh_key_path
        self.full_dir_path: str = os.path.join(save_path, repo_name)
        self.always_sync = always_sync
        self.commit_hash = use_commit
        self.branch = use_branch
        try:
            self._clone_package()
        except Exception as err:
            raise GitCloningException(str(err))

        self._check_rules()

    def _clone_package(self) -> None:
        """Cloning package from github.
        """

        if not os.path.isdir(self.full_dir_path):
            if self.ssh_key_path != "":
                ssh_key_path = {"GIT_SSH_COMMAND": "ssh -i " + self.ssh_key_path}
                Repo.clone_from(self.ssh_repo_url, self.full_dir_path, env=ssh_key_path)
            else:
                Repo.clone_from(self.ssh_repo_url, self.full_dir_path)

    def _check_rules(self) -> None:
        """Checking for rules to apply on the imported library
        """

        if self.always_sync and self.commit_hash != "":
            raise GitArgsNotAcceptableException("`always_sync` & `use_commit` Cannot be assigned "
                                                "together.")

        if self.branch != "master":
            command = f"""cd {self.full_dir_path}; git checkout -b {self.branch}; git pull
                            origin {self.branch}
                       """
            subprocess.run(command, shell=True)

        if os.path.isdir(self.full_dir_path) and self.always_sync:
            command = f"cd {self.full_dir_path}; git pull origin {self.branch}"
            subprocess.run(command, shell=True)

        if self.commit_hash != "":
            command = f"cd {self.full_dir_path}; git checkout {self.commit_hash}"
            subprocess.run(command, shell=True)
