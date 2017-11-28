from colab.widgets.widget_manager import Widget
from django.template.loader import render_to_string
from colab_pauta.models import PautaAgenda


class PautaHomeSectionWidget(Widget):
    name = 'Collaboration Graph'
    template = 'widgets/pauta_home_section.html'

    def generate_content(self, **kwargs):
        context = kwargs.get('context')
        pauta_data = PautaAgenda.objects.all()
        pauta_data = pauta_data.order_by('-end_date')[:10]
        context['pauta_data'] = pauta_data

        self.content = render_to_string(self.template, context)
        return kwargs.get('context')
