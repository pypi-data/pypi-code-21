from django.db import models
#from feincms.module.page.models import ActiveAwareContentManagerMixin
import mptt

#class NavigationManager(models.Manager, ActiveAwareContentManagerMixin):
#    """
#    Manager to make the Navigation objects behave like Page objects (in terms of navigation)
#    """


#    def toplevel_navigation(self):
#        return self.in_navigation().filter(parent__isnull=True)

class Navigation(models.Model):
    """Navigation item. uses mptt so can have sub navigation."""

    page = models.ForeignKey('page.Page', null=True, blank=True, help_text="Leave blank to create a top level navigation.")
    title = models.CharField(max_length=250, null=True, blank=True, help_text="Leave blank to use the page title.")
    url = models.URLField(verify_exists=False, max_length=250, null=True, blank=True, help_text="Set either the page or url.")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', help_text="Leave blank to create a top level navigation.")
    dom_id = models.CharField(max_length=250, null=True, blank=True, help_text="This must be set for a top level navigation.")
    css_class = models.CharField(max_length=250, null=True, blank=True)

    #objects = NavigationManager()

    class Meta:
        ordering = ['tree_id', 'lft']

    def __unicode__(self):
        return u"%s" % (self.title or self.page or self.url or self.dom_id,)

    def get_absolute_url(self):
        return u"%s" % (self.page and self.page.get_absolute_url() or self.url,)

    def get_css_class(self):
        return u"%s" % (self.css_class or (self.page and  self.page.slug))


mptt.register(Navigation)

