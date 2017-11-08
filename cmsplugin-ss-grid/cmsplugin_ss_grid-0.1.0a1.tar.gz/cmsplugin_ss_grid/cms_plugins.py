from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin
from cms.plugin_pool import plugin_pool
from cms.plugin_base import CMSPluginBase

from .models import Container, ContainerCell
from .forms import ContainerPluginForm


class ContainerPlugin(CMSPluginBase):
    model = Container
    name = _('Container')
    module = _('Layout')
    render_template = 'cmsplugin_ss_grid/container.html'
    allow_children = True
    child_classes = ['ContainerCellPlugin']
    form = ContainerPluginForm


    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'placeholder': placeholder
        })
        return context

    def save_model(self, request, obj, form, change):
        response = super(ContainerPlugin, self).save_model(request, obj, form,
                                                      change)
        for x in range(int(form.cleaned_data['create'])):
            cell = ContainerCell(
                parent=obj, placeholder=obj.placeholder, language=obj.language,
                size_mobile=form.cleaned_data['mobile_size'],
                size_desktop=form.cleaned_data['desktop_size'],
                position=CMSPlugin.objects.filter(parent=obj).count(),
                plugin_type=ContainerCellPlugin.__name__
            )
            cell.save()
        return response

    @classmethod
    def get_parent_classes(cls, slot, page, instance=None):
        # HACK prevent this plugin being added as the child of any other
        if not instance:
            return []
        return [True]


class ContainerCellPlugin(CMSPluginBase):
    model = ContainerCell
    name = _('Cell')
    module = _('Layout')
    render_template = 'cmsplugin_ss_grid/cell.html'
    allow_children = True

    require_parent = True
    parent_classes = ['ContainerPlugin']


plugin_pool.register_plugin(ContainerPlugin)
plugin_pool.register_plugin(ContainerCellPlugin)
