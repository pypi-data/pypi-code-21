from django.db import models
from colab.plugins import helpers
from datetime import date


class PautaAgenda(models.Model):

    id = models.IntegerField(primary_key=True)
    initial_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=100)
    votes_count = models.IntegerField(default=0)
    participants_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Pauta Agenda"
        verbose_name_plural = "Pauta Agendas"

    def __str__(self):
        return self.title

    def get_url(self):
        prefix = helpers.get_plugin_prefix('colab_pauta', regex=False)
        return '/{}pauta/{}'.format(prefix, self.id)

    @property
    def is_closed(self):
        return date.today() > self.end_date


class PautaGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    agenda = models.ForeignKey(PautaAgenda, related_name='groups')
    theme_slug = models.CharField(max_length=250)
    theme_name = models.CharField(max_length=250)

    def __str__(self):
        return self.theme_slug
