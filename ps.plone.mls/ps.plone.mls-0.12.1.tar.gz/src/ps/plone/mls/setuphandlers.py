# -*- coding: utf-8 -*-
"""Post install import steps for ps.plone.mls."""

# python imports
import pkg_resources

# zope imports
from Products.CMFPlone.interfaces import INonInstallable
from Products.GenericSetup.interfaces import IProfileImportedEvent
from plone import api
from zope.component import adapter
from zope.interface import implementer

# local imports
from ps.plone.mls import config


ADD_ONS = [
    'ps.plone.fotorama',
]


@implementer(INonInstallable)
class HiddenProfiles(object):
    """Define hidden GenericSetup profiles."""

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'ps.plone.mls:testfixture',
            'ps.plone.mls:uninstall',
        ]


@adapter(IProfileImportedEvent)
def handle_profile_imported_event(event):
    """Update 'last version for profile' after a full import."""
    qi = api.portal.get_tool(name='portal_quickinstaller')
    if not qi.isProductInstalled(config.PROJECT_NAME):
        return

    if event.profile_id == 'profile-plone.app.upgrade.v50:to50alpha3':
        setup = api.portal.get_tool(name='portal_setup')
        setup.runAllImportStepsFromProfile(config.INSTALL_PROFILE)


def install_add_ons(context):
    """Install additional available add-ons."""
    if not context.readDataFile('plone.mls.listing_various.txt'):
        return

    setup = api.portal.get_tool(name='portal_setup')
    quickinstaller = api.portal.get_tool(name='portal_quickinstaller')
    for item in ADD_ONS:
        try:
            pkg_resources.get_distribution(item)
        except pkg_resources.DistributionNotFound:
            continue
        # Only install add-ons which are not installed yet.
        if not quickinstaller.isProductInstalled(item):
            if quickinstaller.isProductInstallable(item):
                try:
                    profile = 'profile-{0}:default'.format(item)
                    setup.runAllImportStepsFromProfile(profile)
                except AttributeError:
                    pass
