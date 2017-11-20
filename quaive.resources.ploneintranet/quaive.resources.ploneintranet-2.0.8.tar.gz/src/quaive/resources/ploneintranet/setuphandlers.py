# -*- coding: utf-8 -*-
from logging import getLogger
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

logger = getLogger(__name__)


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'quaive.resources.ploneintranet:uninstall',
        ]


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def post_uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
