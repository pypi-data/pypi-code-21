from django.shortcuts import get_object_or_404

from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse

from molo.yourwords.forms import CompetitionEntryForm
from molo.yourwords.models import YourWordsCompetition


class CompetitionEntry(CreateView):
    form_class = CompetitionEntryForm
    template_name = 'yourwords/your_words_competition_entry.html'

    def get_context_data(self, *args, **kwargs):
        context = super(
            CompetitionEntry, self).get_context_data(*args, **kwargs)
        competition = get_object_or_404(
            YourWordsCompetition, slug=self.kwargs.get('slug'))
        context.update({'competition': competition})
        return context

    def get_success_url(self):
        return reverse(
            'molo.yourwords:thank_you',
            args=[self.object.competition.slug])

    def form_valid(self, form):
        competition = get_object_or_404(
            YourWordsCompetition, slug=self.kwargs.get('slug'))
        form.instance.competition = (
            competition.get_main_language_page().specific)
        form.instance.user = self.request.user
        return super(CompetitionEntry, self).form_valid(form)


class ThankYouView(TemplateView):
    template_name = 'yourwords/thank_you.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ThankYouView, self).get_context_data(*args, **kwargs)
        competition = get_object_or_404(
            YourWordsCompetition, slug=self.kwargs.get('slug'))
        context.update({'competition': competition})
        return context
