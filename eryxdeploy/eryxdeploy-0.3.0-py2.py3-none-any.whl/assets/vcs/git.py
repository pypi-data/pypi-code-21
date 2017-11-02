class Git(object):
    def __init__(self, client_machine, remote_url):
        self._client_machine = client_machine
        self._remote_url = remote_url

    def clone_project(self):
        with self._client_machine.cd_project():
            return self._client_machine.run('git clone %s .' % self._remote_url,
                                            on_fail_msg="Could not clone repository! Please make sure you have added "
                                                        "a Deploy Key in Gitlab to allow cloning from '%s'."
                                                        % self._client_machine.hostname())

    def fetch(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git fetch --tags')

    def pull(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git pull')

    def push(self, include_tags=False):
        with self._client_machine.cd_project():
            self._client_machine.run('git push')

            if include_tags:
                self._client_machine.run('git push --tags')

    def get_latest_tag(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git describe --abbrev=0')

    def checkout_master(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git checkout master')

    def checkout_dev(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git checkout dev')

    def merge_dev_into_current_branch(self):
        with self._client_machine.cd_project():
            self._client_machine.run('git merge dev')

    def merge_dev_into_master(self):
        self.checkout_master()
        self.pull()
        self.merge_dev_into_current_branch()

    def tag_version(self, version):
        with self._client_machine.cd_project():
            self._client_machine.run('git tag -a \'%s\' -m \'Release version %s\'' % (version, version))
