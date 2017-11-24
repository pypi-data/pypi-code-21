# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import SitemapQueryBuilder
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from cStringIO import StringIO
from collective.superfish.interfaces import ISuperfishSettings
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.viewlets import common
from plone.registry.interfaces import IRegistry
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate


def _render_sections_cachekey(fun, self):
    key = StringIO()
    print >> key, self.__class__
    print >> key, getToolByName(aq_inner(self.context), 'portal_url')()
    print >> key, self.request.get('LANGUAGE', 'de')

    catalog = getToolByName(self.context, 'portal_catalog')
    counter = catalog.getCounter()
    print >> key, counter
    print >> key, aq_inner(self.context).getPhysicalPath()

    user = getSecurityManager().getUser()
    roles = user.getRolesInContext(aq_inner(self.context))
    print >> key, roles

    return key.getvalue()


class VirtualCatalogBrain(object):
    """wraps an portal_action actioninfo into a fake catalog brain that can
    be used as item in the dictiontary returned by
    plone.app.layout.navigation.navtree.buildFolderTree
    """

    def __init__(self, action):
        self.url = action['url']
        self.Title = action['title']
        self.Description = action['description']
        self.exclude_from_nav = not (action['available'] and action['allowed'])
        self.id = "action-%s" % action['id'].replace('_', '-')

    def getURL(self):
        return self.url


class SuperFishQueryBuilder(SitemapQueryBuilder):
    """Build a folder tree query suitable for a dropdownmenu
    """

    def __init__(self, context):
        super(SuperFishQueryBuilder, self).__init__(context)

        portal_state = getMultiAdapter(
            (context, context.REQUEST), name=u'plone_portal_state')
        root = portal_state.navigation_root_path()

        self.query['path']['query'] = root


class SuperFishViewlet(common.ViewletBase):

    index = ViewPageTemplateFile('sections.pt')

    # monkey patch this if you want to use collective.superfish together with
    # global_sections, need another start level or menu depth.
    menu_id = 'portal-globalnav'

    # See http://wiki.python.org/moin/EscapingHtml
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
        ">": "&gt;",
        "<": "&lt;",
    }

    # this template is used to generate a single menu item.
    _menu_item = u"""
    <li id="%(menu_id)s-%(id)s"%(classnames)s
      ><a href="%(url)s" title="%(description)s">
        %(title)s
    </a>%(submenu)s </li>"""

    # this template is used to generate a menu container
    _submenu_item = u"""\n<ul%(id)s class="%(classname)s" data-pat-superfish='%(patternoptions)s'>%(menuitems)s</ul>"""  # noqa

    def __init__(self, *args):
        super(SuperFishViewlet, self).__init__(*args)

        context_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_context_state')
        portal_state = getMultiAdapter(
            (self.context, self.request), name=u'plone_portal_state')

        self.current_url = context_state.current_page_url()
        self.site_url = portal_state.portal_url()
        self.navigation_root_path = portal_state.navigation_root_path()
        registry = queryUtility(IRegistry)
        self.settings = registry.forInterface(
            ISuperfishSettings, prefix='superfish', check=False)

    def _build_navtree(self):
        # we generate our navigation out of the sitemap. so we can use the
        # highspeed navtree generation, and use it's caching features too.
        query = SuperFishQueryBuilder(self.context)()
        query['path']['depth'] = self.settings.menu_depth
        query['path']['query'] = self.navigation_root_path

        # no special strategy needed, so i kicked the INavtreeStrategy lookup.
        return buildFolderTree(self.context, obj=self.context, query=query)

    def update(self):
        self.data = self._build_navtree()

        if self.settings.add_portal_tabs:
            self._addActionsToData()

    def _actions(self):
        context = aq_inner(self.context)
        context_state = getMultiAdapter((context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions('portal_tabs')

        return actions or []

    def _addActionsToData(self):
        """inject the portal_actions before the rest of the navigation
        """
        actions = self._actions()
        actions.reverse()

        # XXX maybe we can use some ideas of
        # CMFPlone.browser.navigation.CatalogNavigationTabs
        # to mark currentItems (or GlobalSectionsViewlet in
        # plone.app.layout.viewlets.common)
        for actionInfo in actions:
            self.data['children'].insert(
                0,
                {'item': VirtualCatalogBrain(actionInfo),
                 'depth': 1, 'children': [],
                 'currentParent': False, 'currentItem': False}
            )

    def html_escape(self, text):
        """Produce entities within text."""
        # XXX maybe we should use a static method here
        return "".join(self.html_escape_table.get(c, c) for c in text)

    def portal_tabs(self):
        """We do not want to use the template-code any more.
           Python code should speedup rendering."""

        def submenu(items, menu_id=None, menu_level=0, menu_classnames='',
                    patternoptions=''):
            # unsure this is needed any more...
            # if self.menu_depth>0 and menu_level>self.menu_depth:
            #    # finish if we reach the maximum level
            #    return

            i = 0
            s = []

            # exclude nav items
            items = [item for item in items if not item['item'].exclude_from_nav]  # noqa

            if not items:
                return ''

            for item in items:
                first = i == 0
                i += 1
                last = i == len(items)

                s.append(menuitem(item, first, last, menu_level))

            return self._submenu_item % dict(
                id=menu_id and u" id=\"%s\"" % (menu_id) or u"",
                menuitems=u"".join(s),
                classname=u"navTreeLevel%d %s" % (menu_level, menu_classnames),
                patternoptions=patternoptions)

        def menuitem(item, first=False, last=False, menu_level=0):
            classes = []

            if first:
                classes.append('firstItem')
            if last:
                classes.append('lastItem')
            if item['currentParent']:
                classes.append('navTreeItemInPath')
            if item['currentItem']:
                classes.append('selected')
            brain = item['item']

            if type(brain) == VirtualCatalogBrain:
                # translate our portal_actions and use their id instead of the
                # url
                title = translate(brain.Title, context=self.request)
                desc = translate(brain.Description, context=self.request)
                item_id = brain.id
            else:
                title = safe_unicode(brain.Title)
                desc = safe_unicode(brain.Description)
                item_id = brain.getURL()[len(self.site_url):]

            item_id = item_id.strip('/').replace('/', '-')

            return self._menu_item % dict(
                menu_id=self.menu_id,
                id=item_id,
                level=menu_level,
                title=self.html_escape(title),
                description=self.html_escape(desc),
                url=item['item'].getURL(),
                classnames=len(classes) and u' class="%s"' % (" ".join(classes)) or u"",  # noqa
                submenu=submenu(item['children'],
                                menu_level=menu_level + 1) or u"")

        if self.data:
            return submenu(
                self.data['children'],
                menu_id=self.menu_id,
                menu_classnames=u"plone-nav plone-navbar-nav pat-superfish sf-menu",  # noqa
                patternoptions=self.settings.superfish_options)

    # @ram.cache(_render_sections_cachekey)
    def render(self):
        return self.index()
