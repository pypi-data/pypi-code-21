from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from cms.menu_bases import CMSAttachMenu
from menus.base import Menu, NavigationNode
from menus.menu_pool import menu_pool


class CollectionMenu(CMSAttachMenu):
    name = _("Collection menu")

    def get_nodes(self, request):
        """
        This method is used to build the menu tree.
        """
        from .models import Collection
        nodes = []
        for collection in Collection.objects.filter(published=True):
            node = NavigationNode(
                collection.title,
                collection.get_absolute_url(),
                collection.slug
            )
            nodes.append(node)
        return nodes

menu_pool.register_menu(CollectionMenu)