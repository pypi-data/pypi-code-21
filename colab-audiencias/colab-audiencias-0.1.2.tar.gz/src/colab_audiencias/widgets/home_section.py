from colab.widgets.widget_manager import Widget
from django.template.loader import render_to_string
from colab_audiencias.models import AudienciasRoom
from itertools import chain
import datetime


class AudienciasHomeSectionWidget(Widget):
    name = 'Audiencias Interativas home section'
    template = 'widgets/audiencias_home_section.html'

    def generate_content(self, **kwargs):
        context = kwargs.get('context')
        audiencias_today = AudienciasRoom.objects.filter(
            date__startswith=datetime.date.today(), is_visible=True)
        live_videos = audiencias_today.filter(youtube_status=1)
        history_videos = audiencias_today.filter(youtube_status=2)
        agenda_videos = audiencias_today.filter(
            youtube_status=0, reunion_status__in=[2, 3]).order_by('date')

        if audiencias_today.count() < 10:
            empty_cards_count = 10 - audiencias_today.count()
            next_agenda = AudienciasRoom.objects.filter(
                youtube_status=0, is_visible=True,
                reunion_status__in=[2, 3]).exclude(
                date__startswith=datetime.date.today()).exclude(
                date__lte=datetime.datetime.now()).order_by(
                'date')[:empty_cards_count]
            agenda_videos = list(chain(agenda_videos, next_agenda))

        context['live_videos'] = live_videos
        context['history_videos'] = history_videos
        context['agenda_videos'] = agenda_videos
        self.content = render_to_string(self.template, context)
        return kwargs.get('context')
