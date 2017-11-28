from colab.widgets.widget_manager import Widget
from django.template.loader import render_to_string
from colab_discourse.models import DiscourseTopic


class DiscourseHomeSectionWidget(Widget):
    name = 'Discourse Home Section'
    template = 'widgets/discourse_home_section.html'

    def generate_content(self, **kwargs):
        context = kwargs.get('context')
        discourse_data = DiscourseTopic.objects.filter(visible=True)
        discourse_data = discourse_data.order_by('-last_posted_at')
        context['discourse_data'] = discourse_data[:10]

        self.content = render_to_string(self.template, context)
        return kwargs.get('context')
