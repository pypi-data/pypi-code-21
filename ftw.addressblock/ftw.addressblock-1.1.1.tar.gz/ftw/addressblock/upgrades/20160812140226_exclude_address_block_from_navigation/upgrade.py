from ftw.upgrade import UpgradeStep


class ExcludeAddressBlockFromNavigation(UpgradeStep):
    """Exclude address block from navigation and make it not searchable.
    """

    def __call__(self):
        self.install_upgrade_profile()
