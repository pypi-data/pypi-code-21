from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import SlidePlugin, CarouselPlugin


def js_boolean(prop):
    return 'true' if prop else 'false'


@plugin_pool.register_plugin
class CarouselPluginPublisher(CMSPluginBase):
    model = CarouselPlugin
    name = _('Carousel')
    module = "Ri+"
    render_template = 'ripiu/cmsplugin_rototalc/carousel.html'
    allow_children = True
    child_classes = ['SlidePluginPublisher']
    fieldsets = (
        ('', {
            'fields': (
                'name',
                ('height', 'slide_margin'),
            )
        }), (
            _('Slick configuration'), {
                'fields': (
                    ('show_arrows', 'dots', 'autoplay'),
                    ('autoplay_speed', 'speed'),
                    ('slides_to_show', 'center_mode'),
                    ('focus_on_select', 'infinite', 'variable_width'),
                )
            }
        )
    )

    def render(self, context, instance, placeholder):
        import json
        context = super(CarouselPluginPublisher, self).render(
            context, instance, placeholder
        )
        slick_conf = {
            'autoplay': instance.autoplay,
            'autoplaySpeed': instance.autoplay_speed,
            'arrows': instance.show_arrows,
            'centerMode': instance.center_mode,
            'dots': instance.dots,
            'infinite': instance.infinite,
            'speed': instance.speed,
            'vertical': False,  # instance.vertical,
            'slidesToShow': instance.slides_to_show,
            'focusOnSelect': instance.focus_on_select,
            'variableWidth': instance.variable_width,
            'cssEase': 'ease',
            'useCSS': True,
        }
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'cid': "rototalc-carousel-%s" % instance.name,
            'conf': json.dumps(slick_conf),
        })
        return context


@plugin_pool.register_plugin
class SlidePluginPublisher(CMSPluginBase):
    model = SlidePlugin
    name = _('Slide')
    module = "Ri+"
    render_template = 'ripiu/cmsplugin_rototalc/slide.html'
    allow_children = True
    parent_classes = ['CarouselPluginPublisher']
    require_parent = True

    def render(self, context, instance, placeholder):
        context = super(SlidePluginPublisher, self).render(
            context, instance, placeholder
        )
        carousel = instance.parent.get_bound_plugin()
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'slider_height': carousel.height,
            'horizontal_margin': carousel.slide_margin,
        })
        return context
