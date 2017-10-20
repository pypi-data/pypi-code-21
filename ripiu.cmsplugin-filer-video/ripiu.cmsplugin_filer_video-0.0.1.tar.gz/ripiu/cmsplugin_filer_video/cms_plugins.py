from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _
from .models import FilerVideoPluginModel

@plugin_pool.register_plugin
class FilerVideoPluginPublisher(CMSPluginBase):
    model = FilerVideoPluginModel
    name = _("Self hosted video")
    module = 'Filer'
    render_template = 'ripiu/cmsplugin_filer_video/video.html'
    allow_children = True
    fieldsets = (
        ('', {
            'fields': (
                "title",
                "video_file",
                "poster",
            )
        }), (_('Size'), {
            'fields': (
                ("width", "height"),
            )
        }), (_('Advanced'), {
            'fields': (
                ("autoplay", "controls"),
                ("loop", "muted"),
            )
        })
    )
    
    def render(self, context, instance, placeholder):
        context = super(FilerVideoPluginPublisher, self).render(context, instance, placeholder)
        return context
