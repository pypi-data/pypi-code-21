# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

import pkg_resources


try:
    pkg_resources.get_distribution('plone.app.mosaic')
    HAS_MOSAIC = True
except pkg_resources.DistributionNotFound:  # pragma: no cover
    HAS_MOSAIC = False


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'collective.sortedlisting:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.
    if HAS_MOSAIC:
        context.runAllImportStepsFromProfile(
            'profile-collective.sortedlisting:mosaic')


def post_install_mosaic(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
