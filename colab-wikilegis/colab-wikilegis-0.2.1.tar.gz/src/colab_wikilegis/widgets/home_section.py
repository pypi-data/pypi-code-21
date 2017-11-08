from colab.widgets.widget_manager import Widget
from django.template.loader import render_to_string
from colab_wikilegis.models import WikilegisBill


class WikilegisHomeSectionWidget(Widget):
    name = 'Collaboration Graph'
    template = 'widgets/wikilegis_home_section.html'

    def generate_content(self, **kwargs):
        context = kwargs.get('context')
        wikilegis_data = WikilegisBill.objects.exclude(status='draft')
        wikilegis_data = wikilegis_data.order_by('-status', '-modified')[:10]
        context['wikilegis_data'] = wikilegis_data

        self.content = render_to_string(self.template, context)
        return kwargs.get('context')
