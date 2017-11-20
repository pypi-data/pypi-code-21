# -*- coding: utf-8 -*-
from logging import getLogger
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

logger = getLogger(__name__)


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller"""
        return [
            'quaive.app.taxonomy:uninstall',
        ]


def create_taxonomy_app(
        id='document-browser',
        title=u'Document browser',
        app_parameters='{"vocabulary": "taxonomy"}',
        css_class='document-browser'):
    ''' Create an app for Taxonomy (wanted for Quaive)
    '''
    portal = api.portal.get()
    apps = portal.apps
    if id not in apps:
        api.content.create(
            container=apps,
            type='ploneintranet.layout.app',
            title=title,
            id=id,
            safe_id=False,
            app='@@app-document-browser',
            css_class=css_class,
            app_parameters=app_parameters,
        )
    app = getattr(apps, id)
    if api.content.get_state(app) == 'published':
        return
    try:
        api.content.transition(app, to_state='published')
    except:
        logger.exception('Cannot publish the app: %r', app)


def post_install(context):
    """Post install script"""
    create_taxonomy_app()


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
