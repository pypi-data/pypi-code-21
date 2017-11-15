from django.db import models
import mptt


class Navigation(models.Model):
    """Navigation item. uses mptt so can have sub navigation."""

    page = models.ForeignKey('page.Page', null=True, blank=True, help_text="Leave blank to create a top level navigation.")
    title = models.CharField(max_length=250, null=True, blank=True, help_text="Leave blank to use the page title.")
    url = models.URLField(max_length=250, null=True, blank=True, help_text="Set either the page or url, not both.")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', help_text="Leave blank to create a top level navigation.")
    dom_id = models.CharField(max_length=250, null=True, blank=True, help_text="This is used to identify the navigation and must be set for a top level navigation.")
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
