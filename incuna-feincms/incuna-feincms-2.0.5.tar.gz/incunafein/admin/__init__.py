import json

from feincms.module.page.forms import PageAdminForm as PageAdminFormOld
from feincms.module.page.modeladmins import PageAdmin as PageAdminOld
from feincms.module.page.models import Page
from django.conf import settings
from django.conf.urls import patterns
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe


class RefreshingParentForeignKeyRawIdWidget(ForeignKeyRawIdWidget):
    """Adds the javascript to force-refresh the template field when the parent field loses focus"""
    class Media:
        js = (settings.STATIC_URL + 'incunafein/scripts/get_templates.js',)


def get_valid_templates(instance=None, parent=None):
    """
        Looks up the list of valid templates for this instance, and its parent.

        This is achivined by looking up through the parent tree for a page where the template enforces child templates,
        or the root template list if none is found

        @return dict: dict containing all the templates valid for this instance
    """
    # copy of all the available templates
    templates = Page._feincms_templates.copy()
    check_pages = None

    if parent and not isinstance(parent, Page):
        parent = Page.objects.get(pk=parent)

    if parent:
        check_pages = (parent.get_ancestors(ascending=True) | Page.objects.filter(pk = parent.pk)) or [parent,]
    elif instance:
        check_pages = instance.get_ancestors(ascending=True)

    if check_pages:
        for page in check_pages:
            if hasattr(page.template, 'children'):
                templates = dict([(templates[child].key, templates[child]) for child in page.template.children])

    # remove templates that are defined as children within the current set
    for t in templates.values():
        if hasattr(t, 'children') and t.children:
            for c in t.children:
                if c in templates:
                    del(templates[c])

    return templates


class PageAdminForm(PageAdminFormOld):
    """
    Adds hooks into the admin form to allow the munging of the template list.

    cf http://www.marcofucci.com/tumblelog/17/jun/2010/customizing-feincms-part-2/
    """
    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        parent = kwargs.get('initial', {}).get('parent')
        if not parent and instance:
            parent = instance.parent

        templates = get_valid_templates(instance, parent)

        choices = []
        for key, template in templates.items():
            if template.preview_image:
                choices.append((template.key,
                    mark_safe(u'<img src="%s" alt="%s" /> %s' % (
                        template.preview_image, template.key, template.title))))
            else:
                choices.append((template.key, template.title))

        self.fields['template_key'].choices = choices
        if choices:
            self.fields['template_key'].default = choices[0][0]

        self.fields['parent'].widget = RefreshingParentForeignKeyRawIdWidget(self.fields['parent'].widget.rel)


class PageAdmin(PageAdminOld):
    form = PageAdminForm

    def get_templates(self, request):
        """Ajax view for getting a JSON list of the avaliable templates,
        (using the get_valid_templates function above)
        """

        if 'page_id' in request.POST and request.POST['page_id']:
            parent = get_object_or_404(Page, pk=request.POST['page_id'])
        else:
            parent = None
        valid_templates = get_valid_templates(parent=parent)
        if valid_templates:
            result = [{'id':key, 'desc':unicode(valid_templates[key]),} for key in valid_templates.keys()]
        else:
            result = list()

        return HttpResponse(json.dumps(result), mimetype="application/javascript")

    def get_urls(self):
        """URL hooks to add the above view at /admin/page/page/get_templates/"""

        urls = super(PageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^get_templates/?$', self.admin_site.admin_view(self.get_templates))
        )
        return my_urls + urls

# Change the field order so the parent is first
try:
    admin_fields = PageAdmin.fieldsets[0][1]['fields']
    if 'parent' in admin_fields and 'template_key' in admin_fields:
        admin_fields.remove('parent')
        admin_fields.insert(admin_fields.index('template_key'), 'parent')
except IndexError:
    pass
