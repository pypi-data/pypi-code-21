from ftw.upgrade import UpgradeStep


class EnableMapForAnonymous(UpgradeStep):
    """Enable map for anonymous.
    """

    def __call__(self):
        self.install_upgrade_profile()
