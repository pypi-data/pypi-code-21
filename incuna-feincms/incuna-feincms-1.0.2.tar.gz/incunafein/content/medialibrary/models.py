from django.template.loader import render_to_string
from feincms.content.medialibrary.models import MediaFileContent as BaseMediaFileContent


class MediaFileContent(BaseMediaFileContent):
    """Add some region specific rendering options."""
    class Meta(BaseMediaFileContent.Meta):
        abstract = True

    def render(self, **kwargs):
        ctx = {'content': self}
        ctx.update(kwargs)
        template_names = [
            'content/mediafile/%s/%s_%s.html' % (self.region, self.mediafile.type, self.type),
            'content/mediafile/%s/%s.html' % (self.region, self.mediafile.type),
            'content/mediafile/%s/%s.html' % (self.region, self.type),
            'content/mediafile/%s/default.html' % self.region,

            'content/mediafile/%s_%s.html' % (self.mediafile.type, self.type),
            'content/mediafile/%s.html' % self.mediafile.type,
            'content/mediafile/%s.html' % self.type,
            'content/mediafile/default.html',
        ]
        ctx_inst = kwargs.get('context')
        return render_to_string(template_names, ctx, context_instance=ctx_inst)
