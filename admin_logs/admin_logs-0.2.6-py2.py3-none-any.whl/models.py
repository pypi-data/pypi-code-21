# common
import logging

# django
from django.db import models
from django.template.defaultfilters import linebreaksbr

# other
from picklefield.fields import PickledObjectField


class Request(models.Model):

    CT_NOT_SET = 0
    CT_PC = 1
    CT_MOBILE = 2
    CT_TABLET = 3
    CT_BOT = 4

    LEVEL_CHOICES = (
        (logging.CRITICAL, 'CRITICAL'),
        (logging.ERROR, 'ERROR'),
        (logging.WARNING, 'WARNING'),
        (logging.INFO, 'INFO'),
        (logging.DEBUG, 'DEBUG'),
        (logging.NOTSET, 'NOTSET'),
    )

    hash = models.CharField(max_length=100, unique=True, verbose_name="Hash",
                            help_text="Unique identifier of request. "
                                      "Should be unique accross all requests.")

    start_date = models.DateTimeField(verbose_name="Request start time", db_index=True)
    duration = models.FloatField(verbose_name="Duration in milleseconds")
    max_level = models.SmallIntegerField(verbose_name="Max level", db_index=True, default=logging.NOTSET,
                                         choices=LEVEL_CHOICES)

    url = models.CharField(max_length=1024, verbose_name="Request url",
                           db_index=True, null=True, blank=True)
    status_code = models.SmallIntegerField(verbose_name="Status code", db_index=True, null=True, blank=True)
    content_length = models.IntegerField(verbose_name="Content length", null=True)
    user_agent = models.CharField(max_length=1024, null=True)
    ip = models.GenericIPAddressField(db_index=True, null=True, blank=True)
    name = models.CharField(max_length=256, null=True)

    entries = PickledObjectField(default=[])

    class Meta(object):
        ordering = ['-start_date']

    @property
    def milliseconds(self):
        return self.duration * 1000

    @property
    def formatted_start_date(self):
        return self.start_date.strftime('%Y-%m-%d %H:%M:%S') + '.' + \
            self.start_date.strftime('%f')[:3]

    @property
    def can_be_expanded(self):
        for entry in self.entries:
            if entry.stack_trace or entry.is_long_message:
                return True
        return False

    @property
    def entries_html(self):
        result = []
        for entity in self.entries:
            result.append(str(entity))

        return linebreaksbr("\n\n".join(result))